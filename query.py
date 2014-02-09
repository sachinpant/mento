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

from models import Users, Roles, Artists, Albums, Artwork, Tracks, Playlist, Playlist_data

def songs_from_playlist(playlist_id, start_return=0, end_return=0):
    """
    This function returns a list of songs from a playlist.
    The number of songs it returns is specified in start_return and and end_return, standard both are 0 which means all songs.
    """

    """ Get all the element_ids that belong to this playlist """
    elements = Playlist_data.query.filter_by(playlist_id=playlist_id).get_or_404(number_return)

    """ Define an empty list en iterate over the elements and check if they are albums or tracks and put the track id in the empty list.
    If a range is specified we start end at end_return"""
    tracks = []
    if start_return == 0 and end_return == 0:
        for element in elements:
            if element.object_type == "track":
                tracks.append(element.object_id)
            else:
                tracks_in_album = Tracks.query.filter_by(album=element.object_id).all()
                for track_in_album in tracks_in_album:
                    tracks.append(track_in_album.id)
        return tracks
    else:
        while len(tracks)-start_retrun < end_return
            for element in elements:
                if element.object_type == "track":
                    tracks.append(element.object_id)
                else:
                    tracks_in_album = Tracks.query.filter_by(album=element.object_id).all()
                    for track_in_album in tracks_in_album:
                        tracks.append(track_in_album.id)
        return tracks[start_return:end_return]
