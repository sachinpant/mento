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

import os
import hashlib
import mutagen
import mimetypes
import datetime
import time
import models
from mutagen import File
from mutagen.mp3 import MP3
from flask.ext.sqlalchemy import SQLAlchemy
from helper import db, app, musicfolder, switchcase, finders, cache

# Global variables
music_count = 0
simple_cache_tracks = [time.time()]

class Update:
    def full_rescan(self, use_cache=True):
        global simple_cache_tracks
        music_count = 0
        cache_hit = 0
        tracks_added = 0
        path_updated = 0
        db.create_all()
        if use_cache == False:
            simple_cache_tracks = [time.time()]
        elif use_cache == True:
            simple_cache_tracks = cache.tracks(simple_cache_tracks)
        mp3_tags = {'artist':'TPE1', 'album':'TALB', 'title':'TIT2', 'number':'TRCK', 'year':'TDOR', 'genre':'TCON'}
        cover_names = ['folder', 'cover', 'album', 'front']
        start = time.time()
        for root, dirs, files in os.walk(musicfolder):
            for file in files:
                if file.endswith('.mp3'):
                    tags = mp3_tags
                if not file.endswith('.mp3'):
                    continue
                music_count += 1

                file_location = os.path.abspath(os.path.join(root, file)).decode('ISO-8859-1')
                track_cache_id = (file_location)

                if track_cache_id in simple_cache_tracks:
                    cache_hit += 1
                    continue

                try:
                    track = File(os.path.abspath(os.path.join(root, file)))
                except EOFError:
                    simple_cache_tracks.append(track_cache_id)
                    continue
                track_artist = finders.tag_finder(track, tags['artist'])
                track_artist = finders.tag_finder(track, tags['artist'])
                track_title = finders.tag_finder(track, tags['title'])
                if track_title == 'Unkown':
                    track_title = file.split(".")[:-1][0]

                if file.endswith('.mp3'):
                    track_length = int(MP3(os.path.abspath(os.path.join(root, file))).info.length)
                    track_format = u'mp3'

                track_album = finders.tag_finder(track,  tags['album'] )
                track_number = finders.tag_finder(track, tags['number'])
                track_year = finders.tag_finder(track, tags['year'])
                track_genre = finders.tag_finder(track, tags['genre'])
                date_added = datetime.datetime.today()

                track_hash = hashlib.md5()
                track_hash.update(track_title+track_artist+str(track_length))
                track_id = unicode(track_hash.hexdigest())

                if track_cache_id not in simple_cache_tracks:
                    simple_cache_tracks.append(track_cache_id)
                    database_query = models.Tracks.query.get(track_id)
                    if database_query != None:
                        if database_query.file_location == file_location:
                            continue
                        else:
                            simple_cache_tracks.remove(database_query.file_location)
                            path_updated += 1
                            database_query.file_location = file_location
                            continue

                data_artwork = 'none'
                data_artwork_file = 'none'
                for cover_name in cover_names:
                    cases = {1:switchcase.upper, 2:switchcase.lower, 3:switchcase.to_str, 4:switchcase.title}
                    for case in cases:
                        cover_name_in_use = cases[case](cover_name)
                        for extension in ['jpg', 'jpe', 'jpeg', 'png', 'bmp']:
                            if os.path.exists(os.path.join(root, cover_name_in_use+'.'+extension)):
                                external_artwork = True
                                artwork = unicode(os.path.abspath(os.path.join(root, cover_name_in_use+'.'+extension)))
                                data_artwork = "found"
                                continue
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
                db.session.add(track_db)
                tracks_added += 1
            db.session.commit()
        db.session.commit()
        return 'Library refreshed, scanned ' + str(music_count) + ' tracks, we hit the cache ' + str(cache_hit) + ' times. It took ' + str(time.time() - start) + ' seconds. In total ' + str(tracks_added) + ' tracks were added. We updated the path for ' + str(path_updated) + ' file(s)'

class Remove:
    def delete_missing(self):
        all_tracks = models.Tracks.query.all()
        good_paths = 0
        bad_paths = 0
        for track in all_tracks:
            if os.path.exists(track.file_location.encode('ISO-8859-1')) == True:
                good_paths += 1
            else:
                bad_paths += 1
                print track.file_location
                db.session.delete(track)
        db.session.commit()
        return "Of a total of %s tracks %s had a bad path, they have been deleted" %(str(good_paths + bad_paths), bad_paths)

update = Update()
remove = Remove()
