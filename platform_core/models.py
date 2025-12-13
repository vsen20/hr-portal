from django.db import models


class Organization(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class OrgSettings(models.Model):
    organization = models.OneToOneField(
        Organization,
        on_delete=models.CASCADE,
        related_name='settings'
    )
    timezone = models.CharField(max_length=64, default='America/Bogota')
    language = models.CharField(max_length=10, default='ru')
    currency = models.CharField(max_length=10, default='USD')
    date_format = models.CharField(max_length=20, default='YYYY-MM-DD')

    def __str__(self):
        return f"Settings for {self.organization.name}"


class OrgModule(models.Model):
    MODULE_CHOICES = [
        ('PLATFORM', 'Platform'),
        ('TIME_TRACKING', 'Time Tracking'),
        ('HR', 'HR Core'),
        ('LEAVE', 'Absences'),
        ('PAYROLL', 'Payroll'),
        ('ORG_STRUCTURE', 'Org Structure'),
    ]

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='modules'
    )
    code = models.CharField(max_length=50, choices=MODULE_CHOICES)
    enabled = models.BooleanField(default=False)

    class Meta:
        unique_together = ('organization', 'code')

    def __str__(self):
        status = 'ON' if self.enabled else 'OFF'
        return f"{self.organization.name}: {self.code} ({status})"
