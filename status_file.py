#!/usr/bin/python3

'''
Twitch Tool. For educational purpose only.

Copyright (C) 2021 Dr. Sergey Kolevatov

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

'''

import csv            # load_status_file
import os             # save_status_file
import time           # time

##########################################################

def read_text_file( fname ):

    with open(fname) as f:
        content = f.read().splitlines()

    return content

##########################################################

def read_users( filename ):

    users = read_text_file( filename )

    print( "INFO: read {} users from {}".format( len( users ), filename ) )

    return users

##########################################################

class StreamUser:
    timestamp    = 0
    is_following = False

    def __str__(self):
        return str( self.timestamp ) + ";" + str( int( self.is_following ) )

##########################################################

def load_status_file( filename ):

    status = dict()

    with open( filename ) as csvfile:
        reader = csv.reader( csvfile, delimiter=';' )
        for row in reader:
            ( username, timestamp, is_following ) = row[0:3]
            #print( "DEBUG: {}, {}, {}".format( username, timestamp, is_following ) )
            s = StreamUser()
            s.timestamp    = timestamp
            s.is_following = bool( int ( is_following ) )
            #print( "DEBUG: s = {}".format( s ) )
            status[ username ] = s

    print( "INFO: read {} records from {}".format( len( status ), filename ) )

    return status

##########################################################

def save_status_file_direct( filename, status ):

    f = open( filename, "w" )

    i = 0

    for s in status:
        line = s + ";" + str( status[s] ) + "\n"
        f.write( line )
        i += 1

    return i

##########################################################

def save_status_file( filename, status ):

    filename_new = filename + ".new"

    size = save_status_file_direct( filename_new, status )

    filename_old = filename + ".old"

    os.rename( filename, filename_old )
    os.rename( filename_new, filename )

    print( "INFO: saved {} records to {}".format( size, filename ) )

##########################################################

def set_follow( status, username, is_following ):

    s = StreamUser()

    s.timestamp    = int( time.time() )
    s.is_following = bool( is_following )

    status[username] = s

##########################################################
