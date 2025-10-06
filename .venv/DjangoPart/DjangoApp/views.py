from django.http import JsonResponse
from django.views import View
from django.contrib.auth.hashers import make_password
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .utils import generate_verification_code, send_verification_email
import json

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

        # 3. Сохраняем данные в сессии
        request.session['registration_data'] = {
            'username': username,
            'email': email,
            'password': make_password(password),
            'verification_code': verification_code,
        }

        # Исправлено: убрана строка с req_session.id, так как эта переменная не определена
        request.session['registration_session_id'] = str(request.session.session_key)

        # 4. Отправляем код на email
        try:
            send_verification_email(email, verification_code)
            return JsonResponse({'status': 'success', 'message': 'Код отправлен'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Ошибка отправки email'}, status=500)

class Step2VerificationView(View):
    def post(self, request):
        # 1. Получаем введенный код
        user_code = request.POST.get('code')

        # 2. Получаем данные из сессии
        registration_data = request.session.get('registration_data')
        session_id = request.session.get('registration_session_id')

        # Способ 1: Проверка через сессию (менее надежный)
        if registration_data:
            stored_code = registration_data.get('verification_code')
            if user_code == stored_code:
                return self._complete_registration(request, registration_data)


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

            # TODO: Можете выполнить автоматический логин здесь
            # login(request, user)

            return JsonResponse({'status': 'success', 'message': 'Регистрация завершена'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Ошибка создания пользователя'})



