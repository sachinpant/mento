#! engine/bin/python2.7

#This file is part of Mento.

#Mento is a web app for playing music from your computer and
#the computers of your friends that creates useful API's for other programs to hook in on.
#Copyright (C) 2014

#Mento is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#Mento is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from flask import Flask, request, send_file, jsonify, Response
from flask.ext.sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)
# set up the config and database
app.config.from_object('config')
musicfolder = app.config['MUSICFOLDER']
db = SQLAlchemy(app)

class Finders:
    def tag_finder(self, track, tag):
        if tag in track:
            return unicode(track.tags[tag][0])
        else:
            return u"Unkown"

class Cache:
    def tracks(self, currunt_cache):
        if currunt_cache[0] - time.time() > 86400:
            return [time.time()]
        else:
            print "cache is good!"
            return currunt_cache

class SwitchCase:
    def upper(self, a):
        return a.upper()

    def lower(self, a):
        return a.lower()

    def title(self, a):
        return a.title()

    def to_str(self, a):
        return a

switchcase = SwitchCase()
cache = Cache()
finders = Finders()
