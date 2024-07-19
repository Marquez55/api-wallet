import os
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.contrib.auth.models import User

from app.empresa.models import Empresa
from app.empresa.serializers import EmpresaUpdateSerializer

from app.user.models import Perfil


class EmpresaUpdateView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)

    queryset = Empresa.objects.all()
    serializer_class = EmpresaUpdateSerializer

    def put(self, request, *args, **kwargs):
        user_id = request.user.id
        perfil = Perfil.objects.get(user_id=user_id)
        empresa = Empresa.objects.get(id=perfil.empresa_id)

        new_email = request.data.get('email', None)
        if new_email:
            if User.objects.filter(email=new_email).exclude(id=user_id).exists():
                return Response({"detail": "El correo electrónico ya está en uso."}, status=status.HTTP_400_BAD_REQUEST)
            else:
                request.user.email = new_email
                request.user.save()

        serializer = self.get_serializer(empresa, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetAppURLView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        url_app = os.getenv('URL_APP')
        if not url_app:
            return Response({'detail': 'URL not found'}, status=status.HTTP_404_NOT_FOUND)

        url_app = url_app.rstrip('/')

        return Response({'url': url_app}, status=status.HTTP_200_OK)
