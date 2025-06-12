# Port Scanner

Запускаем `python -m ports {tcp|udp} {IP} {port_start} {port_end}`.

Флаг `-t` настраивает время ожидания ответа.
Если ожидания слишком низкое, протокол может
быть не обнаружен.

Есть параллельная реализация,
возможность проверки UDP-портов,
определение протокола, запущенного на порту.

## Примеры

### TCP

Google HTTP: `python -m ports tcp 172.253.63.101 75 450`.

Yandex SMTP: `python -m ports tcp 77.88.21.158 20 30 -t 2`.

### DNS

Google DNS: `python -m ports udp 8.8.8.8 50 55`.

NIST SNTP: `python -m ports udp 129.6.15.28 120 125`
