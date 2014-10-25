from django.apps.config import AppConfig
from django.utils.translation import ugettext_lazy as _


class StoresAppConfig(AppConfig):
    name = 'stores'
    verbose_name = _('Stores')
