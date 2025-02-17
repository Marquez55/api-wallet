from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=1000)
    last_name = serializers.CharField(max_length=1000)
    apellidoM = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    tipo_usuario = serializers.IntegerField()  # ID del rol (2: administrador, 3: usuario, 4: Nexuz)