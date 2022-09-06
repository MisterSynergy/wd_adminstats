from .UserManager import UserWithoutInactivityPolicy, UserManager


# https://www.wikidata.org/wiki/Wikidata:Confirmed_users


class ConfirmedUser(UserWithoutInactivityPolicy):
    level:str = 'confirmed'


class ConfirmedUserManager(UserManager):
    user_class = ConfirmedUser
    report_column_headers:list[str] = [
        'confirmed user',
        'promoted to confirmed',
        'edit count',
        'last edit'
    ]
    report_subpage = 'Confirmed user'
    report_template = 'confirmed.template'
