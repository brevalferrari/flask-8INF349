# -*- coding: utf-8 -*-
from peewee import SqliteDatabase
from .config import DefaultConfig

db = SqliteDatabase(DefaultConfig.DATABASE_URI)
