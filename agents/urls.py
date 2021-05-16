from django.urls import path
from .views import (
AgentListView, AgentCreateView, AgentDetailView,
AgentUpdateView, AgentDeleteView)

urlpatterns=[
    path('',AgentListView.as_view(), name='agent_list'),
    path('<int:pk>/detail/',AgentDetailView.as_view(), name='agent_detail'),
    path('<int:pk>/update/',AgentUpdateView.as_view(), name='agent_update'),
    path('<int:pk>/delete/',AgentDeleteView.as_view(), name='agent_delete'),
    path('create/',AgentCreateView.as_view(), name='agent_create'),
]
