from .UserManager import UserWithoutInactivityPolicy, UserManager


# https://www.wikidata.org/wiki/Wikidata:IP_block_exemption


class IPBlockExemptUser(UserWithoutInactivityPolicy):
    level:str = 'ipblock-exempt'


class IPBlockExemptUserManager(UserManager):
    user_class = IPBlockExemptUser
    report_column_headers:list[str] = [
        'IP block exempt user',
        'promoted to ipblock-exempt',
        'edit count',
        'last edit'
    ]
    report_subpage = 'IP block exempted user'
    report_template = 'ipblock-exempt.template'