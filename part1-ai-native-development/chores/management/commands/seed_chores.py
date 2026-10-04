from django.core.management.base import BaseCommand
from chores.models import Member, Chore


class Command(BaseCommand):
    help = 'Seeds initial household members and chores'

    def handle(self, *args, **options):
        # 1. Seed Members
        members_data = ['Alice', 'Bob', 'Charlie']
        created_members = []
        for name in members_data:
            member, created = Member.objects.get_or_create(name=name)
            if created:
                created_members.append(name)

        self.stdout.write(self.style.SUCCESS(
            f"Members seeded: {len(created_members)} new ({', '.join(created_members) if created_members else 'all existed'})"
        ))

        # 2. Seed Common Chores
        chores_data = [
            {
                'title': 'Clean Kitchen Counters & Sink',
                'description': 'Wipe down kitchen surfaces, disinfect sink, and clear drying rack.',
                'frequency': Chore.Frequency.DAILY,
                'effort_level': Chore.EffortLevel.MEDIUM,
            },
            {
                'title': 'Take Out Trash & Recycling',
                'description': 'Empty household bins into main outdoor containers.',
                'frequency': Chore.Frequency.DAILY,
                'effort_level': Chore.EffortLevel.LOW,
            },
            {
                'title': 'Vacuum & Mop Common Areas',
                'description': 'Vacuum living room rugs and mop kitchen/hallway floors.',
                'frequency': Chore.Frequency.WEEKLY,
                'effort_level': Chore.EffortLevel.HIGH,
            },
            {
                'title': 'Deep Clean Bathrooms',
                'description': 'Scrub toilet, shower, and sink; replace bath mat and hand towels.',
                'frequency': Chore.Frequency.WEEKLY,
                'effort_level': Chore.EffortLevel.HIGH,
            },
            {
                'title': 'Restock Household Groceries',
                'description': 'Check pantry and purchase shared supplies (dish soap, toilet paper, olive oil).',
                'frequency': Chore.Frequency.BIWEEKLY,
                'effort_level': Chore.EffortLevel.MEDIUM,
            },
        ]

        created_chores = []
        for c in chores_data:
            chore, created = Chore.objects.get_or_create(
                title=c['title'],
                defaults={
                    'description': c['description'],
                    'frequency': c['frequency'],
                    'effort_level': c['effort_level'],
                }
            )
            if created:
                created_chores.append(c['title'])

        self.stdout.write(self.style.SUCCESS(
            f"Chores seeded: {len(created_chores)} new ({', '.join(created_chores) if created_chores else 'all existed'})"
        ))
        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
