import json
import os
from datetime import timedelta
from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from chores.allocation.llm_engine import LLMAllocationEngine
from chores.allocation.mock_engine import MockAllocationEngine
from chores.allocation.schemas import (
    AllocationRequest,
    ChoreData,
    MemberData,
    WorkloadHistory,
)
from chores.models import Assignment, Chore, Member


@csrf_exempt
def members_api(request):
    """
    Handle member list and creation.
    - GET /api/members/: List members with assignment stats.
    - POST /api/members/: Create a new member.
    """
    if request.method == 'GET':
        members = Member.objects.annotate(
            pending_assignments_count=Count(
                'assignments',
                filter=Q(assignments__status=Assignment.Status.PENDING),
                distinct=True,
            ),
            completed_assignments_count=Count(
                'assignments',
                filter=Q(assignments__status=Assignment.Status.COMPLETED),
                distinct=True,
            ),
        ).order_by('name')

        data = [
            {
                'id': member.id,
                'name': member.name,
                'created_at': member.created_at.isoformat(),
                'pending_assignments_count': member.pending_assignments_count,
                'completed_assignments_count': member.completed_assignments_count,
            }
            for member in members
        ]
        return JsonResponse(data, safe=False, status=200)

    elif request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            payload = json.loads(body) if body.strip() else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)

        if not isinstance(payload, dict):
            return JsonResponse({'error': 'Request body must be a JSON object.'}, status=400)

        name = payload.get('name')
        if not name or not isinstance(name, str) or not name.strip():
            return JsonResponse({'error': 'Member name is required.'}, status=400)

        name = name.strip()

        if Member.objects.filter(name=name).exists():
            return JsonResponse({'error': 'Member with this name already exists.'}, status=400)

        try:
            member = Member.objects.create(name=name)
        except IntegrityError:
            return JsonResponse({'error': 'Member with this name already exists.'}, status=400)

        return JsonResponse(
            {
                'id': member.id,
                'name': member.name,
                'created_at': member.created_at.isoformat(),
                'pending_assignments_count': 0,
                'completed_assignments_count': 0,
            },
            status=201,
        )

    return JsonResponse({'error': f'Method {request.method} not allowed.'}, status=405)


@csrf_exempt
def chores_api(request):
    """
    Handle chore list and creation.
    - GET /api/chores/: List chores, filtered by is_active (default: true).
    - POST /api/chores/: Create a new chore.
    """
    if request.method == 'GET':
        is_active_param = request.GET.get('is_active')
        if is_active_param is None:
            chores = Chore.objects.filter(is_active=True)
        else:
            val = is_active_param.strip().lower()
            if val in ('true', '1'):
                chores = Chore.objects.filter(is_active=True)
            elif val in ('false', '0'):
                chores = Chore.objects.filter(is_active=False)
            elif val == 'all':
                chores = Chore.objects.all()
            else:
                return JsonResponse(
                    {'error': "Invalid boolean for is_active. Expected 'true', 'false', or 'all'."},
                    status=400,
                )

        data = [
            {
                'id': chore.id,
                'title': chore.title,
                'description': chore.description,
                'frequency': chore.frequency,
                'effort_level': chore.effort_level,
                'is_active': chore.is_active,
            }
            for chore in chores
        ]
        return JsonResponse(data, safe=False, status=200)

    elif request.method == 'POST':
        try:
            body = request.body.decode('utf-8')
            payload = json.loads(body) if body.strip() else {}
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)

        if not isinstance(payload, dict):
            return JsonResponse({'error': 'Request body must be a JSON object.'}, status=400)

        title = payload.get('title')
        if not title or not isinstance(title, str) or not title.strip():
            return JsonResponse({'error': 'Title is required.'}, status=400)
        title = title.strip()

        # Validate effort_level
        effort_level = payload.get('effort_level', Chore.EffortLevel.MEDIUM)
        try:
            effort_level = int(effort_level)
        except (ValueError, TypeError):
            return JsonResponse(
                {'error': 'Invalid effort_level. Must be 1, 2, or 3.'},
                status=400,
            )

        valid_efforts = [choice[0] for choice in Chore.EffortLevel.choices]
        if effort_level not in valid_efforts:
            return JsonResponse(
                {'error': 'Invalid effort_level. Must be 1, 2, or 3.'},
                status=400,
            )

        # Validate frequency
        frequency = payload.get('frequency', Chore.Frequency.WEEKLY)
        if not isinstance(frequency, str):
            return JsonResponse(
                {'error': f"Invalid frequency. Allowed choices: {[c[0] for c in Chore.Frequency.choices]}."},
                status=400,
            )
        frequency = frequency.strip().lower()
        valid_frequencies = [choice[0] for choice in Chore.Frequency.choices]
        if frequency not in valid_frequencies:
            return JsonResponse(
                {'error': f"Invalid frequency '{frequency}'. Allowed choices: {valid_frequencies}."},
                status=400,
            )

        description = payload.get('description', '')
        if not isinstance(description, str):
            description = str(description)

        is_active = payload.get('is_active', True)
        if isinstance(is_active, str):
            is_active = is_active.strip().lower() in ('true', '1')
        elif not isinstance(is_active, bool):
            is_active = bool(is_active)

        chore = Chore.objects.create(
            title=title,
            description=description,
            frequency=frequency,
            effort_level=effort_level,
            is_active=is_active,
        )

        return JsonResponse(
            {
                'id': chore.id,
                'title': chore.title,
                'description': chore.description,
                'frequency': chore.frequency,
                'effort_level': chore.effort_level,
                'is_active': chore.is_active,
            },
            status=201,
        )

    return JsonResponse({'error': f'Method {request.method} not allowed.'}, status=405)


@csrf_exempt
def assignments_api(request):
    """
    Handle assignments listing.
    - GET /api/assignments/: List assignments, filterable by status and member_id.
    """
    if request.method == 'GET':
        assignments = Assignment.objects.select_related('chore', 'member').all()

        status_param = request.GET.get('status')
        if status_param is not None:
            status_param = status_param.strip().lower()
            valid_statuses = [choice[0] for choice in Assignment.Status.choices]
            if status_param not in valid_statuses:
                return JsonResponse(
                    {'error': f"Invalid status '{status_param}'. Allowed choices: {valid_statuses}."},
                    status=400,
                )
            assignments = assignments.filter(status=status_param)

        member_id_param = request.GET.get('member_id')
        if member_id_param is not None:
            try:
                member_id = int(member_id_param)
            except (ValueError, TypeError):
                return JsonResponse({'error': 'Invalid member_id. Must be an integer.'}, status=400)
            assignments = assignments.filter(member_id=member_id)

        data = [
            {
                'id': assignment.id,
                'chore': {
                    'id': assignment.chore.id,
                    'title': assignment.chore.title,
                    'description': assignment.chore.description,
                    'frequency': assignment.chore.frequency,
                    'effort_level': assignment.chore.effort_level,
                },
                'member': {
                    'id': assignment.member.id,
                    'name': assignment.member.name,
                },
                'assigned_date': assignment.assigned_date.isoformat() if assignment.assigned_date else None,
                'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
                'status': assignment.status,
                'completed_at': assignment.completed_at.isoformat() if assignment.completed_at else None,
                'ai_reasoning': assignment.ai_reasoning,
            }
            for assignment in assignments
        ]
        return JsonResponse(data, safe=False, status=200)

    return JsonResponse({'error': f'Method {request.method} not allowed.'}, status=405)


@csrf_exempt
def complete_assignment_api(request, id=None, assignment_id=None):
    """
    Handle marking an assignment as completed.
    - POST /api/assignments/<id>/complete/
    """
    if request.method != 'POST':
        return JsonResponse({'error': f'Method {request.method} not allowed.'}, status=405)

    target_id = id if id is not None else assignment_id

    # Validate optional JSON body if present
    content_type = request.content_type or ''
    if request.body:
        body_str = request.body.decode('utf-8', errors='ignore').strip()
        if 'application/json' in content_type or (body_str.startswith('{') and body_str.endswith('}')):
            try:
                payload = json.loads(body_str)
                if not isinstance(payload, dict):
                    return JsonResponse({'error': 'Request body must be a JSON object.'}, status=400)
                status = payload.get('status')
                if status is not None and status != Assignment.Status.COMPLETED:
                    return JsonResponse(
                        {'error': f"Invalid status '{status}'. Expected 'completed'."},
                        status=400,
                    )
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
        elif body_str and not body_str.startswith('--') and 'multipart' not in content_type:
            return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)

    try:
        assignment = Assignment.objects.select_related('chore', 'member').get(pk=target_id)
    except Assignment.DoesNotExist:
        return JsonResponse({'error': f'Assignment with id {target_id} not found.'}, status=404)

    # Idempotent state transition
    assignment.mark_completed()

    return JsonResponse(
        {
            'id': assignment.id,
            'chore': {
                'id': assignment.chore.id,
                'title': assignment.chore.title,
                'description': assignment.chore.description,
                'frequency': assignment.chore.frequency,
                'effort_level': assignment.chore.effort_level,
            },
            'member': {
                'id': assignment.member.id,
                'name': assignment.member.name,
            },
            'assigned_date': assignment.assigned_date.isoformat() if assignment.assigned_date else None,
            'due_date': assignment.due_date.isoformat() if assignment.due_date else None,
            'status': assignment.status,
            'completed_at': assignment.completed_at.isoformat() if assignment.completed_at else None,
            'ai_reasoning': assignment.ai_reasoning,
        },
        status=200,
    )


def get_allocation_engine():
    """
    Instantiate the appropriate allocation engine based on AI_PROVIDER settings.
    Defaults to MockAllocationEngine when no provider or 'mock' is configured.
    """
    provider = getattr(settings, 'AI_PROVIDER', None) or os.environ.get('AI_PROVIDER')
    if provider and str(provider).lower() != 'mock':
        return LLMAllocationEngine()
    return MockAllocationEngine()


@csrf_exempt
def allocate_api(request):
    """
    Trigger smart chore allocation.
    - POST /api/allocate/
    """
    if request.method != 'POST':
        return JsonResponse({'error': f'Method {request.method} not allowed.'}, status=405)

    payload = {}
    if request.body:
        try:
            body = request.body.decode('utf-8').strip()
            if body:
                payload = json.loads(body)
                if not isinstance(payload, dict):
                    return JsonResponse({'error': 'Request body must be a JSON object.'}, status=400)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)

    user_notes = payload.get('user_notes', '')
    if not isinstance(user_notes, str):
        user_notes = str(user_notes) if user_notes is not None else ''

    dry_run = payload.get('dry_run', False)
    if isinstance(dry_run, str):
        dry_run = dry_run.strip().lower() in ('true', '1')
    elif not isinstance(dry_run, bool):
        dry_run = bool(dry_run)

    members = Member.objects.all().order_by('name')
    chores = Chore.objects.filter(is_active=True).order_by('title')

    if not members.exists() or not chores.exists():
        return JsonResponse(
            {
                'error': 'Cannot run allocation without active members and chores.',
                'message': 'Cannot run allocation without active members and chores.',
            },
            status=400,
        )

    # Calculate recent workload history per member (past 14 days)
    cutoff_date = timezone.now().date() - timedelta(days=14)
    effort_by_member = dict(
        Assignment.objects.filter(assigned_date__gte=cutoff_date)
        .exclude(status=Assignment.Status.SKIPPED)
        .values('member_id')
        .annotate(recent_effort=Sum('chore__effort_level'))
        .values_list('member_id', 'recent_effort')
    )

    workload_history = [
        WorkloadHistory(
            member_id=m.id,
            recent_effort_sum=effort_by_member.get(m.id, 0) or 0,
        )
        for m in members
    ]

    allocation_request = AllocationRequest(
        members=[MemberData(id=m.id, name=m.name) for m in members],
        chores=[
            ChoreData(
                id=c.id,
                title=c.title,
                effort_level=c.effort_level,
                frequency=c.frequency,
            )
            for c in chores
        ],
        workload_history=workload_history,
        user_notes=user_notes,
    )

    engine = get_allocation_engine()
    allocation_response = engine.allocate(allocation_request)

    member_map = {m.id: m for m in members}
    chore_map = {c.id: c for c in chores}

    if not dry_run:
        with transaction.atomic():
            persisted_assignments = []
            for proposed in allocation_response.assignments:
                assignment = Assignment.objects.create(
                    chore=chore_map[proposed.chore_id],
                    member=member_map[proposed.member_id],
                    status=Assignment.Status.PENDING,
                    ai_reasoning=proposed.reasoning,
                    assigned_date=timezone.now().date(),
                )
                persisted_assignments.append(assignment)

        serialized_assignments = [
            {
                'id': a.id,
                'chore_id': a.chore_id,
                'member_id': a.member_id,
                'chore_title': a.chore.title,
                'member_name': a.member.name,
                'chore': {
                    'id': a.chore.id,
                    'title': a.chore.title,
                    'description': a.chore.description,
                    'frequency': a.chore.frequency,
                    'effort_level': a.chore.effort_level,
                },
                'member': {
                    'id': a.member.id,
                    'name': a.member.name,
                },
                'assigned_date': a.assigned_date.isoformat() if a.assigned_date else None,
                'due_date': a.due_date.isoformat() if a.due_date else None,
                'status': a.status,
                'completed_at': a.completed_at.isoformat() if a.completed_at else None,
                'ai_reasoning': a.ai_reasoning,
                'reasoning': a.ai_reasoning,
            }
            for a in persisted_assignments
        ]
        assignments_created_count = len(persisted_assignments)
    else:
        serialized_assignments = [
            {
                'id': None,
                'chore_id': proposed.chore_id,
                'member_id': proposed.member_id,
                'chore_title': chore_map[proposed.chore_id].title if proposed.chore_id in chore_map else '',
                'member_name': member_map[proposed.member_id].name if proposed.member_id in member_map else '',
                'chore': {
                    'id': chore_map[proposed.chore_id].id,
                    'title': chore_map[proposed.chore_id].title,
                    'description': chore_map[proposed.chore_id].description,
                    'frequency': chore_map[proposed.chore_id].frequency,
                    'effort_level': chore_map[proposed.chore_id].effort_level,
                } if proposed.chore_id in chore_map else None,
                'member': {
                    'id': member_map[proposed.member_id].id,
                    'name': member_map[proposed.member_id].name,
                } if proposed.member_id in member_map else None,
                'assigned_date': timezone.now().date().isoformat(),
                'due_date': None,
                'status': Assignment.Status.PENDING,
                'completed_at': None,
                'ai_reasoning': proposed.reasoning,
                'reasoning': proposed.reasoning,
            }
            for proposed in allocation_response.assignments
        ]
        assignments_created_count = 0

    return JsonResponse(
        {
            'success': True,
            'engine_used': allocation_response.engine_used,
            'assignments_created': assignments_created_count,
            'raw_reasoning_summary': allocation_response.raw_reasoning_summary,
            'assignments': serialized_assignments,
        },
        status=200,
    )


def dashboard_view(request):
    """
    Render the main household chore management dashboard.
    Computes summary metrics context:
    - total_active_chores: Active chore count.
    - pending_assignments_count: Uncompleted pending assignments count.
    - completed_this_week_count: Assignments completed within the past 7 days.
    - active_members_count: Total active household members count.
    """
    total_active_chores = Chore.objects.filter(is_active=True).count()
    pending_assignments_count = Assignment.objects.filter(status=Assignment.Status.PENDING).count()

    seven_days_ago = timezone.now() - timedelta(days=7)
    completed_this_week_count = Assignment.objects.filter(
        status=Assignment.Status.COMPLETED
    ).filter(
        Q(completed_at__gte=seven_days_ago) |
        Q(completed_at__isnull=True, assigned_date__gte=seven_days_ago.date())
    ).count()

    active_members_count = Member.objects.count()

    context = {
        'total_active_chores': total_active_chores,
        'pending_assignments_count': pending_assignments_count,
        'completed_this_week_count': completed_this_week_count,
        'active_members_count': active_members_count,
    }

    return render(request, 'chores/dashboard.html', context)
