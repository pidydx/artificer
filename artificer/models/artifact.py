from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    String,
    Table,
    ForeignKey
)

from sqlalchemy.orm import relationship

from .meta import Base


# Association tables
artifact_labels = Table('artifact_labels', Base.metadata,
                        Column('artifact_id', ForeignKey('artifacts.id'), primary_key=True),
                        Column('label_id', ForeignKey('labels.id'), primary_key=True)
                        )

artifact_os = Table('artifact_os', Base.metadata,
                    Column('artifact_id', ForeignKey('artifacts.id'), primary_key=True),
                    Column('os_id', ForeignKey('supported_os.id'), primary_key=True)
                    )

artifact_sources = Table('artifact_sources', Base.metadata,
                    Column('artifact_id', ForeignKey('artifacts.id'), primary_key=True),
                    Column('source_id', ForeignKey('source.id'), primary_key=True)
                    )

class Artifact(Base):
    __tablename__ = 'artifacts'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String, unique=True)
    data = Column(Text)
    author = relationship('User', back_populates='artifacts')
    labels = relationship('Label', secondary=artifact_labels, back_populates='artifacts')
    supported_os = relationship('SupportedOS', secondary=artifact_os, back_populates='artifacts')
    sources = relationship('Source', secondary=artifact_sources, back_populates='artifacts')

    def __repr__(self):
        return "%s" % self.data


class Label(Base):
    __tablename__ = 'labels'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)
    desc = Column(Text)
    artifacts = relationship('Artifact', secondary=artifact_labels, back_populates='labels')

    def __repr__(self):
        return "%s" % self.name


class SupportedOS(Base):
    __tablename__ = 'supported_os'
    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False, unique=True)
    artifacts = relationship('Artifact', secondary=artifact_os, back_populates='supported_os')

    def __repr__(self):
        return "%s" % self.name

class Source(Base):
    __tablename__ = 'source'
    id = Column(Integer, primary_key=True)
    type = Column(String(20), nullable=False, unique=True)
    artifacts = relationship('Artifact', secondary=artifact_sources, back_populates='sources')

    def __repr__(self):
        return "%s" % self.type