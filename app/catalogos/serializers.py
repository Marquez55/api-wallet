from rest_framework import serializers
from app.catalogos.models import AnioUsuario, Categoria, Subcategoria
import datetime


class AnioUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnioUsuario
        fields = ['id', 'anio', 'activo']

    def validate_anio(self, value):
        """
        Valida que el año:
        - No sea menor al último año creado por el usuario.
        - No esté ya registrado para el usuario actual.
        """
        usuario = self.context['request'].user

        # Validar duplicado
        if AnioUsuario.objects.filter(usuario=usuario, anio=value).exists():
            raise serializers.ValidationError("Este año ya está registrado para el usuario actual.")

        # Obtener el año máximo creado por el usuario
        ultimo_anio = AnioUsuario.objects.filter(usuario=usuario).order_by('-anio').first()

        if ultimo_anio and value < ultimo_anio.anio:
            raise serializers.ValidationError(
                f"No se pueden crear años menores al último registrado ({ultimo_anio.anio})."
            )

        return value



class SubcategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategoria
        fields = ['id', 'nombre', 'favorito', 'categoria']
        read_only_fields = ['id', 'categoria', 'usuario']  # 'categoria' ahora es de solo lectura

    def create(self, validated_data):
        # El campo 'categoria' se asignará desde la vista
        usuario = self.context['request'].user
        categoria = self.context.get('categoria')
        subcategoria = Subcategoria.objects.create(
            usuario=usuario,
            categoria=categoria,
            **validated_data
        )
        return subcategoria

class CategoriaSerializer(serializers.ModelSerializer):
    subcategorias = SubcategoriaSerializer(many=True, read_only=True)

    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'favorito', 'activo', 'subcategorias']