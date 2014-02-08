#! engine/bin/python2.7

from app import db

# privilege classes
ROLE_USER = 0
ROLE_ADMIN = 1

class Users(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(120), index = True, unique = True)
    password = db.Column(db.String(128), index = True)
    salt = db.Column(db.String(128), index = True)
    last_login = db.Column(db.DateTime)
    activated = db.Column(db.Boolean)
    create_date = db.Column(db.DateTime)
    role = db.Column(db.String(32), default = "USER")

    def __repr__(self):
        return '<E-mail %r>' % (self.email)

class Roles(db.Model):
    role_uid = db.Column(db.Integer, primary_key = True)
    role_name = db.Column(db.String(32), index = True)

class Artists(db.Model):
    __tablename__  = 'artists'

    id = db.Column(db.Integer, index = True, primary_key = True)
    name = db.Column(db.String(80))

    def __repr__(self):
        return '<Artist %r>' % (self.name)

class Albums(db.Model):
    __tablename__ = 'albums'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(80))
    year = db.Column(db.Integer)
    type = db.Column(db.String(80), index = True)
    album_artist = db.Column(db.String(80))
    rating = db.Column(db.Integer)
    genre = db.Column(db.String(80))

    def __repr__(self):
        return '<Album %r>' % (self.name)

class Artwork(db.Model):
    __tablename__ = 'artwork'

    id = db.Column(db.Integer, primary_key = True, index = True)
    path = db.Column(db.String(4096))

    def __repr__(self):
        return '<Artwork %r>' % (self.path)

class Tracks(db.Model):
    __tablename__ = 'tracks'

    id = db.Column(db.Integer, index = True, primary_key = True)
    title = db.Column(db.String(80))
    album = db.Column(db.Integer, db.ForeignKey(Albums.id))
    artist = db.Column(db.Integer, db.ForeignKey(Artists.id))
    year = db.Column(db.Integer)
    genre = db.Column(db.String(80))
    format = db.Column(db.String(32))
    length = db.Column(db.Integer)
    date_added = db.Column(db.DateTime)
    date_played = db.Column(db.DateTime)
    last_played = db.Column(db.Integer)
    file_location = db.Column(db.String(4096))
    external_artwork = db.Column(db.Boolean)
    artwork = db.Column(db.Integer, db.ForeignKey(Artwork.id))

    def __repr__(self):
        return '<Song %r>' % (self.title)

class Playlist(db.Model):
    __tablename__ = 'playlist'

    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(255), index = True)
    user_id = db.Column(db.Integer)
    type = db.Column(db.Enum(u'private', u'public'))
    date_added = db.Column(db.DateTime)

    def __repr__(self):
        return '<Name %r>' % (self.name)

class Playlist_data(db.Model):
    __tablename__ = 'playlists_data'

    playlist_id = db.Column(db.ForeignKey(Playlist.id), primary_key = True, index = True)
    object_id = db.Column(db.Integer)
    object_type = db.Column(db.Enum(u'track', u'album'))
