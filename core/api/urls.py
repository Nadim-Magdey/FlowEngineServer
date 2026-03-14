from django.urls import path
from .views import GetServices, FlowConstraintsView,ServiceInputsView, CheckAuth,ServiceFlowsView, CybersourceFlexV2EncryptView, APGMastercardEncryptView, UserLogsView, UserNotification, UserInfoView, UserProxyView, CreateAuthSessionView, CheckTelegramSessionView, TelegramWebhookView


urlpatterns = [
    path('service/inputs/', ServiceInputsView.as_view(), name='service-inputs'),
    path('service/flows/', ServiceFlowsView.as_view(), name='service-flows'),
    
    path('encrypt/cyber/', CybersourceFlexV2EncryptView.as_view(), name='encrypt-cybersource-v2'),
    path('encrypt/apg/', APGMastercardEncryptView.as_view(), name='encrypt-apg-mastercard'),

    path("auth/check/", CheckAuth.as_view(), name ="check-auth"),

    path("services/get/", GetServices().as_view(), name ="get-services"),
    path('flow-constraints/', FlowConstraintsView.as_view(), name='flow-constraints'),

    path('log/', UserLogsView().as_view(), name='user-log'),
    path('notification/', UserNotification().as_view(), name='user-notification'),

    path('user-info/', UserInfoView().as_view(), name='user-info'),
    path('user-proxy/', UserProxyView().as_view(), name='user-proxy'),
    path('telegram/create/', CreateAuthSessionView.as_view(), name='create_telegram_session'),
    path('telegram/check/', CheckTelegramSessionView.as_view(), name='check_telegram_session'),
    path('telegram/webhook/', TelegramWebhookView.as_view(), name='telegram_webhook'),
]

