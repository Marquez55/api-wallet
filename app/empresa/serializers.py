from rest_framework import serializers


class EmpresaSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=6, max_length=16)
