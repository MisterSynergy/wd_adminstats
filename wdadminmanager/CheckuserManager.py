from .UserManager import UserWithElevatedRights, UserManager


# https://www.wikidata.org/wiki/Wikidata:CheckUser


class Checkuser(UserWithElevatedRights):
    level:str = 'checkuser'


class CheckuserManager(UserManager):
    user_class = Checkuser
    report_column_headers:list[str] = [
        'checkuser',
        'promoted to checkuser',
        'last edit'
    ]
    report_subpage = 'CheckUser'
    report_template = 'checkuser.template'
