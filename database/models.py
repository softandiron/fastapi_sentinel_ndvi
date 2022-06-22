from db import Base
from sqlalchemy import Integer, String, Text, Column


class Footprint(Base):
    __tablename__ = "footprints"
    id = Column(String(255), primary_key=True)
    timestamp = Column(String(255), nullable=False, unique=False)
    geoJson = Column(Text, nullable=True, unique=False)

    def __repr__(self):
        return f"Footprint id={self.id}, timestamp={self.timestamp}, geoJson={self.geoJson}"
