# Тестовое задание ООО Каналсервис

Соответствующий гугл документ [тут](https://docs.google.com/spreadsheets/d/1L2u--y05cou36Ny_CPsSvG7P0i1YbP2PEb-Rn-3xBx8/edit?usp=share_link)

Реализованный скрипт:

* Получает данные из Google документа при помощи Google API
* Обогащает данные стоимостью в рублях, конвертируя стоимость в USD по курсу ЦБ РФ
* Обновляет данные в соответствующей таблице в PostgreSQL
* Отправляет уведомления в телеграм при критических неисправностях скрипта админу
* Отправляет уведомления при проверке соблюдения «срока поставки» клиенту

### Структура проекта

- **script.py** - основной файл скрипта
- **db.py** - функции для работы с базой данных
- **exceptions.py** - кастомные исключения
- **config.py** - конфиг
- **requirements.txt** - зависимости

- **creds.json** и **.env** - секреты для работы скрипта
> Намеренно оставлены в публичном доступе дабы не утруждать проверяющих добавлением соответствующих данных вручную

- **Dockerfile** и **docker-compose.yml** - инфраструктура для развертывания в `Docker`

### Технологии

google-api-python-client==2.82.0
httplib2==0.22.0
oauth2client==4.1.3
pydantic==1.10.6
requests==2.28.2
python-telegram-bot==13.7
SQLAlchemy==2.0.7
psycopg2-binary==2.9.5

### Установка

> Для развертывания и тестирования проекта необходимо установить [docker](https://docs.docker.com/engine/install/) и [docker-compose](https://docs.docker.com/compose/install/other/)

- Клонируйте репозиторий и перейдите в папку проекта:
```
git clone <link>

cd kanalservice/
```

- Выполните сборку проекта:
```
docker-compose up -d
```

### Использование

Для удобства проверки вместе с `PostgreSQL` запускается веб-клиент `Adminer`, доступный по адресу **localhost:8080**:

```
# Данные для авторизации Adminer (localhost:8080)

Движок: PostgreSQL
Сервер: db
Имя пользователя: kanalservice_user
Пароль: NJb5xK8PPkpDqVg9Rrfm
База данных: kanalservice_db
```

Для получения уведомлений в Telegram необходимо в `.env` файле указать свои `TLG_ADMIN_ID` и `TLG_CLIENT_ID`, запустить [бота]( http://t.me/test_kanalservice_chupss_bot) и перезапустить скрипт:

```
docker-compose stop

docker-compose up --build -d
```

Частотой обновлений (в секундах) можно управлять с помощью константы `RETRY_TIME` в файле `script.py`.

### Автор

*Чупринский Станислав*
