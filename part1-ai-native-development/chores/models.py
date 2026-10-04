from django.db import models
from django.utils import timezone


class Member(models.Model):
    """Represents a member of the shared household."""
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Chore(models.Model):
    """Represents a recurring or ad-hoc chore in the household."""

    class Frequency(models.TextChoices):
        DAILY = 'daily', 'Daily'
        WEEKLY = 'weekly', 'Weekly'
        BIWEEKLY = 'biweekly', 'Bi-weekly'
        AS_NEEDED = 'as_needed', 'As-needed'

    class EffortLevel(models.IntegerChoices):
        LOW = 1, 'Low'
        MEDIUM = 2, 'Medium'
        HIGH = 3, 'High'

    title = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.WEEKLY,
    )
    effort_level = models.IntegerField(
        choices=EffortLevel.choices,
        default=EffortLevel.MEDIUM,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.get_frequency_display()})"


class Assignment(models.Model):
    """Represents the assignment of a chore to a member."""

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        SKIPPED = 'skipped', 'Skipped'

    chore = models.ForeignKey(
        Chore,
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    assigned_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    completed_at = models.DateTimeField(null=True, blank=True)
    ai_reasoning = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-assigned_date', 'status']

    def __str__(self):
        return f"{self.chore.title} -> {self.member.name} ({self.get_status_display()})"

    def mark_completed(self):
        """Mark this assignment as completed and set timestamp."""
        self.status = self.Status.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
