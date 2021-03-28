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

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import staleness_of
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

import sys, getopt
import config         # DRIVER_PATH
import credentials    # LOGIN
import helpers        # find_element_by_tag_and_class_name
import loginer        # login
#import product_parser # parse_product
import re
import time
import csv            # read_status_file
import os             # save_status_file

from datetime import datetime

DEBUG_CATEGORY = False

##########################################################

def harmonize_link( link ):

    if link.endswith('/'):
        return link

    return link + '/'

##########################################################

def has_unfollow_button( driver ):

    paths = [
"/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[2]/div[1]/div/div[1]/div/div/div[1]/div/div/div/div/button",
"/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[2]/div[1]/div/div/div/div/div[1]/div/div/div/div/button"
]
    result = helpers.do_xpaths_exist_with_timeout( driver, paths, 10 )

    if result[0] == False:
        print( "ERROR: cannot find follow/unfollow button" )
        return False

    button = driver.find_element_by_xpath( result[1] )

    attr = button.get_attribute( "data-a-target" )

    if attr == "unfollow-button":
        return True

    return False

##########################################################

def click_follow_user( driver ):

    paths = [
"/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[2]/div[1]/div/div[1]/div/div/div[1]/div/div/div/div/button",
"/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div[1]/div[1]/div[2]/div/div[2]/div[1]/div[2]/div[1]/div/div/div/div/div[1]/div/div/div/div/button"
]
    result = helpers.do_xpaths_exist_with_timeout( driver, paths, 10 )

    if result[0] == False:
        print( "ERROR: cannot find follow button" )
        return False

    #print( "DEBUG: found element link {}".format( result[2] ) )

    print( "INFO: clicked follow button" )

    button = driver.find_element_by_xpath( result[1] )

    button.click()

    return True

##########################################################

def follow_user( driver, f, user ):

    link = "https://www.twitch.tv/" + user

    driver.get( link )

    if has_unfollow_button( driver ):
        print( "WARNING: user {} is already followed".format( user ) )
        return

    creation_time = int( time.time() )

    has_followed = False

    if( click_follow_user( driver ) ):
        if has_unfollow_button( driver ):
            has_followed = True

    line = user + ';' + str( creation_time ) + ';' + str( int( has_followed ) ) + "\n"

    f.write( line )

##########################################################

def follow_users( driver, f, users ):

    num_users = len( users )

    i = 0

    for u in users:

        i += 1

        print( "INFO: following user {} / {} - {}".format( i, num_users, u ) )

        follow_user( driver, f, u )

##########################################################

def generate_filename():
    now = datetime.now()
    d1 = now.strftime( "%Y%m%d_%H%M" )
    res = "users_" + d1 + ".csv"
    return res

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

def read_status_file( filename ):

    status = dict()

    with open( filename ) as csvfile:
        reader = csv.reader( csvfile, delimiter=';' )
        for row in reader:
            ( username, timestamp, is_following ) = row[0:3]
            #print( "DEBUG: {}, {}, {}".format( username, timestamp, is_following ) )
            s = StreamUser()
            s.timestamp    = timestamp
            s.is_following = bool( is_following )
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

def determine_notfollowed_users( status, users_list ):

    res = []

    for u in users_list:
        if u in status:
            if status[u].is_following == False:
                res.append( u )
        else:
            res.append( u )

    return res

##########################################################

def process( user_file, status_file ):

    users_all = read_users( user_file )

    status = read_status_file( status_file )

    save_status_file( "xxx", status )

    users = determine_notfollowed_users( status, users_all )

    print( "INFO: total users - {}, still to follow - {}, already followed - {}".format( len( users_all), len( users ), len( users_all) - len( users ) ) )

    quit()

    driver = helpers.init_driver( config.DRIVER_PATH, config.BROWSER_BINARY, harmonize_link( config.COOKIES_DIR ) + credentials.LOGIN )

    loginer.login( driver, credentials.LOGIN, credentials.PASSWORD )

    f = open( generate_filename(), "w" )

    follow_users( driver, f, users )

    print( "INFO: done" )

##########################################################

def main( argv ):

    user_file = None
    status_file = None

    outputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:s:",["ifile=","ofile=","status="])
    except getopt.GetoptError:
        print( 'follower.py -i <inputfile> -o <outputfile> -s <userfile>' )
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print( 'follower.py -i <inputfile> -o <outputfile> -s <userfile>' )
            sys.exit()
        elif opt in ("-i", "--ifile"):
            user_file = arg
        elif opt in ("-s", "--status"):
            status_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg

    print ( "DEBUG: input file  = {}".format( user_file ) )
    print ( "DEBUG: status file = {}".format( status_file ) )
    print ( "DEBUG: output file = {}".format( outputfile ) )

    if not user_file:
        print( "FATAL: user file is not given" )
        quit()

    if not status_file:
        print( "FATAL: status file is not given" )
        quit()

    process( user_file, status_file )

##########################################################

if __name__ == "__main__":
   main( sys.argv[1:] )
