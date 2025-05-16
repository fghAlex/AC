#!/usr/bin/env bash

# Запуск контейнера с нужными параметрами
docker run -d \
           --name mitmproxy-cont \
           -v $(pwd)/reports:/reports \
           -p 8080:8080 \
           mitmproxy:1
