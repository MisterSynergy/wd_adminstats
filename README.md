# wd_adminstats
Wikidata bot to log activity of users with elevated rights. Since some user rights are being removed from inactive accounts, the community needs to track activity.

## Technical requirements
The bot is currently scheduled to run daily on [Toolforge](https://wikitech.wikimedia.org/wiki/Portal:Toolforge) from within the `msynbot` tool account. It depends on the [shared pywikibot files](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Pywikibot#Using_the_shared_Pywikibot_files_(recommended_setup)) and is running in a Kubernetes environment using Python 3.9.2.

On Toolforge, if you make shared pywikibot available via your tool's PYTHONPATH, there may be an issue when installing Python requirements in your virtual environment. You can temporarily remove pywikibot from PYTHONPATH via `~/.bash_profile `.