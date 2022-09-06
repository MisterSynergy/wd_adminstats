from typing import Optional

from .UserManager import User
from .AdminManager import Admin

class RequiresAdmin:
    def __init__(self, admin:Optional[User]) -> None:
        self.admin = admin

        if isinstance(self.admin, Admin):
            self.admin_inactivity = self.admin.is_inactive
            self.admin_inacticity_warn = self.admin.is_slipping_into_inactivity
        else:
            self.admin_inactivity = True
            self.admin_inacticity_warn = True

    @property
    def is_admin(self) -> bool:
        return isinstance(self.admin, Admin)

    @property
    def is_inactive_admin(self) -> bool:
        return self.admin_inactivity

    @property
    def is_slipping_into_admin_inactivity(self) -> bool:
        return self.admin_inacticity_warn