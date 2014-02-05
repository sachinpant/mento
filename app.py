#! engine/bin/python2.7

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import shutil
import os
import trans
import hashlib
import mutagen
from mutagen import File
from flask import Flask, request, send_file, jsonify, Response
from flask.ext.sqlalchemy import SQLAlchemy
app = Flask(__name__)

# global variables
music_count = 0

# main app
@app.route('/')
def invalid_call():
    return 'Mento has to be accessed using REST API calls.'

@app.route('/manage/info')
def show_info():
    if os.path.exists('info.mento'):
        info_file = open('info.mento')
        for config in info_file:
            if 'music_count=' in config:
                music_count = config.split('=')[1]        
        return 'Mento configuration:<br /><br />' + "Music folder: " + musicfolder + "<br />Tracks in library: " + str(music_count) # TODO music_count should be retrieved from a file
    return 'No information file found. Make sure you ran a library refresh at least once.'

@app.route('/manage/refresh')
def refresh_library():
    print 'Refreshing library...'
    music_count = 0
    if os.path.exists('library.temp'):
        os.remove('library.temp')
    temp_library_file = open('library.temp', 'w+')
    if os.path.exists('paths.temp'):
        os.remove('paths.temp')
    temp_paths_file = open('paths.temp', 'w+')
    for root, dirs, files in os.walk(musicfolder):
        for file in files:
            if file.endswith('.mp3'):
                music_count += 1
                track = File(os.path.abspath(os.path.join(root, file)))
                track_artist = str(track.tags['TPE1']).decode('utf-8').encode('trans')
                track_album = str(track.tags['TALB']).decode('utf-8').encode('trans')
                track_title = str(track.tags['TIT2']).decode('utf-8').encode('trans')	
                track_number = str(track.tags['TRCK']).decode('utf-8').encode('trans')
                track_hash = hashlib.md5()
                track_hash.update(track_artist + track_album + track_title)
                track_hash_string = str(track_hash.hexdigest())
                track_id = track_hash_string
                temp_library_file.write(track_id + '__break__' + track_artist + '__break__' + track_album + '__break__' + track_title + '__break__' + track_number + '__new__')
                data_id = track_hash_string
                data_file = os.path.abspath(os.path.join(root, file))
                data_artwork = 'none'
                data_artwork_file = 'none'
                if os.path.exists(os.path.join(root, 'cover.jpg')):
                    data_artwork = 'external'
                    data_artwork_file = os.path.abspath(os.path.join(root, 'cover.jpg'))
                if not os.path.exists(os.path.join(root, 'cover.jpg')):
                        data_artwork = 'none'
                        data_artwork_file = 'none'
                temp_paths_file.write(data_id + '__break__' + data_file + '__break__' + data_artwork + '__break__' + data_artwork_file + '__new__')
    temp_library_file.close()
    temp_paths_file.close()
    if os.path.exists('library.mento'):
        os.remove('library.mento')
    shutil.copy2('library.temp', 'library.mento')
    if os.path.exists('paths.mento'):
        os.remove('paths.mento')
    shutil.copy2('paths.temp', 'paths.mento')
    if os.path.exists('info.mento'):
        os.remove('info.mento')
    info_file = open('info.mento', 'w+')
    info_file.write('music_count=' + str(music_count))
    info_file.close()
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
    app.config.from_pyfile('config.cfg')
    print 'Reading configuration file...'
    musicfolder = app.config['MUSICFOLDER']
    if os.path.exists('info.mento'): # TODO save it in the database
        info_file = open('info.mento')
        for config in info_file:
            if 'music_count=' in config:
                music_count = config.split('=')[1]
    print 'Starting Mento...'
    app.run(port=1337, host='0.0.0.0', debug=True)
