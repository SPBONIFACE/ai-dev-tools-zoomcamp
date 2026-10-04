from django.contrib import admin
from chores.models import Member, Chore, Assignment


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ('title', 'frequency', 'effort_level', 'is_active', 'created_at')
    list_filter = ('frequency', 'effort_level', 'is_active')
    search_fields = ('title', 'description')
    ordering = ('title',)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('chore', 'member', 'assigned_date', 'due_date', 'status', 'completed_at')
    list_filter = ('status', 'assigned_date', 'member')
    search_fields = ('chore__title', 'member__name', 'ai_reasoning')
    ordering = ('-assigned_date',)
