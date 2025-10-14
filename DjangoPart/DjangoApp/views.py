from django.http import JsonResponse
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .utils import generate_verification_code, send_verification_email
from django.core.cache import cache
import json


# def get_session(request):
#     # Чтение данных из сессии
#     email = request.session.get('email')
#     username = request.session.get('username')
#     return email, username
#
# def set_session(request, verification_code):
#     # Запись данных в сессию
#     request.session['username'] = (json.loads(request.body)).get('login')
#     request.session['email'] = (json.loads(request.body)).get('email')
#     request.session['password'] = make_password((json.loads(request.body)).get('password'))
#     request.session['verification_code'] = verification_code
#     request.session.set_expiry(3600)  # срок жизни 1 час

@method_decorator(csrf_exempt, name='dispatch')
class Step1RegistrationView(View):
    def post(self, request):
        # 1. Получаем данные
        data = json.loads(request.body)
        username = data.get('login')
        password = data.get('password')
        email = data.get('email')
        print(username, password, email)

        # TODO: Добавь проверку, что пользователь с таким username/email не существует

        # 2. Генерируем код верификации
        verification_code = generate_verification_code()

        cache.set_many({"username": username, 'password' : make_password(password), 'email' : email, 'verification_code' : verification_code}, 300)
        # set_session(request, verification_code)


        # Исправлено: убрана строка с req_session.id, так как эта переменная не определена
        request.session['registration_session_id'] = str(request.session.session_key)

        # 4. Отправляем код на email
        try:
            send_verification_email(email, verification_code)
            return JsonResponse({'status': 'success', 'message': 'Код отправлен'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Ошибка отправки email'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class Step2VerificationView(View):
    def post(self, request):
        # Получаем введенный код
        data = json.loads(request.body)
        user_code = data.get('code')

        stored_code = cache.get('verification_code')

        # Получаем данные из сессии
        # stored_code = request.session.get('verification_code')
        # session_id = request.session.get('registration_session_id')
        # print(get_session(request))

        print(user_code, stored_code)
        # Проверка через сессию
        if user_code == stored_code:
            print('успех')
            return JsonResponse({'status': 'success', 'message': 'Успешная регистрация'})


        return JsonResponse({'status': 'error', 'message': 'Неверный код'})

    def _complete_registration(self, request, data):
        """Завершает регистрацию и создает пользователя."""
        # Создаем пользователя
        try:
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password']  # make_password уже применен
            )

            # Помечаем сессию как верифицированную (если использовали модель)
            if hasattr(data, 'is_verified'):  # Это объект модели
                data.is_verified = True
                data.save()

            # Очищаем сессию
            if 'registration_data' in request.session:
                del request.session['registration_data']
            if 'registration_session_id' in request.session:
                del request.session['registration_session_id']

            return JsonResponse({'status': 'success', 'message': 'Регистрация завершена'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Ошибка создания пользователя'})



