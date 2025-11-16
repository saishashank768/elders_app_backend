from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .viewsets import CareRequestViewSet, TaskViewSet, DonationViewSet, PaymentViewSet, MessageViewSet, NotificationViewSet, DocumentViewSet, CityViewSet
from . import views_webhooks

router = DefaultRouter()
router.register(r'requests', CareRequestViewSet, basename='requests')
router.register(r'tasks', TaskViewSet)
router.register(r'donations', DonationViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'messages', MessageViewSet)
router.register(r'notifications', NotificationViewSet)
router.register(r'documents', DocumentViewSet)
router.register(r'cities', CityViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('payments/webhook/', views_webhooks.payment_webhook, name='payment-webhook'),
]
