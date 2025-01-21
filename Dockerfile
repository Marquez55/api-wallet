# Utilizamos Python 3.11
FROM python:3.11

# Evitar el buffering de Python
ENV PYTHONUNBUFFERED=1

# Actualización de paquetes y configuración de locales
RUN apt-get update && \
    apt-get install -y locales && \
    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen en_US.UTF-8 && \
    apt-get clean

# Configuración de variables de entorno para locales
ENV LC_ALL=en_US.UTF-8
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en

# Crear el directorio de la aplicación dentro del contenedor
RUN mkdir /app

# Crear la carpeta para almacenar archivos de usuarios o documentos
RUN mkdir -p /repo_app/api_wallet

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar el archivo de dependencias e instalar las dependencias necesarias
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Crear el archivo de log para Django
RUN mkdir /var/log/django && \
    touch /var/log/django/api_wallet.log

# Copiar el código fuente del proyecto al directorio de trabajo
COPY . /app/

# Exponer el puerto que usa Gunicorn para servir la aplicación
EXPOSE 1022

# Comando para iniciar la aplicación con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:1022", "config.wsgi"]
