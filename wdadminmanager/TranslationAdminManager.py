from .UserManager import UserWithInactivityPolicy, UserManagerWithTimestamps


# https://www.wikidata.org/wiki/Wikidata:Translation_administrators
INACTIVE_TRANSLATIONADMIN_TIME = 6  # informal
INACTIVE_TRANSLATIONADMIN_ACTIONS = 1


class TranslationAdmin(UserWithInactivityPolicy):
    level:str = 'translationadmin'
    log_types:list[str] = [ # https://www.wikidata.org/wiki/Special:ListGroupRights
        'pagelang',
        'pagetranslation'
    ]

    def __init__(self, username:str, start_ts:int, warn_ts:int) -> None:
        super().__init__(username, start_ts, warn_ts)

        self.translationadmin_actions = self.count_logged_actions(self.start_ts, TranslationAdmin.log_types)
        self.translationadmin_actions_warn = self.count_logged_actions(self.warn_ts, TranslationAdmin.log_types)

    @property
    def is_inactive(self) -> bool:
        if (self.latest_promotion_timestamp or 0) > self.start_ts:
            return False

        return self.translationadmin_actions < INACTIVE_TRANSLATIONADMIN_ACTIONS

    @property
    def is_slipping_into_inactivity(self) -> bool:
        if (self.latest_promotion_timestamp or 0) > self.warn_ts:
            return False

        return self.translationadmin_actions_warn < INACTIVE_TRANSLATIONADMIN_ACTIONS

    def report_table_row(self) -> str:
        report_table_wikitext_rows = [ '|-' ]
        
        report_table_wikitext_rows.append(f'| {{{{User|{self.username}}}}}')
        report_table_wikitext_rows.append(f'|{self.promotion_class} data-sort-value="{self.latest_promotion_timestamp}" | {self.latest_promotion_string}')
        report_table_wikitext_rows.append(f'|{self.inactivity_class} data-sort-value="{self.translationadmin_actions}" | {self.translationadmin_actions}')
        report_table_wikitext_rows.append(f'| data-sort-value="{self.last_edit_activity}" | {self.last_edit_date}')

        return '\n'.join(report_table_wikitext_rows)


class TranslationAdminManager(UserManagerWithTimestamps):
    user_class = TranslationAdmin
    report_column_headers:list[str] = [
        'translation admin',
        'promoted to translation admin',
        f'translation admin actions<br>(past {INACTIVE_TRANSLATIONADMIN_TIME} months)',
        'last edit'
    ]
    report_subpage = 'Translation administrator'
    report_template = 'translationadmin.template'

    def __init__(self):
        super().__init__(INACTIVE_TRANSLATIONADMIN_TIME)
