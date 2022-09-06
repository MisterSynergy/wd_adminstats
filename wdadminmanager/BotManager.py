from .UserManager import UserWithoutInactivityPolicy, UserManager


# https://www.wikidata.org/wiki/Wikidata:Bots


class Bot(UserWithoutInactivityPolicy):
    level:str = 'bot'


class BotManager(UserManager):
    user_class = Bot
    report_column_headers:list[str] = [
        'bot',
        'promoted to bot',
        'edit count',
        'last edit'
    ]
    report_subpage = 'Bot'
    report_template = 'bot.template'
