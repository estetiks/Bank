# Используем официальный образ Ubuntu
FROM ubuntu:20.04

ENV TZ=Etc/UTC

RUN ln -sf /usr/share/zoneinfo/Etc/UTC /etc/localtime && echo "Etc/UTC" > /etc/timezone

# Обновляем пакеты и устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл с зависимостями
COPY requirements.txt .

# Устанавливаем Python-зависимости
RUN pip3 install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения в контейнер
COPY . .

# Установка дополнительных зависимостей
RUN apt-get update && apt-get install -y \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Установка дополнительных зависимостей для Flask и SQLAlchemy
RUN pip3 install flask flask-login flask-sqlalchemy psycopg2-binary

# Экспортируем порт для Flask
EXPOSE 8000

# Создаем администратора
# RUN python3 create_admin.py

# Запускаем Gunicorn
CMD gunicorn --bind 0.0.0.0:8000 app:app
