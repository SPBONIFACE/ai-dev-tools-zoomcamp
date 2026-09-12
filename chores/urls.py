from django.urls import path
from chores import views

app_name = 'chores'

urlpatterns = [
    path('api/members/', views.members_api, name='api_members'),
    path('api/members', views.members_api),
    path('api/chores/', views.chores_api, name='api_chores'),
    path('api/chores', views.chores_api),
    path('api/assignments/', views.assignments_api, name='api_assignments'),
    path('api/assignments', views.assignments_api),
]
