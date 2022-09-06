from .UserManager import UserWithoutInactivityPolicy, UserManager


# https://www.wikidata.org/wiki/Wikidata:Rollbackers


class Rollbacker(UserWithoutInactivityPolicy):
    level:str = 'rollbacker'


class RollbackerManager(UserManager):
    user_class = Rollbacker
    report_column_headers:list[str] = [
        'rollbacker',
        'promoted to rollbacker',
        'edit count',
        'last edit'
    ]
    report_subpage = 'Rollbacker'
    report_template = 'rollbacker.template'
