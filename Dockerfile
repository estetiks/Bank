# Используем официальный образ Ubuntu
FROM ubuntu:20.04

# Обновляем пакеты и устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    build-essential \
    libpq-dev \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip3 install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения в контейнер
COPY . .

# Копируем конфигурацию Nginx
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf

# Установка дополнительных зависимостей
RUN apt-get update && apt-get install -y \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка дополнительных зависимостей для Flask и SQLAlchemy
RUN pip3 install flask flask-login flask-sqlalchemy psycopg2-binary

# Экспортируем порты для Nginx и Flask
EXPOSE 80
EXPOSE 8000

# Создаем администратора
RUN python3 create_admin.py

# Запускаем Nginx и Gunicorn
CMD service nginx start && gunicorn --bind 0.0.0.0:8000 app:app
