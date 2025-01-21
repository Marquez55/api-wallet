from rest_framework import serializers



class AdministradorSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=1000)
    last_name = serializers.CharField(max_length=1000)
    apellidoM = serializers.CharField(max_length=50)
    email = serializers.EmailField()