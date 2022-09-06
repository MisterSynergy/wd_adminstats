from .UserManager import UserWithInactivityPolicy, UserManagerWithTimestamps


INACTIVE_ADMIN_TIME = 6  # https://www.wikidata.org/wiki/Wikidata:Administrators
INACTIVE_ADMIN_ACTIONS = 5  # including crat actions and property creations


class Admin(UserWithInactivityPolicy):
    level:str = 'sysop'
    log_types:list[str] = [ # https://www.wikidata.org/wiki/Special:ListGroupRights
        'abusefilter',
        'block',
        'contentmodel',
        'delete',
        'import',
        'managetags',
        'merge',
        'protect',
        'rights'
    ]

    def __init__(self, username:str, start_ts:int, warn_ts:int) -> None:
        super().__init__(username, start_ts, warn_ts)

        self.actions = self.count_logged_actions(self.start_ts, Admin.log_types)
        self.actions_warn = self.count_logged_actions(self.warn_ts, Admin.log_types)

        self.property_creations = self.count_property_creations(self.start_ts)
        self.property_creations_warn = self.count_property_creations(self.warn_ts)

    @property
    def is_inactive(self) -> bool:
        if (self.latest_promotion_timestamp or 0) > self.start_ts:
            return False

        return (self.actions + self.property_creations < INACTIVE_ADMIN_ACTIONS)

    @property
    def is_slipping_into_inactivity(self) -> bool:
        if (self.latest_promotion_timestamp or 0) > self.warn_ts:
            return False

        return (self.actions_warn + self.property_creations_warn < INACTIVE_ADMIN_ACTIONS)

    @property
    def total_action_string(self) -> str:
        actions = ''
        if self.actions > 0:
            actions += f'{self.actions} action'
            if self.actions > 1:
                actions += 's'
            if self.property_creations > 0:
                actions += ', '
        if self.property_creations > 0:
            actions += f'{self.property_creations} property creation'
            if self.property_creations > 1:
                actions += 's'
        
        return actions

    def report_table_row(self) -> str:
        report_table_wikitext_rows = [ '|-' ]

        report_table_wikitext_rows.append(f'| {{{{User|{self.username}}}}}')
        report_table_wikitext_rows.append(f'|{self.promotion_class} data-sort-value="{self.latest_promotion_timestamp}" | {self.latest_promotion_string}')
        report_table_wikitext_rows.append(f'|{self.inactivity_class} data-sort-value="{self.actions + self.property_creations}" | {self.total_action_string}')

        return '\n'.join(report_table_wikitext_rows)


class AdminManager(UserManagerWithTimestamps):
    report_column_headers:list[str] = [
        'admin',
        'promoted to admin',
        f'logged actions<br>(past {INACTIVE_ADMIN_TIME} months)'
    ]
    user_class = Admin
    report_subpage = 'Administrator'
    report_template = 'sysop.template'

    def __init__(self) -> None:
        super().__init__(INACTIVE_ADMIN_TIME)
