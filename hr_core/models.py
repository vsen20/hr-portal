from django.db import models

from platform_core.models import Organization


class Department(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="departments",
    )

    name = models.CharField(max_length=150)

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="uniq_department_name_per_org",
            )
        ]

    def __str__(self) -> str:
        return self.name

class Position(models.Model):
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="positions",
    )

    name = models.CharField(max_length=150)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Position"
        verbose_name_plural = "Positions"
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="uniq_position_name_per_org",
            )
        ]

    def __str__(self) -> str:
        return self.name

class EmployeeDocument(models.Model):
    class DocumentType(models.TextChoices):
        ID = "ID", "ID / Passport"
        RESUME = "RESUME", "Resume"
        CONTRACT = "CONTRACT", "Contract"
        ADDENDUM = "ADDENDUM", "Addendum"
        OTHER = "OTHER", "Other"

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="employee_documents",
    )

    employee = models.ForeignKey(
        "Employee",
        on_delete=models.CASCADE,
        related_name="documents",
    )

    doc_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
    )

    title = models.CharField(
        max_length=255,
        help_text="Document title",
    )

    identifier = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="Document number / identifier",
    )

    issued_date = models.DateField(
        null=True,
        blank=True,
    )

    file = models.FileField(
        upload_to="employee_documents/",
        null=True,
        blank=True,
    )

    url = models.URLField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Employee document"
        verbose_name_plural = "Employee documents"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(file__isnull=False) | models.Q(url__isnull=False),
                name="employee_document_file_or_url",
            )
        ]

    def __str__(self) -> str:
        return f"{self.get_doc_type_display()} — {self.title}"

class Employee(models.Model):
    class EmploymentStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        PROBATION = "PROBATION", "Probation"
        TERMINATED = "TERMINATED", "Terminated"

    class EmploymentType(models.TextChoices):
        STAFF = "STAFF", "Staff"
        CONTRACTOR = "CONTRACTOR", "Contractor"
        
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="employees",
    )

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE,
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.STAFF,
    )

    hire_date = models.DateField(
        null=True,
        blank=True,
        help_text="Employee hire date",
    )

    probation_start_date = models.DateField(
        null=True,
        blank=True,
        help_text="Probation start date",
    )

    probation_end_date = models.DateField(
        null=True,
        blank=True,
        help_text="Probation end date",
    )

    manager = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subordinates",
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )

    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="employees",
    )


    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"

    def __str__(self) -> str:
        return f"{self.last_name} {self.first_name}"
