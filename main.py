from time import time

import pywikibot as pwb

from wdadminmanager import UserManager, AdminManager, BureaucratManager, OversighterManager, \
    CheckuserManager, InterfaceAdminManager, TranslationAdminManager, PropertyCreatorManager, \
    BotManager, FlooderManager, IPBlockExemptUserManager, RollbackerManager, ConfirmedUserManager



BASEPAGE = 'User:MisterSynergy/activity'
EDIT_SUMMARY = 'update user activity tables #msynbot #unapproved'
SAVE_TO_WIKIPAGE = True
SAVE_TO_LOGFILE = True

SITE = pwb.Site('wikidata', 'wikidata')
SITE.login()


def save_to_wikipage(page_title:str, edit_summary:str, body:str) -> None:
    if SAVE_TO_WIKIPAGE is not True:
        return

    page = pwb.Page(SITE, page_title)
    page.text = body
    page.save(
        summary=edit_summary,
        watch='nochange',
        minor=True,
        quiet=True
    )


def save_to_logfile(page_title:str, body:str) -> None:
    if SAVE_TO_LOGFILE is not True:
        return

    filename = f'{page_title}.txt'.replace('/', '_').replace(' ', '_').replace(':', '_')
    with open(f'./logs/{filename}', mode='w', encoding='utf8') as file_handle:
        file_handle.write(body)
        print(filename)


def save_report(page_title:str, edit_summary:str, body:str) -> None:
    if SAVE_TO_WIKIPAGE is True:
        save_to_wikipage(page_title, EDIT_SUMMARY, body)

    if SAVE_TO_LOGFILE is True:
        save_to_logfile(page_title, body)


def main() -> None:
    t_start = time()

    admin_manager = AdminManager()
    bureaucrat_manager = BureaucratManager(admin_manager)
    oversighter_manager = OversighterManager(admin_manager)
    checkuser_manager = CheckuserManager()#

    interfaceadmin_manager = InterfaceAdminManager()
    translationadmin_manager = TranslationAdminManager()
    propertycreator_manager = PropertyCreatorManager()

    bot_manager = BotManager()
    flooder_manager = FlooderManager()

    ipblockexemptuser_manager = IPBlockExemptUserManager()
    rollbacker_manager = RollbackerManager()
    confirmeduser_manager = ConfirmedUserManager()

    managers = [
        admin_manager,
        bureaucrat_manager,
        oversighter_manager,
        checkuser_manager,
        interfaceadmin_manager,
        translationadmin_manager,
        propertycreator_manager,
        bot_manager,
        flooder_manager,
        ipblockexemptuser_manager,
        rollbacker_manager,
        confirmeduser_manager
    ]

    for manager in managers:
        body = manager.get_report_page(t_start)
        page_title = f'{BASEPAGE}/{manager.report_subpage}'

        save_report(page_title, EDIT_SUMMARY, body)


if __name__=='__main__':
    main()
