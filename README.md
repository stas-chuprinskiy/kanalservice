# Тестовое задание ООО Каналсервис

Соответствующий гугл документ [тут](https://docs.google.com/spreadsheets/d/1L2u--y05cou36Ny_CPsSvG7P0i1YbP2PEb-Rn-3xBx8/edit?usp=share_link)

Реализованный скрипт:

* Получает данные из Google документа при помощи Google API
* Обогащает данные стоимостью в рублях, конвертируя стоимость в USD по курсу ЦБ РФ
* Обновляет данные в соответствующей таблице в PostgreSQL
* Отправляет уведомления в телеграм при критических неисправностях скрипта админу
* Отправляет уведомления при проверке соблюдения «срока поставки» клиенту

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
