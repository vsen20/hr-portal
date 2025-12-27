from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from hr_core.models import Employee, Department, Position, EmployeeDocument
from platform_core.models import Organization, OrgSettings, OrgModule


class Command(BaseCommand):
    help = "Create default user roles and assign permissions"

    def handle(self, *args, **options):
        self.stdout.write("Setting up roles and permissions...")

        roles = {
            "ORG_ADMIN": {
                "models": [
                    Employee,
                    Department,
                    Position,
                    EmployeeDocument,
                    Organization,
                    OrgSettings,
                    OrgModule,
                ],
                "perms": ["add", "change", "view", "delete"],
            },
            "HR_MANAGER": {
                "models": [
                    Employee,
                    Department,
                    Position,
                    EmployeeDocument,
                ],
                "perms": ["add", "change", "view"],
            },
            "EMPLOYEE": {
                "models": [
                    Employee,
                    EmployeeDocument,
                ],
                "perms": ["view"],
            },
        }

        for role_name, config in roles.items():
            group, created = Group.objects.get_or_create(name=role_name)

            if created:
                self.stdout.write(f"Created group: {role_name}")
            else:
                self.stdout.write(f"Group already exists: {role_name}")

            permissions = []

            for model in config["models"]:
                content_type = ContentType.objects.get_for_model(model)

                for perm in config["perms"]:
                    codename = f"{perm}_{model._meta.model_name}"
                    try:
                        permission = Permission.objects.get(
                            content_type=content_type,
                            codename=codename,
                        )
                        permissions.append(permission)
                    except Permission.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(
                                f"Permission not found: {codename}"
                            )
                        )

            group.permissions.set(permissions)

            self.stdout.write(
                self.style.SUCCESS(
                    f"Assigned {len(permissions)} permissions to {role_name}"
                )
            )

        self.stdout.write(self.style.SUCCESS("Roles setup completed."))
