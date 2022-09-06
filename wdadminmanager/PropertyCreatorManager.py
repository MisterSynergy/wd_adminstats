from .UserManager import UserWithInactivityPolicy, UserManagerWithTimestamps


# https://www.wikidata.org/wiki/Wikidata:Property_creators
INACTIVE_PROPERTY_CREATOR_TIME = 6  # months
INACTIVE_PROPERTY_CREATOR_ACTIONS = 1


class PropertyCreator(UserWithInactivityPolicy):
    level:str = 'propertycreator'

    def __init__(self, username:str, start_ts:int, warn_ts:int):
        super().__init__(username, start_ts, warn_ts)

        self.property_creations = self.count_property_creations(self.start_ts)
        self.property_creations_warn = self.count_property_creations(self.warn_ts)

    @property
    def is_inactive(self) -> bool:
        if (self.latest_promotion_timestamp or 0) > self.start_ts:
            return False

        return self.property_creations < INACTIVE_PROPERTY_CREATOR_ACTIONS

    @property
    def is_slipping_into_inactivity(self) -> bool:
        if (self.latest_promotion_timestamp or 0) > self.warn_ts:
            return False

        return self.property_creations_warn < INACTIVE_PROPERTY_CREATOR_ACTIONS

    def report_table_row(self) -> str: # TODO: maybe issue warnings with CSS if self.property_creations_warn==0
        report_table_wikitext_rows = [ '|-' ]

        report_table_wikitext_rows.append(f'| {{{{User|{self.username}}}}}')
        report_table_wikitext_rows.append(f'|{self.promotion_class} data-sort-value="{self.latest_promotion_timestamp}" | {self.latest_promotion_string}')
        report_table_wikitext_rows.append(f'|{self.inactivity_class} data-sort-value="{self.property_creations} | {self.property_creations}')
        report_table_wikitext_rows.append(f'| data-sort-value="{self.last_edit_activity}" | {self.last_edit_date}')

        return '\n'.join(report_table_wikitext_rows)


class PropertyCreatorManager(UserManagerWithTimestamps):
    user_class = PropertyCreator
    report_column_headers:list[str] = [
        'property creator',
        'promoted to property creator',
        f'property creations<br>(past {INACTIVE_PROPERTY_CREATOR_TIME} months)',
        'last edit'
    ]
    report_subpage = 'Property creator'
    report_template = 'propertycreator.template'

    def __init__(self):
        super().__init__(INACTIVE_PROPERTY_CREATOR_TIME)
