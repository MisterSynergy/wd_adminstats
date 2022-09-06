from typing import Optional

from .UserManager import User, UserWithElevatedRights, UserManager
from .AdminManager import Admin, AdminManager
from .RequiresAdmin import RequiresAdmin

# https://www.wikidata.org/wiki/Wikidata:Oversight
# requires sysop


class Oversighter(UserWithElevatedRights, RequiresAdmin):
    level:str = 'suppress'
    former_levels:list[str] = [ 'oversight' ]

    def __init__(self, username:str, admin:Optional[User]) -> None:
        UserWithElevatedRights.__init__(self, username)
        RequiresAdmin.__init__(self, admin)

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
        
        if self.is_inactive_admin:
            inactivity_css = ' style="background-color:#BBB;"'
        elif self.is_slipping_into_admin_inactivity:
            inactivity_css = ' style="background-color:#FDD;"'
        else:
            inactivity_css = ''

        yesno = { True : 'yes', False : 'no' }

        report_table_wikitext_rows.append(f'| {{{{User|{self.username}}}}}')
        report_table_wikitext_rows.append(f'| data-sort-value="{self.latest_promotion_timestamp}" | {self.latest_promotion_string}')
        report_table_wikitext_rows.append(f'|{self.admin_inactivity_class} data-sort-value="{self.is_admin}" | {self.is_admin_string}')

        return '\n'.join(report_table_wikitext_rows)


class OversighterManager(UserManager):
    user_class = Oversighter
    report_column_headers:list[str] = [
        'oversighter',
        'promoted to oversighter',
        'is admin'
    ]
    report_subpage = 'Oversighter'
    report_template = 'oversight.template'

    def __init__(self, admin_manager:AdminManager) -> None:
        self.admin_manager = admin_manager
        super().__init__()

    def populate_user_data(self) -> None:
        self.user_data = {}
        for username in self.__class__.query_users(self.__class__.user_class.level):
            self.user_data[username] = self.__class__.user_class(
                username,
                self.admin_manager.user_data.get(username)
            )
