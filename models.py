from flask import Flask
from flask_sqlalchemy import SQLAlchemy


server = Flask(__name__)
server.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
server.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(server)


class Animal(db.Model):
    __tablename__ = 'animals'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    card = db.Column(db.String(255), nullable=False)
    animal = db.Column(db.String(255), nullable=False)
    year = db.Column(db.String(255), nullable=False)
    weight = db.Column(db.String(255), nullable=False)
    male = db.Column(db.String(255), nullable=False)
    breed = db.Column(db.String(255), nullable=False)
    color = db.Column(db.String(255), nullable=False)
    swool = db.Column(db.String(255), nullable=False)
    ear = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    is_social = db.Column(db.String(255), nullable=False)
    def __repr__(self):
        return f'{self.name}'