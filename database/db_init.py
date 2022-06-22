import logging

from db import Base, engine

logger = logging.getLogger("db_init")


def create_table_if_ne():
    logger.debug("Creating table if not exists ....")
    Base.metadata.create_all(engine)
