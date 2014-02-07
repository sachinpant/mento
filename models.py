#! engine/bin/python2.7

from app import db

# privilege classes
ROLE_USER = 0
ROLE_ADMIN = 1

class Users(db.Model):
    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), index = True, unique = True)
    password = db.Column(db.String(64), index = True)
    salt = db.Column(db.String(16), index = True)
    role = db.Column(db.SmallInteger, default = ROLE_USER)

    def __repr__(self):
        return '<E-mail %r>' % (self.email)

class Artists(db.Model):
    __tablename__  = 'Artists' 

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80))

    def __repr__(self):
        return '<Artist %r>' % (self.name)

class Albums(db.Model):
    __tablename__ = 'Albums'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80))
    year = db.Column(db.Integer)
    type = db.Column(db.Integer)

    def __repr__(self):
        return '<Album %r>' % (self.name)
    
class Songs(db.Model):
    __tablename__ = 'Songs'

    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(80))
    album = db.Column(db.Integer) # this id has to be the same as the one in table Albums
    artist = db.Column(db.Integer) # this id has to be the same as the one in table Artists
    artwork = db.Column(db.String(4096)) # this id has to be the same as the one in table Artwork    

    def __repr__(self):
        return '<Song %r>' % (self.title)

class Artwork(db.Model):
    __tablename__ = 'Artwork'

    id = db.Column(db.Integer, primary_key = True)
    path = db.Column(db.String(4096))

    def __repr__(self):
        return '<Artwork %r>' % (self.path)
