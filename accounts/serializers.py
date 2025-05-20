from rest_framework import serializers
from .models import User, BanquetBooking, Cafe
from django.contrib.auth.password_validation import validate_password


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    role = serializers.SerializerMethodField()
    cafe = serializers.PrimaryKeyRelatedField(queryset=Cafe.objects.all(), required=False, write_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
    role_input = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role', 'role_input', 'cafe', 'date_joined', 'is_superuser')
        read_only_fields = ('id', 'date_joined', 'is_superuser', 'role')

    def get_role(self, obj):
        print(f"Getting role for user {obj.username}")
        print(f"is_superuser: {obj.is_superuser}")
        print(f"is_staff: {obj.is_staff}")
        
        if obj.is_superuser:
            return 'superadmin'
        elif obj.is_staff:
            return 'admin'
        return 'assistant'

    def to_representation(self, instance):
        data = super().to_representation(instance)
        # Добавляем информацию о кафе
        if instance.cafe:
            data['cafe'] = {
                'id': instance.cafe.id,
                'name': instance.cafe.name
            }
        return data

    def validate_password(self, value):
        if not value:  # Если пароль не указан (при обновлении)
            return value
        return value

    def validate_username(self, value):
        # Проверяем существование пользователя только при создании
        if not self.instance and User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Пользователь с таким именем уже существует")
        return value

    def validate(self, data):
        # Проверяем, что кафе указано для admin и assistant
        if data.get('role_input') in ['admin', 'assistant'] and not data.get('cafe'):
            raise serializers.ValidationError({"cafe": "Кафе обязательно для администратора и ассистента"})
        return data

    def create(self, validated_data):
        if 'password' not in validated_data:
            raise serializers.ValidationError({"password": "Пароль обязателен при создании пользователя"})

        password = validated_data.pop('password')
        role = validated_data.pop('role_input', 'assistant')
        
        # Создаем пользователя
        user = User.objects.create(**validated_data)
        user.set_password(password)
        
        # Устанавливаем роль
        if role == 'superadmin':
            user.is_superuser = True
            user.is_staff = True
            user.cafe = None  # Супер-админ не привязан к кафе
        elif role == 'admin':
            user.is_superuser = False
            user.is_staff = True
        else:  # assistant
            user.is_superuser = False
            user.is_staff = False
        
        user.save()
        return user

    def update(self, instance, validated_data):
        # Если пароль указан, обновляем его
        if 'password' in validated_data:
            password = validated_data.pop('password')
            if password:  # Обновляем пароль только если он не пустой
                instance.set_password(password)

        # Обновляем остальные поля
        for attr, value in validated_data.items():
            if attr != 'role_input':  # Пропускаем role_input при обновлении полей
                setattr(instance, attr, value)

        # Обновляем роль
        if 'role_input' in validated_data:
            role = validated_data.pop('role_input')
            if role == 'superadmin':
                instance.is_superuser = True
                instance.is_staff = True
                instance.cafe = None  # Супер-админ не привязан к кафе
            elif role == 'admin':
                instance.is_superuser = False
                instance.is_staff = True
            else:  # assistant
                instance.is_superuser = False
                instance.is_staff = False

        instance.save()
        return instance

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password', 'password2', 'role']
    
    def validate(self, data):
        # Проверка, что пароли совпадают
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return data

    def create(self, validated_data):
        # Убираем password2 из данных
        validated_data.pop('password2')
        
        # Создаем пользователя
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            role=validated_data['role'],
            password=validated_data['password']
        )
        return user

class BanquetBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BanquetBooking
        fields = [
            'id', 'cafe', 'assistant',
            'client_name', 'client_phone', 'client_email',
            'date', 'time', 'duration_hours', 'number_of_people',
            'price_per_visitor', 'total_price', 'prepayment',
            'remaining_payment', 'created_at',
            'event_name', 'event_status', 'client_comment',
        ]
        read_only_fields = ['id', 'created_at', 'total_price', 'remaining_payment']

    def validate(self, data):
        instance = getattr(self, 'instance', None)

        number_of_people = data.get('number_of_people', getattr(instance, 'number_of_people', None))
        price_per_visitor = data.get('price_per_visitor', getattr(instance, 'price_per_visitor', None))
        prepayment = data.get('prepayment', getattr(instance, 'prepayment', None))

        # Проверка на наличие нужных данных
        if number_of_people is None or price_per_visitor is None:
            raise serializers.ValidationError("Нужно указать количество людей и цену за одного посетителя")

        total_price = number_of_people * price_per_visitor

        if prepayment is None:
            raise serializers.ValidationError("Необходимо указать сумму предоплаты")

        if prepayment > total_price:
            raise serializers.ValidationError("Предоплата не может быть больше общей стоимости")

        # Добавляем вычисления, если они нужны
        data['total_price'] = total_price
        data['remaining_payment'] = total_price - prepayment

        return data


class CafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cafe
        fields = ['id', 'name', 'address', 'organization_id']
