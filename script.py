import datetime
import logging
import logging.config
import os
import sys
import time
import xml.etree.ElementTree as ET

import googleapiclient.discovery
import httplib2
import requests
import telegram
from oauth2client.service_account import ServiceAccountCredentials
from pydantic import BaseModel, ValidationError, validator

from config import logger_config
from db import get_engine, get_session, get_should_be_notified, upsert_table
from exceptions import CustomError, GetSheetDataError

logger = logging.getLogger('script')

USER = os.getenv('POSTGRES_USER')
PASSWORD = os.getenv('POSTGRES_PASSWORD')
DATABASE = os.getenv('POSTGRES_DB')

TLG_BOT_TOKEN = os.getenv('TLG_BOT_TOKEN')
TLG_ADMIN_ID = os.getenv('TLG_ADMIN_ID')
TLG_CLIENT_ID = os.getenv('TLG_CLIENT_ID')

CREDENTIALS_FILE = 'creds.json'
SPREADSHEET_ID = '1L2u--y05cou36Ny_CPsSvG7P0i1YbP2PEb-Rn-3xBx8'
CB_RATES_ENDPOINT = 'https://www.cbr.ru/scripts/XML_daily.asp'
RETRY_TIME = 60


class SheetTable(BaseModel):
    """Базовый класс для объектов таблицы."""

    id: int
    order_num: int
    usd_price: float
    supply_date: datetime.date

    @validator('supply_date', pre=True)
    def parse_supply_date(cls, value):
        return datetime.datetime.strptime(value, '%d.%m.%Y').date()


def get_sheet_data(service):
    """Получение данных о таблице с записями."""
    try:
        sheet_data = service.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='A:D',
            majorDimension='ROWS'
        ).execute()
    except Exception:
        raise GetSheetDataError('Sth went wrong while getting sheet data')
    else:
        return sheet_data


def get_sheet_table_objects(sheet_table):
    """Преобразование сырых записей в таблице в объекты."""
    sheet_table_objects = []
    for row in sheet_table:
        try:
            sheet_table_obj = SheetTable(id=row[0], order_num=row[1],
                                         usd_price=row[2], supply_date=row[3])
        except ValidationError:
            logger.error(f'ValidationError while convert {row} to SheetTable',
                         exc_info=True)
        else:
            sheet_table_objects.append(sheet_table_obj)
    return sheet_table_objects


def get_usd_rate(url=CB_RATES_ENDPOINT):
    """Получение курса USD ЦБ на текущую дату."""
    try:
        response = requests.get(url)
        response.raise_for_status()

        currencies = ET.fromstring(response.text)

        usd_obj = list(filter(lambda x: x.get('ID') == 'R01235', currencies))
        usd_rate = usd_obj[0].find('Value').text
        usd_rate = float(usd_rate.replace(',', '.'))
    except requests.RequestException:
        logger.error(f'RequestException while calling Central Bank API '
                     f'endpoint {url}', exc_info=True)
    except Exception:
        logger.error(f'Error while parsing usd_rate from {url}',
                     exc_info=True)
    else:
        return usd_rate


def send_tlg_message(bot, chat_id, text):
    """Отправка сообщения в Telegram."""
    try:
        bot.send_message(chat_id=chat_id, text=text)
    except telegram.error.TelegramError:
        logger.error('Error while sending telegram message', exc_info=True)


def main():
    logging.config.dictConfig(logger_config)

    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        CREDENTIALS_FILE,
        ['https://www.googleapis.com/auth/drive',
         'https://www.googleapis.com/auth/spreadsheets'],
    )
    http_аuth = credentials.authorize(httplib2.Http())
    service = googleapiclient.discovery.build('sheets', 'v4', http=http_аuth)
    engine = get_engine(USER, PASSWORD, DATABASE)
    db_session = get_session(engine)
    bot = telegram.Bot(token=TLG_BOT_TOKEN)

    while True:
        try:
            logger.info('New update cycle')

            sheet_data = get_sheet_data(service)
            # получение строк таблицы без заголовка
            sheet_table = sheet_data.get('values')[1:]
            sheet_table_objects = get_sheet_table_objects(sheet_table)

            usd_rate = get_usd_rate()
            upsert_table(db_session, sheet_table_objects, usd_rate)

            objects = get_should_be_notified(db_session)
            if objects:
                for obj in objects:
                    send_tlg_message(bot, TLG_CLIENT_ID, str(obj))
        except CustomError as err:
            text = f'Script error: {err}'
            send_tlg_message(bot, TLG_ADMIN_ID, text)
            logger.error(err, exc_info=True)
        except Exception as err:
            text = f'Unexpected error, script was stopped: {err}'
            send_tlg_message(bot, TLG_ADMIN_ID, text)
            logger.critical(err, exc_info=True)
            sys.exit()
        finally:
            logger.info('Update cycle finished')
            time.sleep(RETRY_TIME)


if __name__ == "__main__":
    main()
