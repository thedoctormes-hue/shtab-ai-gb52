#!/bin/bash
# port_scanner.sh — Быстрый тест портов на RF Proxy (89.169.4.51)
# Запуск: bash port_scanner.sh

TARGET="89.169.4.51"
START_PORT=1
END_PORT=10000
TIMEOUT=1

echo "Сканируем $TARGET с $START_PORT по $END_PORT..."
echo "Результаты (OPEN порты):"

for port in $(seq $START_PORT $END_PORT); do
    timeout $TIMEOUT bash -c "echo test > /dev/tcp/$TARGET/$port" 2>/dev/null && echo "Port $port: OPEN"
done

echo "Готово! Для теста из РФ запусти этот же скрипт с мобильного/ПК в РФ."
