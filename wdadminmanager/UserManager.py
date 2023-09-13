from abc import abstractmethod
from datetime import datetime
from time import gmtime, strftime
from typing import Optional, Type, ValuesView

import phpserialize
import requests

from .Replica import Replica

class User:
    level:str
    former_levels:list[str] = []

    def __init__(self, username:str) -> None:
        self.username = username
        self.query_last_edit_activity()
        self.query_last_logged_activity()
        self.query_editcount()

    @property
    def username_underscore(self) -> str:
        return self.username.replace(' ', '_')

    @property
    def username_underscore_escaped(self) -> str:
        return self.username_underscore.replace("'", "''")

    @property
    def username_escaped(self) -> str:
        return self.username.replace("'", "''")

    @property
    def last_edit_date(self) -> str:
        if self.last_edit_activity == 0:
            return 'None'

        s = str(self.last_edit_activity)
        return f'{s[0:4]}-{s[4:6]}-{s[6:8]}'

    @property
    def last_activity(self) -> int:
        return max(self.last_edit_activity, self.last_logged_activity)

    def get_previous_username(self) -> Optional[str]:
        query = f"""SELECT
          log_params
        FROM
          logging
        WHERE
          log_type='gblrename'
          AND log_action='rename'
          AND log_title='CentralAuth/{self.username_underscore_escaped}'"""

        result = Replica.query(query, 'metawiki')
        for tpl in result:
            try:
                params = phpserialize.loads(tpl[0])
            except ValueError as exception:  # old log_params format, to be ignored
                continue

            previous_username = params[b'4::olduser'].decode('utf8')
            current_username = params[b'5::newuser'].decode('utf8')
            
            if current_username == self.username_underscore:
                return previous_username

        return None

    def query_editcount(self) -> None:
        query = f"""SELECT
          user_editcount
        FROM
          user
        WHERE
          user_name='{self.username_escaped}'"""

        result = Replica.query(query)

        if len(result) == 0:
            self.editcount = 0
        else:
            self.editcount = result[0][0]

    def count_logged_actions(self, earliest_timestamp:int, log_types:list[str]) -> int:
        log_types_concatenated = "', '".join(log_types)

        query = f"""SELECT
          COUNT(log_id) AS cnt
        FROM
          logging_userindex
            JOIN actor_logging ON log_actor=actor_id
        WHERE
          actor_name='{self.username_escaped}'
          AND log_timestamp>={earliest_timestamp}
          AND log_type IN ('{log_types_concatenated}')"""

        result = Replica.query(query)

        return result[0][0]

    def count_property_creations(self, earliest_timestamp:int) -> int:
        query = f"""SELECT
          COUNT(*) AS cnt
        FROM
          page
            JOIN revision_userindex ON page_id=rev_page
            JOIN actor_revision ON rev_actor=actor_id
        WHERE
          rev_parent_id=0
          AND rev_timestamp>={earliest_timestamp}
          AND page_namespace=120
          AND actor_name='{self.username_escaped}'"""

        result = Replica.query(query)

        return result[0][0]

    def get_rights_actions(self, earliest_timestamp:int) -> list[tuple]:
        query = f"""SELECT
          log_params
        FROM
          logging_userindex
            JOIN actor_logging ON log_actor=actor_id
        WHERE
          actor_name='{self.username_escaped}'
          AND log_timestamp>={earliest_timestamp}
          AND log_type='rights'"""

        result = Replica.query(query)

        return result

    def count_mediawiki_namespace_edits(self, earliest_timestamp:int) -> int:
        query = f"""SELECT
          COUNT(rev_id)
        FROM
          revision_userindex
            JOIN actor_revision ON rev_actor=actor_id
            JOIN page ON rev_page=page_id
        WHERE
          actor_name='{self.username_escaped}'
          AND rev_timestamp>={earliest_timestamp}
          AND page_namespace=8
          AND page_content_model NOT IN ('css', 'sanitized-css', 'javascript', 'json')"""

        result = Replica.query(query)

        return result[0][0]

    def count_jscss_edits(self, earliest_timestamp:int) -> int:
        edit_count = 0
        
        for tpl in self._query_jscss_edits(earliest_timestamp):
            page_title = tpl[0].decode('utf8')
            page_namespace = tpl[1]
            #page_content_model = tpl[2]

            if page_namespace in [ 2, 3 ] and page_title.startswith(self.username_underscore):
                continue

            edit_count += 1
        
        return edit_count

    def _query_jscss_edits(self, earliest_timestamp:int) -> list[tuple]:
        query = f"""SELECT
          page_title,
          page_namespace,
          page_content_model
        FROM
          revision_userindex
            JOIN actor_revision ON rev_actor=actor_id
            JOIN page ON rev_page=page_id
        WHERE
          actor_name='{self.username_escaped}'
          AND rev_timestamp>={earliest_timestamp}
          AND page_content_model IN ('css', 'sanitized-css', 'javascript', 'json')"""

        result = Replica.query(query)

        return result

    def query_last_logged_activity(self) -> None:
        response = requests.get(
            url='https://www.wikidata.org/w/api.php',
            params={
                'action' : 'query',
                'format' : 'json',
                'list' : 'logevents',
                'leprop' : 'timestamp',
                'leuser' : f'{self.username}',
                'lelimit' : '1'
            },
            headers={
                'User-Agent' : f'{requests.utils.default_headers()["User-Agent"]} (Wikidata bot' \
                                ' by User:MisterSynergy; mailto:mister.synergy@yahoo.com)'
            }
        )
        payload = response.json()

        logevents = payload.get('query', {}).get('logevents', [])
        if len(logevents) == 0:
            self.last_logged_activity = 0
            return

        timestamp_str = logevents[0].get('timestamp', '')
        if timestamp_str == '':
            self.last_logged_activity = 0
            return

        self.last_logged_activity = int(datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%SZ').strftime('%Y%m%d%H%M%S'))

    def query_last_edit_activity(self) -> None:
        query = f"""SELECT 
          rev_timestamp
        FROM
          revision_userindex
            JOIN actor_revision ON rev_actor=actor_id
        WHERE
          actor_name='{self.username_escaped}'
        ORDER BY
          rev_timestamp DESC
        LIMIT
          1"""

        result = Replica.query(query)

        if len(result) == 0:
            self.last_edit_activity = 0
        else:
            self.last_edit_activity = int(result[0][0])

    def report_table_row(self) -> str:
        report_table_wikitext_rows = [ '|-' ]

        report_table_wikitext_rows.append(f'| {{{{User|{self.username}}}}}')
        report_table_wikitext_rows.append(f'| data-sort-value="{self.last_edit_activity}" | {self.last_edit_date}')

        return '\n'.join(report_table_wikitext_rows)


class UserWithElevatedRights(User):
    system_accounts = [ 'Abuse filter', 'Maintenance script', 'MediaWiki default', 'MediaWiki message delivery' ]  # system accounts that do not have a promotion date
    
    def __init__(self, username:str, level:Optional[str]=None) -> None:
        super().__init__(username)
        if level is not None:  # optionally overwrite the class attribute with an instance attribute
            self.level = level
        self.init_promotion_timestamps()

    @property
    def latest_promotion_timestamp(self) -> Optional[int]:
        if len(self.promotion_timestamps) == 0:
            return None

        return max(self.promotion_timestamps)

    @property
    def latest_promotion_string(self) -> str:
        if self.latest_promotion_timestamp is None:
            return 'unknown'

        s = str(self.latest_promotion_timestamp)
        return f'{s[0:4]}-{s[4:6]}-{s[6:8]}'

    def init_promotion_timestamps(self) -> None:
        self.promotion_timestamps:list[int] = []

        if self.username in self.system_accounts:
            return

        bytes_level = bytes(self.level, 'utf8')

        try:
            rights_changes_wikidata = self._query_rights_changes()
            rights_changes_metawiki = self._query_rights_changes('metawiki')
        except RuntimeError as exception:
            return

        for tpl in rights_changes_wikidata + rights_changes_metawiki:
            timestamp = int(tpl[0].decode('utf8'))
            params = tpl[1]

            try:
                params_loaded = phpserialize.loads(params)
            except ValueError:
                continue  # old log_params format; there are no such cases

            if b'4::oldgroups' not in params_loaded or b'5::newgroups' not in params_loaded: # log_param is serialized php string with wrong format
                continue

            if bytes_level not in params_loaded[b'4::oldgroups'].values() and bytes_level in params_loaded[b'5::newgroups'].values():
                self.promotion_timestamps.append(timestamp)

        if len(self.former_levels) > 0:
            for former_level in self.former_levels:
                previous_level_user = UserWithElevatedRights(self.username, level=former_level)
                self.promotion_timestamps += previous_level_user.promotion_timestamps

        previous_username = self.get_previous_username()
        if previous_username is not None:
            previous_user = UserWithElevatedRights(previous_username, level=self.level)
            self.promotion_timestamps += previous_user.promotion_timestamps

            if len(self.former_levels) > 0:
                for former_level in self.former_levels:
                    previous_level_user = UserWithElevatedRights(previous_username, level=former_level)
                    self.promotion_timestamps += previous_level_user.promotion_timestamps

    def _query_rights_changes(self, database:str='wikidatawiki') -> list[tuple]:
        if database=='wikidatawiki':
            log_title = self.username_underscore_escaped
        else:  # this is important since some logs are located in metawiki
            log_title = f'{self.username_underscore_escaped}@wikidatawiki'

        query = f"""SELECT
          log_timestamp,
          log_params
        FROM
          logging
        WHERE
          log_type='rights'
          AND log_title='{log_title}'"""

        result = Replica.query(query, database)

        return result

    def report_table_row(self) -> str:
        report_table_wikitext_rows = [ '|-' ]

        report_table_wikitext_rows.append(f'| {{{{User|{self.username}}}}}')
        report_table_wikitext_rows.append(f'| data-sort-value="{self.latest_promotion_timestamp}" | {self.latest_promotion_string}')
        report_table_wikitext_rows.append(f'| data-sort-value="{self.last_edit_activity}" | {self.last_edit_date}')

        return '\n'.join(report_table_wikitext_rows)


class UserWithInactivityPolicy(UserWithElevatedRights):
    def __init__(self, username:str, start_ts:int, warn_ts:int) -> None:
        super().__init__(username)

        self.start_ts = start_ts
        self.warn_ts = warn_ts

# inactive: background-color:#BBB;
# slipping: background-color:#FDD;

    @property
    @abstractmethod
    def is_inactive(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_slipping_into_inactivity(self) -> bool:
        pass

    @property
    def inactivity_class(self) -> str:
        if self.is_inactive:
            return ' class="inactive"'

        if self.is_slipping_into_inactivity:
            return ' class="slipping"'

        return ''

# freshly_promoted: background-color:#DFD;
    @property
    def promotion_class(self) -> str:
        if (self.latest_promotion_timestamp or 0) > self.start_ts:
            return ' class="freshly_promoted"'

        return ''


class UserWithoutInactivityPolicy(UserWithElevatedRights):
    def report_table_row(self) -> str:
        report_table_wikitext_rows = [ '|-' ]

        report_table_wikitext_rows.append(f'| {{{{User|{self.username}}}}}')
        report_table_wikitext_rows.append(f'| data-sort-value="{self.latest_promotion_timestamp}" | {self.latest_promotion_string}')
        report_table_wikitext_rows.append(f'| data-sort-value="{self.editcount}" | {self.editcount}')
        report_table_wikitext_rows.append(f'| data-sort-value="{self.last_edit_activity}" | {self.last_edit_date}')

        return '\n'.join(report_table_wikitext_rows)


class UserManager:
    report_column_headers:list[str]
    user_class:Type[User]
    report_template:str
    report_subpage:str

    def __init__(self) -> None:
        self.populate_user_data()
        self.make_user_table(
            self.__class__.report_column_headers,
            self.user_data.values()
        )

    @staticmethod
    def query_users(group:str) -> list[str]:
        query = f"""SELECT
          user_name
        FROM
          user
            LEFT JOIN user_groups ON user_id=ug_user
        WHERE
          ug_group='{group}'
        ORDER BY
          user_name ASC"""

        result = Replica.query(query)

        return [ row[0].decode('utf8') for row in result ]

    def populate_user_data(self) -> None:
        self.user_data = {}
        for username in self.__class__.query_users(self.__class__.user_class.level):
            self.user_data[username] = self.__class__.user_class(username)

    def make_user_table(self, column_headers:list[str], users:ValuesView[User]) -> None:
        self.report_table  = '{| class="wikitable sortable MisterSynergy-activity"\n'
        self.report_table += '|-\n'
        self.report_table += f'! {" !! ".join(column_headers)}\n'
        for user in users:
            self.report_table += user.report_table_row()
            self.report_table += '\n'
        self.report_table += '|}'

    def print_user_table(self) -> None:
        print(self.report_table)

    def get_report_page(self, t_start:float) -> str:
        timestamp = str(int(t_start))
        timestamp_formatted = strftime('%Y-%m-%d, %H:%M:%S (UTC)', gmtime(t_start))
        
        with open(f'./templates/{self.__class__.report_template}', mode='r', encoding='utf8') as file_handle:
            template = file_handle.read()

        body = template.format(
            timestamp=timestamp,
            timestamp_formatted=timestamp_formatted,
            report_table=self.report_table,
            group=self.__class__.user_class.level
        )

        return body

class UserManagerWithTimestamps(UserManager):
    user_class:Type[UserWithInactivityPolicy]
    
    def __init__(self, timeframe:int) -> None:
        self.start_ts, self.warn_ts = UserManagerWithTimestamps.get_timestamps(timeframe)
        super().__init__()

    def populate_user_data(self) -> None:
        self.user_data = {}
        for username in self.__class__.query_users(self.__class__.user_class.level):
            self.user_data[username] = self.__class__.user_class(username, self.start_ts, self.warn_ts)

    @staticmethod
    def get_timestamps(timeframe:int) -> tuple[int, int]:
        start_month = int(strftime('%m')) - timeframe
        start_year = int(strftime('%Y'))

        if start_month<1:
            start_month += 12
            start_year -= 1

        start_month_warn = start_month+1  # this is one month less than the inactivity timeframe
        start_year_warn = start_year

        if start_month_warn>12:
            start_month_warn -= 12
            start_year_warn += 1

        start_timestamp = int(f'{start_year:4d}{start_month:02d}{strftime("%d%H%M%S")}')
        start_timestamp_warn = int(f'{start_year_warn:4d}{start_month_warn:02d}{strftime("%d%H%M%S")}')

        return start_timestamp, start_timestamp_warn
