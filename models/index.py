from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy.types import Boolean, Date, DateTime, Float, Integer, Text, Time, Interval

db = SQLAlchemy()

class Content(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	code_list = db.Column(db.String(10))
	filling_date = db.Column(db.DateTime(timezone=False), default=func.now())
	trade_date = db.Column(db.Date(), default=func.now())
	ticker = db.Column(db.String(10))
	company_name = db.Column(db.String(100))
	insider_name = db.Column(db.String(100))
	title = db.Column(db.String(100))
	trade_type = db.Column(db.String(100))
	price = db.Column(db.String(100))
	qty = db.Column(db.String(100))
	owned = db.Column(db.String(100))
	own = db.Column(db.String(100))
	value = db.Column(db.String(100))
	_1d = db.Column(db.String(10))
	_1w = db.Column(db.String(10))
	_1m = db.Column(db.String(10))
	_6m = db.Column(db.String(10))

class Separate(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	code_list = db.Column(db.String(10))
	filling_date = db.Column(db.DateTime(timezone=False), default=func.now())
	trade_date = db.Column(db.Date(), default=func.now())
	ticker = db.Column(db.String(10))
	company_name = db.Column(db.String(100))
	insider_name = db.Column(db.String(100))
	title = db.Column(db.String(100))
	trade_type = db.Column(db.String(100))
	price = db.Column(db.String(100))
	qty = db.Column(db.String(100))
	owned = db.Column(db.String(100))
	own = db.Column(db.String(100))
	value = db.Column(db.String(100))
