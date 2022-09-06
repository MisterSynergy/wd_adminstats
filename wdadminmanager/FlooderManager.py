from .UserManager import UserWithoutInactivityPolicy, UserManager


# https://www.wikidata.org/wiki/Wikidata:Flooders


class Flooder(UserWithoutInactivityPolicy):
    level:str = 'flood'


class FlooderManager(UserManager):
    user_class = Flooder
    report_column_headers:list[str] = [
        'flooder',
        'promoted to flooder',
        'edit count',
        'last edit'
    ]
    report_subpage = 'Flooder'
    report_template = 'flood.template'
