#! engine/bin/python2.7

import sys
import os
import json
import trans
import hashlib
from mutagen import File
from flask import Flask, request, send_file, jsonify
app = Flask(__name__)

# global variables
music_count = 0
music_library = []

# main app
@app.route('/')
def invalid_call():
    return 'Mento has to be accessed using REST API calls.'

@app.route('/manage/info')
def show_info():
    return 'Mento configuration:<br /><br />' + "Music folder: " + musicfolder + "<br />Tracks in library: " + str(music_count) # TODO music_count should be retrieved from a file

@app.route('/manage/refresh')
def refresh_library():
    print 'Refreshing library...'
    music_count = 0
    for root, dirs, files in os.walk(musicfolder):
        for file in files:
            if file.endswith('.mp3'):
                music_count += 1
                track = File(os.path.abspath(os.path.join(root, file)))
                info = {}
                info['artist'] = str(track.tags['TPE1']).decode('utf-8').encode('trans')
                info['album'] = str(track.tags['TALB']).decode('utf-8').encode('trans')
                info['title'] = str(track.tags['TIT2']).decode('utf-8').encode('trans')	
                track_hash = hashlib.md5()
                track_hash.update(info['artist'] + info['album'] + info['title'])
                info['id'] = str(track_hash.hexdigest())
                music_library.append(info)
    if os.path.exists('library.json'):
        os.remove('library.json')
    library_file = open('library.json', 'w+')
    library_file.write(str(json.dumps(music_library, indent = 4)))
    library_file.close()
    return 'Library refreshed, scanned ' + str(music_count) + ' tracks.' # TODO save this to a file

@app.route('/library')
def show_library():
    if os.path.exists('library.json'):
        return send_file('library.json')
    return 'No library file found.'

# TODO remove this stub routing
@app.route('/test')
def test_file():
    return send_file('/home/pi/hdd/file.mp3')

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
    print 'Starting Mento...'
    app.run(port=1337, host='0.0.0.0', debug=True)
