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

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
import hashlib
import mutagen
import mimetypes
import datetime
import time
import models
from mutagen import File
from mutagen.mp3 import MP3
from flask import Flask, request, send_file, jsonify, Response
from flask.ext.sqlalchemy import SQLAlchemy
from helper import finders, cache
from library import update, remove, show
app = Flask(__name__)

# set up the config and database
app.config.from_object('config')
db = SQLAlchemy(app)

# main app
@app.route('/')
def invalid_call():
    return 'Mento has to be accessed using REST API calls.'

@app.route('/manage/info_tracks')
def show_tracks():
    #TODO this information has to be shown from the database
    return show.return_all_tracks()

@app.route('/manage/info_albums')
def show_albums():
    #TODO this information has to be shown from the database
    return show.return_all_albums()

@app.route('/manage/refresh')
def refresh_library():
    return update.full_rescan()

@app.route('/manage/remove_missing')
def remove_missing():
    return remove.delete_missing()

@app.route('/manage/remove_tracks')
def remove_tracks():
    return remove.remove_tracks()

@app.route('/manage/remove_albums')
def remove_albums():
    return remove.remove_albums()

@app.route('/user/library')
def show_library():
    if os.path.exists('library.mento'):
        return open('library.mento').read()
    return 'No library file found.'

@app.route('/user/artwork/<string:id>', methods = ['GET'])
def show_artwork(id):
    paths_file = open('paths.mento', 'r').read().split('__new__')
    for track in paths_file:
        if id in track:
            if track.split('__break__')[2] == 'external':
                return send_file(track.split('__break__')[3].decode('utf-8'))
            return 'No artwork found.'

@app.route('/user/play/<string:id>', methods = ['GET'])
def show_track(id):
    paths_file = open('paths.mento', 'r').read().split('__new__')
    for track in paths_file:
        if id in track:
            return send_file(track.split('__break__')[1].decode('utf-8'))
    return 'Unknown ID.'

@app.errorhandler(404)
def page_not_found(error):
    return 'Invalid call.'

@app.errorhandler(500)
def internal_server_error(error):
    return 'Invalid call.'

if __name__ == '__main__':
    print 'Reading configuration file...'
    if not os.path.exists('artwork'):
        os.makedirs('artwork')
    print 'Starting Mento...'
    app.run(port=1337, host='0.0.0.0', debug=True)
