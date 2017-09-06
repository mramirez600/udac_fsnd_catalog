import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)

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
    release_year = Column(String(8))
    album = Column(String(250))
    genre_id = Column(Integer, ForeignKey('genre.id'))
    genre = relationship(Genre)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'bio': self.bio,
            'album': self.album,
            'release_year': self.release_year,
    }




engine = create_engine('sqlite:///musicartists.db')


Base.metadata.create_all(engine)

"""
from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Genre, Artist

app = Flask(__name__)

engine = create_engine('sqlite:///musicartists.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()"""