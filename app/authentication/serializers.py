from rest_framework import serializers

class AtuhSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=20)
    password = serializers.CharField(max_length=20)


class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=20)
    newPassword = serializers.CharField(max_length=20)
    extra_kwargs = {
        'password': {
            'write_only': True,
            'required': True,
        },
        'newPassword': {
            'write_only': True,
            'required': True,
        }
    }


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=80)
    extra_kwargs = {
        'email': {
            'write_only': True,
            'required': True,
        }
    }


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=20)
    extra_kwargs = {
        'password': {
            'write_only': True,
            'required': True,
        }
    }