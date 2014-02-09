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
import models
from mutagen import File
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
    for root, dirs, files in os.walk(musicfolder):
        for file in files:
            if file.endswith('.mp3'):
                music_count += 1

                track = File(os.path.abspath(os.path.join(root, file)))

                try:
                    track_artist = str(track.tags['TPE1']).decode('utf-8').encode('trans')
                except:
                    track_artist = 'Unknown'
                try:
                    track_album = str(track.tags['TALB']).decode('utf-8').encode('trans')
                except:
                    track_album = 'Unknown'
                try:
                    track_title = str(track.tags['TIT2']).decode('utf-8').encode('trans')
                except:
                    track_title = str(file.strip(".mp3"))
                try:
                    track_number = str(track.tags['TRCK']).decode('utf-8').encode('trans')
                except:
                    track_number = 'Unknown'
                try:
                    track_year = str(track.tags['TDOR']).decode('utf-8').encode('trans')
                except:
                    track_year = 'Unknown'
                try:
                    track_genre = 'Undefined' # TODO there is no ID3 tag for genre
                except:
                    track_genre = 'Unknown'
                track_format = str(track).split(".")[-1]
                try:
                    track_length = str(MP3(track).info.length)
                except:
                    track_length  = 'Unknown'
                date_added = time.strftime("%H:%M:%S")
                file_location = os.path.abspath(os.path.join(root, file))

                track_hash = hashlib.md5()
                track_hash.update(track_artist + track_album + track_title)
                track_hash_string = int(track_hash.hexdigest(), 16)
                track_id = track_hash_string

                data_artwork = 'none'
                data_artwork_file = 'none'
                if os.path.exists(os.path.join(root, 'cover.jpg')):
                    artwork = 'external'
                    external_artwork = os.path.abspath(os.path.join(root, 'cover.jpg'))
                if not os.path.exists(os.path.join(root, 'cover.jpg')):
                        try:
                            artwork = 'external'
                            artwork_data = track.tags['APIC:'].data
                            with open('artwork/' + track_id + '.jpg', 'wb') as img:
                                img.write(artwork_data)
                            external_artwork = 'artwork/' + track_id + '.jpg'
                        except:
                            artwork = 'none'
                            external_artwork = 'none'

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
