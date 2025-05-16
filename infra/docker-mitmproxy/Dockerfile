# Базовый образ Ubuntu
FROM ubuntu:latest AS build-stage

# Обновляем систему и устанавливаем нужные пакеты НЕИНТЕРАКТИВНО
RUN DEBIAN_FRONTEND=noninteractive apt-get update \
    && apt-get install -y mitmproxy

# Создание рабочей директории для отчетов
WORKDIR /reports
VOLUME ["/reports"]

# Настройка команд для запуска контейнера
CMD ["mitmdump", "-q", "-w", "output_file", "-p", "8080", "--set", "stream_large_bodies=0"]
