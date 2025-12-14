from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Organization, OrgSettings, OrgModule


DEFAULT_MODULES = [
    'PLATFORM',
    'TIME_TRACKING',
    'HR',
    'LEAVE',
    'PAYROLL',
    'ORG_STRUCTURE',
]


@receiver(post_save, sender=Organization)
def create_defaults_for_organization(sender, instance: Organization, created: bool, **kwargs):
    if not created:
        return

    # 1) Settings
    OrgSettings.objects.get_or_create(organization=instance)

    # 2) Modules
    for code in DEFAULT_MODULES:
        OrgModule.objects.get_or_create(
            organization=instance,
            code=code,
            defaults={'enabled': code == 'PLATFORM'}  # Platform включён по умолчанию
        )
