from django.urls import path
from chores import views

app_name = 'chores'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard'),
    path('api/members/', views.members_api, name='api_members'),
    path('api/members', views.members_api),
    path('api/chores/', views.chores_api, name='api_chores'),
    path('api/chores', views.chores_api),
    path('api/assignments/', views.assignments_api, name='api_assignments'),
    path('api/assignments', views.assignments_api),
    path('api/assignments/<int:id>/complete/', views.complete_assignment_api, name='api_assignment_complete'),
    path('api/assignments/<int:id>/complete', views.complete_assignment_api),
    path('api/allocate/', views.allocate_api, name='api_allocate'),
    path('api/allocate', views.allocate_api),
]
