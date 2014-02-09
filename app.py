#! engine/bin/python2.7

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import shutil
import os
import trans
import time
import hashlib
import mutagen
import mimetypes
import datetime
import models
from mutagen import File
from mutagen.mp3 import MP3
from flask import Flask, request, send_file, jsonify, Response
from flask.ext.sqlalchemy import SQLAlchemy
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
    mp3_tags = {'artist':'TPE1', 'album':'TALB', 'title':'TIT2', 'number':'TRCK', 'year':'TDOR', 'genre':'TCON'}
    cover_names = ['folder', 'cover', 'album', 'front']
    for root, dirs, files in os.walk(musicfolder):
        for file in files:
            if file.endswith('.mp3'):
                tags = mp3_tags
                track_length = int(MP3(os.path.abspath(os.path.join(root, file))).info.length)
                track_format = 'mp3'
            else:
                continue
            music_count += 1
            track = File(os.path.abspath(os.path.join(root, file)))

            if tags['artist'] in track:
                track_artist = track[tags['artist']][0]
            else:
                track_artist = 'Unknown'
            if tags['album'] in track:
                track_album = track[tags['album']][0]
            else:
                track_album = 'Unknown'
            if tags['title'] in track:
                track_title = track.tags[tags['title']][0]
            else:
                track_title = str(file.strip(".mp3"))
            if tags['number'] in track:
                track_number = track.tags[tags['number']][0]
            else:
                track_number = 'Unknown'
            if tags['year'] in track:
                track_year = track.tags[tags['year']][0]
            else:
                track_year = 'Unknown'
            if tags['genre'] in track:
                track_genre = track.tags[tags['genre']][0]
            else:
                track_genre = 'Unknown'
            track_format = str(track).split(".")[-1]
            date_added = datetime.datetime.today()
            file_location = os.path.abspath(os.path.join(root, file))

            track_hash = hashlib.md5()
            track_hash.update(track_artist + track_album + track_title)
            track_hash_string = int(track_hash.hexdigest(), 16)
            track_id = track_hash_string

            data_artwork = 'none'
            data_artwork_file = 'none'
            for cover_name in cover_names:
                for extension in ['jpg', 'jpe', 'jpeg', 'png', 'bmp']:
                    if os.path.exists(os.path.join(root, cover_name+'.'+extension)):
                        artwork = 'external'
                        external_artwork = os.path.abspath(os.path.join(root, cover_name+'.'+extension))
                        data_artwork = "found"
            if data_artwork != "found":
                try:
                    artwork = 'external'
                    artwork_data = track.tags['APIC:'].data
                    with open('artwork/' + str(track_id) + mimetypes.guess_extension(track.tags['APIC:'].mime, strict=False), 'wb') as img:
                        img.write(artwork_data)
                    external_artwork = 'artwork/' + str(track_id) + mimetypes.guess_extension(track.tags['APIC:'].mime, strict=False)
                except KeyError:
                    artwork = 'none'
                    external_artwork = False

            tracks_db = models.Tracks(track_id, track_title, track_album, track_artist, track_year, track_genre, track_format, track_length, date_added, file_location, external_artwork, artwork)
            db.session.add(tracks_db)
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
