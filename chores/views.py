import json
from django.db import IntegrityError
from django.db.models import Count, Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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
