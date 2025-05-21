import random
import requests

from django.core.mail import send_mail
from django.contrib.auth import authenticate

from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth.models import User

from .models import BanquetBooking, Cafe, User
from .permissions import IsAdminUserRole, IsSuperAdmin
from .serializers import RegisterUserSerializer, BanquetBookingSerializer, CafeSerializer, UserSerializer

# Create your views here.
class RegisterView(APIView):
    """
    Представление для регистрации пользователя.
    """
    permission_classes = [AllowAny]  # Разрешаем доступ всем

    def post(self, request, *args, **kwargs):
        serializer = RegisterUserSerializer(data=request.data)
        
        if serializer.is_valid():
            # Сохраняем пользователя
            serializer.save()
            return Response({'message': 'Пользователь успешно зарегистрирован'}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class LoginView(APIView):
    """
    Представление для логина пользователя и получения JWT токенов.
    """
    permission_classes = [AllowAny] 

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        # Аутентификация пользователя
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Если пользователь существует, создаём токены
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'detail': 'Invalid credentials'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
class LogoutView(APIView):
    """
    Представление для разлогинивания пользователя (удаление токена).
    """
    permission_classes = [AllowAny]  # Только аутентифицированные пользователи могут выйти

    def post(self, request, *args, **kwargs):
        try:
            # Получаем токен из запроса
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)

            # Добавляем токен в черный список
            token.blacklist()

            return Response({"detail": "Вы успешно разлогинились"}, status=status.HTTP_205_RESET_CONTENT)

        except TokenError:
            return Response({"detail": "Неверный токен"}, status=status.HTTP_400_BAD_REQUEST)
    
class BanquetBookingListView(generics.ListAPIView):
    serializer_class = BanquetBookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'superadmin':
            return BanquetBooking.objects.all()
        else:
            return BanquetBooking.objects.filter(cafe=user.cafe)
        
class BanquetBookingCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()

        # Автоматически подставляем текущего пользователя как assistant
        data['assistant'] = request.user.id

        serializer = BanquetBookingSerializer(data=data)
        if request.user.role in ['assistant', 'admin']:
            if int(data.get('cafe')) != request.user.cafe_id:
                return Response({'error': 'Вы не можете создавать заявки для другого кафе.'}, status=status.HTTP_403_FORBIDDEN)
        if serializer.is_valid():
            # Сохраняем бронь с подставленным ассистентом
            booking = serializer.save(assistant=request.user)
            return Response({'message': 'Бронь успешно создана', 'booking': serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class BanquetBookingUpdateView(generics.RetrieveUpdateAPIView):
    queryset = BanquetBooking.objects.all()
    serializer_class = BanquetBookingSerializer
    permission_classes = [IsAuthenticated, IsAdminUserRole]
    def perform_update(self, serializer):
        user = self.request.user
        booking = serializer.instance

        # Проверка: можно обновлять только своё кафе
        if user.role in ['assistant', 'admin'] and booking.cafe != user.cafe:
            raise PermissionDenied("Вы не можете редактировать заявки другого кафе.")
        
        serializer.save()

class BanquetBookingDeleteView(generics.DestroyAPIView):
    queryset = BanquetBooking.objects.all()
    serializer_class = BanquetBookingSerializer
    permission_classes = [IsAuthenticated, IsAdminUserRole]
    def perform_destroy(self, instance):
        user = self.request.user
        if user.role in ['assistant', 'admin'] and instance.cafe != user.cafe:
            raise PermissionDenied("Вы не можете удалить заявку другого кафе.")
        instance.delete()



class SendConfirmationCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        try:
            booking = BanquetBooking.objects.get(id=booking_id)
            if request.user.role in ['assistant', 'admin'] and booking.cafe != request.user.cafe:
                return Response({'error': 'Вы не можете управлять заявками другого кафе.'}, status=status.HTTP_403_FORBIDDEN)
        except BanquetBooking.DoesNotExist:
            return Response({'error': 'Бронь не найдена'}, status=status.HTTP_404_NOT_FOUND)

        method = request.data.get('method', 'sms')  # по умолчанию sms
        print(method)
        code = f"{random.randint(1000, 9999)}"
        booking.confirmation_code = code
        booking.save()

        if method == 'email':
            if not booking.client_email:
                raise ValidationError("У клиента не указана почта.")
            
            try:
                send_mail(
                    subject='Броньды растау коды',
                    message=(
                        f"*Сәлеметсіз бе, {booking.client_name}*\n"
                        f"Мейрамхана -  {booking.cafe.name}. өтетін іс-шара - {booking.event_name},  "
                        f"күні - {booking.date}, басталу уақыты - {booking.time}, адам саны - {booking.number_of_people}, "
                        f"бір адамға бағасы - {booking.price_per_visitor} ₸, алдын ала төленген қаражат - {booking.prepayment} ₸,\n"
                        f"Жоғарыдағы ақпаратпен мұқият танысып шығыңыз.\n\n"
                        f"Администраторға көрсетіңіз - {code}"
                    ),
                from_email='muafikd@gmail.com',
                recipient_list=[booking.client_email],
                fail_silently=False,
)

            except Exception as e:
                return Response({'error': f'Ошибка при отправке email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        elif method == 'sms':
            payload = {
                "booking_id": booking.id,
                "client_name": booking.client_name,
                "phone": booking.client_phone,
                "date": str(booking.date),
                "time": str(booking.time),
                "event_name": booking.event_name,
                "event_status": booking.event_status,
                "confirmation_code": code,
                "organizationId": booking.cafe.organization_id,
                "organizationName": booking.cafe.name,
                "prepayment": str(booking.prepayment),
                "number_of_people": str(booking.number_of_people),
                "price_per_visitor": str(booking.price_per_visitor)
            }

            try:
                requests.post("https://miramgazy.app.n8n.cloud/webhook/6c740239-c83b-42a2-aa78-71bfef56afef", json=payload, timeout=5)
            except requests.RequestException:
                return Response({'error': 'Ошибка при отправке кода на n8n'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            raise ValidationError("Неверный способ отправки. Используйте 'sms' или 'email'.")

        return Response({'message': f'Код подтверждения отправлен через {method}'}, status=status.HTTP_200_OK)
    
class ConfirmBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, booking_id):
        code = request.data.get('code')

        try:
            booking = BanquetBooking.objects.get(id=booking_id)
            if request.user.role in ['assistant', 'admin'] and booking.cafe != request.user.cafe:
                return Response({'error': 'Вы не можете управлять заявками другого кафе.'}, status=status.HTTP_403_FORBIDDEN)
        except BanquetBooking.DoesNotExist:
            return Response({'error': 'Бронь не найдена'}, status=status.HTTP_404_NOT_FOUND)

        if booking.confirmation_code != code:
            return Response({'error': 'Неверный код подтверждения'}, status=status.HTTP_400_BAD_REQUEST)

        booking.event_status = 'confirmed'
        booking.confirmation_code = None  # очищаем, т.к. больше не нужен
        booking.save()

        return Response({'message': 'Заявка успешно подтверждена'}, status=status.HTTP_200_OK)

class CafeListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Определяем роль пользователя
        is_superadmin = request.user.is_superuser
        print(f"User {request.user.username}: is_superuser={is_superadmin}")
        
        if is_superadmin:
            cafes = Cafe.objects.all()
            print(f"Superadmin: found {cafes.count()} cafes")
        else:
            cafes = Cafe.objects.filter(id=request.user.cafe_id)
            print(f"Regular user: found {cafes.count()} cafes")
            
        serializer = CafeSerializer(cafes, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'Только супер-администратор может создавать кафе'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = CafeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CafeDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Cafe.objects.get(pk=pk)
        except Cafe.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        cafe = self.get_object(pk)
        if not request.user.is_superuser and request.user.cafe_id != cafe.id:
            return Response({'error': 'У вас нет доступа к этому кафе'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        serializer = CafeSerializer(cafe)
        return Response(serializer.data)

    def put(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Только супер-администратор может редактировать кафе'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        cafe = self.get_object(pk)
        serializer = CafeSerializer(cafe, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if not request.user.is_superuser:
            return Response({'error': 'Только супер-администратор может удалять кафе'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        cafe = self.get_object(pk)
        cafe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def user_list(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def delete_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([IsAuthenticated, IsSuperAdmin])
def update_user(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    # Если пароль не указан, удаляем его из данных запроса
    if 'password' not in request.data or not request.data['password']:
        request.data.pop('password', None)
        serializer = UserSerializer(user, data=request.data, partial=True)
    else:
        serializer = UserSerializer(user, data=request.data)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)