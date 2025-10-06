from django.urls import path
from . import views

urlpatterns = [
    path('sign_up_step1', views.Step1RegistrationView.as_view(), name='register-step1'),
    path('sign_up_step2', views.Step2VerificationView.as_view(), name='register-step2'),
]