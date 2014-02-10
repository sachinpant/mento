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
#import shutil
import os
#import trans
#import time
import hashlib
import mutagen
import mimetypes
import datetime
import time
import models
#from models import Tracks
#reload(models)
from mutagen import File
from mutagen.mp3 import MP3
from flask import Flask, request, send_file, jsonify, Response
from flask.ext.sqlalchemy import SQLAlchemy
from helper import finders
app = Flask(__name__)



# set up the config and database
app.config.from_object('config')
db = SQLAlchemy(app)

# global variables
music_count = 0

# main app
@app.route('/')
def invalid_call():
    return 'Mento has to be accessed using REST API calls.'

@app.route('/manage/info')
def show_info():
    #TODO this information has to be shown from the database
    print 'Stubbed.'

@app.route('/manage/refresh')
def refresh_library():
    music_count = 0
    db.create_all()
    mp3_tags = {'artist':'TPE1', 'album':'TALB', 'title':'TIT2', 'number':'TRCK', 'year':'TDOR', 'genre':'TCON'}
    cover_names = ['folder', 'cover', 'album', 'front']
    for root, dirs, files in os.walk(musicfolder):
        for file in files:
            start = time.time()
            if file.endswith('.mp3'):
                tags = mp3_tags
                try:
                    track_length = int(MP3(os.path.abspath(os.path.join(root, file))).info.length)
                except EOFError:
                    continue
                track_format = u'mp3'
            else:
                continue
            music_count += 1
            try:
                track = File(os.path.abspath(os.path.join(root, file)))
            except EOFError:
                continue

            track_artist = finders.tag_finder(track, tags['artist'])
            track_artist = finders.tag_finder(track, tags['artist'])
            track_album = finders.tag_finder(track,  tags['album'] )
            track_title = finders.tag_finder(track, tags['title'])
            if track_title == 'Unkown':
                track_title = file.split(".")[:-1][0]
            track_number = finders.tag_finder(track, tags['number'])
            track_year = finders.tag_finder(track, tags['year'])
            track_genre = finders.tag_finder(track, tags['genre'])
            date_added = datetime   .datetime.today()
            file_location = os.path.abspath(os.path.join(root, file)).decode('ISO-8859-1')

            track_hash = hashlib.md5()
            track_hash.update(track_title+track_artist+str(track_length))
            track_id = unicode(track_hash.hexdigest())

            database_query = models.Tracks.query.filter_by(id=track_id).first()
            if database_query != None:
                print "die hebben we al!"
                if database_query.file_location == file_location:
                    continue
                else:
                    database_query.file_location = file_location
                    continue

            data_artwork = 'none'
            data_artwork_file = 'none'
            for cover_name in cover_names:
                for extension in ['jpg', 'jpe', 'jpeg', 'png', 'bmp']:
                    if os.path.exists(os.path.join(root, cover_name+'.'+extension)):
                        external_artwork = True
                        artwork = unicode(os.path.abspath(os.path.join(root, cover_name+'.'+extension)))
                        data_artwork = "found"
            if data_artwork != "found":
                try:
                    external_artwork = True
                    artwork_data = track.tags['APIC:'].data
                except KeyError:
                    artwork = 'none'
                    external_artwork = False
                else:
                    mimetype = mimetypes.guess_extension(track.tags['APIC:'].mime, strict=False)
                    if mimetype == None:
                        mimetype = 'jpg'
                    with open('artwork/' + str(track_id) + mimetype, 'wb') as img:
                        img.write(artwork_data)
                    artwork = unicode('artwork/' + str(track_id) + mimetype)
            track_db = models.Tracks(track_id, track_title, track_album, track_artist, track_year, track_genre, track_format, track_length, date_added, file_location, external_artwork, artwork)
            #tracks_db = models.Tracks(track_id, track_title, track_album, track_artist, track_year, track_genre, track_format, track_length, date_added, file_location, external_artwork, artwork)
            db.session.add(track_db)
            print time.time() - start
        db.session.commit()
    db.session.commit()
    return 'Library refreshed, scanned ' + str(music_count) + ' tracks.'

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
    musicfolder = app.config['MUSICFOLDER']
    if not os.path.exists('artwork'):
        os.makedirs('artwork')
    print 'Starting Mento...'
    app.run(port=1337, host='0.0.0.0', debug=True)
