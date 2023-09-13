from typing import Optional

import phpserialize

from .UserManager import User, UserWithInactivityPolicy, UserManagerWithTimestamps
from .AdminManager import Admin, AdminManager
from .RequiresAdmin import RequiresAdmin


INACTIVE_CRAT_TIME = 6  # https://www.wikidata.org/wiki/Wikidata:Bureaucrats
INACTIVE_CRAT_ACTIONS = 10  # including crat actions and property creations


class Bureaucrat(UserWithInactivityPolicy, RequiresAdmin):
    level:str = 'bureaucrat'
    log_types:list[str] = Admin.log_types

    def __init__(self, username:str, start_ts:int, warn_ts:int, admin:Optional[User]) -> None:
        UserWithInactivityPolicy.__init__(self, username, start_ts, warn_ts)
        RequiresAdmin.__init__(self, admin)

        self.admin_actions = self.count_logged_actions(self.start_ts, Bureaucrat.log_types)
        self.admin_actions_warn = self.count_logged_actions(self.warn_ts, Bureaucrat.log_types)

        self.count_bureaucrat_actions()

    def count_bureaucrat_actions(self) -> None:
        self.bureaucrat_actions = 0

        # https://www.wikidata.org/wiki/Special:ListGroupRights
        add_rights = [ 'accountcreator', 'bot', 'bureaucrat', 'confirmed', 'flood', 'interface-admin', 'sysop', 'translationadmin', 'wikidata-staff' ]
        remove_rights = [ 'accountcreator', 'bot', 'confirmed', 'flood', 'interface-admin', 'translationadmin', 'wikidata-staff' ]

        for dct in self.get_rights_actions(self.start_ts):
            params = dct.get('log_params', '')

            try:
                params_loaded = phpserialize.loads(params)
            except ValueError:
                continue  # old log_params format; there are no such cases

            # log_param is serialized php string with wrong format
            if b'4::oldgroups' not in params_loaded:
                continue
            if b'5::newgroups' not in params_loaded:
                continue

            oldgroups = [ right.decode('utf8') for right in params_loaded[b'4::oldgroups'].values() ]
            newgroups = [ right.decode('utf8') for right in params_loaded[b'5::newgroups'].values() ]

            for add_right in add_rights:
                if add_right not in oldgroups and add_right in newgroups:
                    self.bureaucrat_actions += 1

            for remove_right in remove_rights:
                if remove_right in oldgroups and remove_right not in newgroups:
                    self.bureaucrat_actions += 1

    @property
    def is_inactive(self) -> bool:
        if (self.latest_promotion_timestamp or 0) > self.start_ts:
            return False

        return (self.admin_actions < INACTIVE_CRAT_ACTIONS) or self.admin_inactivity

    @property
    def is_slipping_into_inactivity(self) -> bool:
        if (self.latest_promotion_timestamp or 0) > self.warn_ts:
            return False

        return (self.admin_actions_warn < INACTIVE_CRAT_ACTIONS) or self.admin_inacticity_warn

    @property
    def total_action_string(self) -> str:
        actions = ''
        if self.admin_actions > 0:
            actions += f'{self.admin_actions} action'
            if self.admin_actions > 1:
                actions += 's'
        
        return actions

    @property
    def admin_inactivity_class(self) -> str:
# not_admin: background-color:#DFD;
# inactive: background-color:#BBB;
# slipping: background-color:#FDD;

        if not self.is_admin:
            return ' style="not_admin"'
        
        if self.admin_inactivity:
            return ' class="inactive"'

        if self.admin_inacticity_warn:
            return ' class="slipping"'

        return ''

    @property
    def is_admin_string(self) -> str:
        yesno = { True : 'yes', False : 'no' }
        return yesno.get(self.is_admin, 'unknown')

    def report_table_row(self) -> str:
        report_table_wikitext_rows = [ '|-' ]

        report_table_wikitext_rows.append(f'| {{{{User|{self.username}}}}}')
        report_table_wikitext_rows.append(f'|{self.promotion_class} data-sort-value="{self.latest_promotion_timestamp}" | {self.latest_promotion_string}')
        report_table_wikitext_rows.append(f'| data_sort_value="{self.bureaucrat_actions}" | {self.bureaucrat_actions}')
        report_table_wikitext_rows.append(f'|{self.inactivity_class} data-sort-value="{self.admin_actions}" | {self.total_action_string}')
        report_table_wikitext_rows.append(f'|{self.admin_inactivity_class} data-sort-value="{self.is_admin}" | {self.is_admin_string}')

        return '\n'.join(report_table_wikitext_rows)


class BureaucratManager(UserManagerWithTimestamps):
    user_class = Bureaucrat
    report_column_headers:list[str] = [
        'bureaucrat',
        'promoted to bureaucrat',
        f'logged bureaucrat actions<br>(past {INACTIVE_CRAT_TIME} months)',
        f'logged admin+bureaucrat actions<br>(past {INACTIVE_CRAT_TIME} months)',
        'is admin'
    ]
    report_subpage = 'Bureaucrat'
    report_template = 'bureaucrat.template'

    def __init__(self, admin_manager:AdminManager) -> None:
        self.admin_manager = admin_manager
        super().__init__(INACTIVE_CRAT_TIME)

    def populate_user_data(self) -> None:
        self.user_data = {}
        for username in self.__class__.query_users(self.__class__.user_class.level):
            self.user_data[username] = self.__class__.user_class(
                username,
                self.start_ts,
                self.warn_ts,
                self.admin_manager.user_data.get(username)
            )
