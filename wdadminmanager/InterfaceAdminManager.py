from .UserManager import UserWithInactivityPolicy, UserManagerWithTimestamps


# https://www.wikidata.org/wiki/Wikidata:Interface_administrators
INACTIVE_UIADMIN_TIME_ANY = 6  # months
INACTIVE_UIADMIN_TIME = 12  # months
INACTIVE_UIADMIN_ACTIONS = 1  # int


class InterfaceAdmin(UserWithInactivityPolicy):
    level:str = 'interface-admin'

    def __init__(self, username:str, start_ts:int, warn_ts:int, start_ts_any:int, warn_ts_any:int) -> None:
        super().__init__(username, start_ts, warn_ts)

        self.start_ts_any = start_ts_any
        self.warn_ts_any = warn_ts_any

        self.mediawiki_actions = self.count_mediawiki_namespace_edits(self.start_ts)
        self.mediawiki_actions_warn = self.count_mediawiki_namespace_edits(self.warn_ts)

        self.jscss_actions = self.count_jscss_edits(self.start_ts)
        self.jscss_actions_warn = self.count_jscss_edits(self.warn_ts)

    @property
    def interfaceadmin_actions(self) -> int:
        return self.mediawiki_actions + self.jscss_actions

    @property
    def interfaceadmin_actions_warn(self) -> int:
        return self.mediawiki_actions_warn + self.jscss_actions_warn

    @property
    def is_generally_inactive(self) -> bool:
        return self.last_activity < self.start_ts_any

    @property
    def is_slipping_into_general_inactivity(self) -> bool:
        return self.last_activity < self.warn_ts_any

    @property
    def is_ia_inactive(self) -> bool:
        return self.interfaceadmin_actions < INACTIVE_UIADMIN_ACTIONS

    @property
    def is_slipping_into_ia_inactivity(self) -> bool:
        return self.interfaceadmin_actions_warn < INACTIVE_UIADMIN_ACTIONS

    @property
    def ia_inactivity_class(self) -> str:
# inactive: background-color:#BBB;
# slipping: background-color:#FDD;
        if self.is_ia_inactive:
            return ' class="inactive"'

        if self.is_slipping_into_ia_inactivity:
            return ' class="slipping"'
        
        return ''

    @property
    def general_inactivity_string(self) -> str:
        yesno = { True : 'no', False : 'yes' } # counterintuitive, but hey...
        return yesno.get(self.is_generally_inactive, 'unknown')

    @property
    def general_inactivity_class(self) -> str:
        if self.is_generally_inactive:
            return ' class="inactive"'

        if self.is_slipping_into_general_inactivity:
            return ' class="slipping"'

        return ''

    def report_table_row(self) -> str:
        report_table_wikitext_rows = [ '|-' ]

        report_table_wikitext_rows.append(f'| {{{{User|{self.username}}}}}')
        report_table_wikitext_rows.append(f'|{self.promotion_class} data-sort-value="{self.latest_promotion_timestamp}" | {self.latest_promotion_string}')
        report_table_wikitext_rows.append(f'|{self.ia_inactivity_class} data-sort-value="{self.interfaceadmin_actions}" | {self.interfaceadmin_actions}')
        report_table_wikitext_rows.append(f'|{self.general_inactivity_class} data-sort-value="{self.last_activity}" | {self.general_inactivity_string}')

        return '\n'.join(report_table_wikitext_rows)


class InterfaceAdminManager(UserManagerWithTimestamps):
    user_class = InterfaceAdmin
    report_column_headers:list[str] = [
        'interface admin',
        'promoted to interface admin',
        f'interface admin actions<br>(past {INACTIVE_UIADMIN_TIME} months)',
        f'any activity<br>(past {INACTIVE_UIADMIN_TIME_ANY} months)'
    ]
    report_subpage = 'Interface administrator'
    report_template = 'interface-admin.template'

    def __init__(self) -> None:
        self.start_ts_any, self.warn_ts_any = UserManagerWithTimestamps.get_timestamps(INACTIVE_UIADMIN_TIME_ANY)
        super().__init__(INACTIVE_UIADMIN_TIME)

    def populate_user_data(self) -> None:
        self.user_data = {}
        for username in self.__class__.query_users(self.__class__.user_class.level):
            self.user_data[username] = self.__class__.user_class(
                username,
                self.start_ts,
                self.warn_ts,
                self.start_ts_any,
                self.warn_ts_any
            )
