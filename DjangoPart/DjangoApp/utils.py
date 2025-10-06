import random
from django.core.mail import send_mail
from django.conf import settings


def generate_verification_code(length=6):
    """Генерирует случайный цифровой код."""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def send_verification_email(email, code):
    """Отправляет email с кодом подтверждения."""
    subject = 'Ваш код подтверждения для регистрации'
    message = f'Ваш код подтверждения: {code}\nНикому не сообщайте этот код.'
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(subject, message, from_email, [email])

    