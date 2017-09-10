import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class Artist(Base):
    __tablename__ = 'artist'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    bio = Column(String(250))
    wikiLink = Column(String(250))
    release_year = Column(String(8))
    album = Column(String(250))
    albumImg = Column(String(250))
    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'bio': self.bio,
            'album': self.album,
            'release_year': self.release_year,
            'albumImg': self.albumImg,
            'wikiLink': self.wikiLink,
            }


engine = create_engine('postgresql://grader:default@localhost/catalog')


Base.metadata.create_all(engine)
