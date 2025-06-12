# POP3 Client

Поддерживает три команды: LIST, TOP, RETR

LIST: `python -m pop3 {path_to_auth} list`

TOP: `python -m pop3 {path_to_auth} top {index} {lines}`

RETR: `python -m pop3 {path_to_auth} retr {index} {outfile}`

В файле `auth.example.json` представлен пример данных для
аутентификации.