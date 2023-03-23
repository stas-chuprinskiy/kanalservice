from datetime import datetime

from sqlalchemy import (Boolean, Column, Date, DateTime, Float, Integer,
                        create_engine)
from sqlalchemy.orm import declarative_base, sessionmaker

DeclarativeBase = declarative_base()


class Table(DeclarativeBase):
    """Модель объектов таблицы в БД."""

    __tablename__ = 'table'

    id = Column(Integer, primary_key=True)
    order_num = Column('order_num', Integer)
    usd_price = Column('usd_price', Float)
    supply_date = Column('supply_date', Date)
    rub_price = Column('rub_price', Float, default=None)
    creation_date = Column('creation_date', DateTime, default=datetime.now())
    last_update = Column('last_update', DateTime, default=datetime.now())
    is_deleted = Column('is_deleted', Boolean, default=False)
    is_notify = Column('is_notify', Boolean, default=False)

    def __repr__(self):
        return (f'{self.id} | {self.order_num} | {self.usd_price} | '
                f'{self.supply_date}')


def get_engine(user, password, database):
    """Получение engin'а."""
    engine = create_engine(
        f'postgresql+psycopg2://{user}:{password}@db/{database}'
    )
    create_tables(engine)
    return engine


def create_tables(engine):
    """Создание таблиц."""
    DeclarativeBase.metadata.create_all(engine)


def get_session(engine):
    """Получение сессии."""
    session = sessionmaker(bind=engine)
    return session()


def upsert_table(session, sheet_table_objects, usd_rate=None):
    """Обновление данных в таблице.

    Элементы, которые были удалены в исходной таблице, помечаются флагом
    is_deleted и фактически не удаляются.
    """
    objects_idx = []
    for sheet_table_obj in sheet_table_objects:
        db_obj = session.merge(Table(**sheet_table_obj.dict()))
        db_obj.last_update = datetime.now()
        db_obj.is_deleted = False
        db_obj.rub_price = db_obj.usd_price * usd_rate if usd_rate else None
        objects_idx.append(db_obj.id)
    query = session.query(Table).filter(Table.id.notin_(objects_idx))
    query.update({'is_deleted': True})
    session.commit()


def get_should_be_notified(session):
    """Получение объектов, для которых нужно отправить уведомление в Tlg.

    Условия отправки: дата поставки меньше текущей, объект не помечен на
    удаление, уведомление не отправлялось ранее.
    """
    query = session.query(Table).filter(
        Table.supply_date < datetime.now().date(),
        Table.is_deleted.is_(False),
        Table.is_notify.is_(False),
    )
    objects = query.all()
    query.update({'is_notify': True})
    session.commit()
    return objects
