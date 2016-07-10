from sqlalchemy import (
    Column,
    Index,
    Integer,
    String
)

from sqlalchemy.orm import relationship

from .meta import Base


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    password = Column(String)
    artifacts = relationship('Artifact', back_populates='author', lazy='dynamic')

    def __repr__(self):
        return "<User(name='%s', fullname='%s', password='%s')>" % (
            self.name, self.fullname, self.password)
