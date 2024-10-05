# Используем официальный образ Nginx
FROM nginx:latest

# Копируем конфигурацию Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Копируем статические файлы
COPY ../app/static /usr/share/nginx/html/static

# Экспортируем порт 80
EXPOSE 80

# Запускаем Nginx
CMD ["nginx", "-g", "daemon off;"]
