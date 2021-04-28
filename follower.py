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
from selenium.common.exceptions import NoSuchWindowException, WebDriverException

import sys, getopt
import config         # DRIVER_PATH
import helpers        # find_element_by_tag_and_class_name
import loginer        # login
import status_file    # status_file
import configparser   # load_credentials
import re
from print_helpers import print_fatal, print_error, print_warning, print_info, print_debug

from datetime import datetime

DEBUG_CATEGORY = False

##########################################################

MODE_FOLLOW = 0
MODE_UNFOLLOW = 1
MODE_FOLLOW_UNFOLLOW = 2
MODE_REFOLLOW = 3

##########################################################

def harmonize_link( link ):

    if link.endswith('/'):
        return link

    return link + '/'

##########################################################

def has_follow_or_unfollow_button( driver, need_unfollow ):

    path = None

    if need_unfollow:
        path = "//button[@data-a-target='unfollow-button']";
    else:
        path = "//button[@data-a-target='follow-button']";

    return helpers.does_xpath_exist_with_timeout( driver, path, 10 )

##########################################################

def has_follow_button( driver ):

    return has_follow_or_unfollow_button( driver, False )

##########################################################

def has_unfollow_button( driver ):

    return has_follow_or_unfollow_button( driver, True )

##########################################################

BTN_NONE = 0
BTN_FOLLOW = 1
BTN_UNFOLLOW = 2

##########################################################

def detect_follow_unfollow_button( driver ):

    b1 = has_follow_button( driver )
    b2 = has_unfollow_button( driver )

    print_debug( "has_follow = {}, has_unfollow = {}".format( b1, b2 ) )

    if not b1 and b2:
        print_debug( "found UNFOLLOW button" )
        return BTN_UNFOLLOW
    elif b1 and not b2:
        print_debug( "found FOLLOW button" )
        return BTN_FOLLOW
    elif b1 and b2:
        print_error( "found FOLLOW and UNFOLLOW buttons" )
        return BTN_NONE
    else:
        print_error( "cannot find follow/unfollow button" )

    return BTN_NONE

##########################################################

def click_follow_user( driver ):

    paths = [
"//button[@data-a-target='follow-button']",
"//button[@data-a-target='unfollow-button']"
]
    result = helpers.do_xpaths_exist_with_timeout( driver, paths, 10 )

    if result[0] == False:
        print_error( "cannot find follow button" )
        return False

    print_debug( "found element link {}".format( result[2] ) )

    button = driver.find_element_by_xpath( result[1] )

    helpers.wait_till_clickable_and_click( button, 10 )

    print_info( "clicked follow button" )

    return True

##########################################################

def click_modal_unfollow_user( driver ):

    paths = [
"//button[contains(@data-a-target,'modal-unfollow-button')]"

]
    result = helpers.do_xpaths_exist_with_timeout( driver, paths, 10 )

    if result[0] == False:
        print_error( "cannot find modal unfollow button" )
        return False

    #print_debug( "found element link {}".format( result[2] ) )

    print_debug( "clicked modal unfollow button" )

    button = driver.find_element_by_xpath( result[1] )

    helpers.wait_till_clickable_and_click( button, 10 )

    return True

##########################################################

def follow_user_core( driver, username ):

    b1 = detect_follow_unfollow_button( driver )

    if b1 == BTN_UNFOLLOW:
        print_warning( "user {} is already followed".format( username ) )
        return True, status_file.FOLLOWING

    if b1 == BTN_NONE:
        print_error( "user {} doesn't have follow/unfollow button".format( username ) )
        return True, status_file.BROKEN

    if not click_follow_user( driver ):
        return False, status_file.NOT_FOLLOWING

    helpers.sleep( 2, False )

    if has_follow_button( driver ):
        print_error( "failed to follow user {}".format( username ) )
        return False, status_file.NOT_FOLLOWING

    return True, status_file.FOLLOWING

##########################################################

def follow_user( driver, username ):

    link = "https://www.twitch.tv/" + username

    driver.get( link )

    return follow_user_core( driver, username )

##########################################################

def unfollow_user_core( driver, username ):

    b1 = detect_follow_unfollow_button( driver )

    if b1 == BTN_FOLLOW:
        print_warning( "user {} is already unfollowed".format( username ) )
        return True, status_file.NOT_FOLLOWING

    if b1 == BTN_NONE:
        print_error( "user {} doesn't have follow/unfollow button".format( username ) )
        return True, status_file.BROKEN

    if not click_follow_user( driver ):
        return False, status_file.FOLLOWING

    if not click_modal_unfollow_user( driver ):
        return False, status_file.FOLLOWING

    helpers.sleep( 2, False )

    if has_unfollow_button( driver ):
        print_error( "failed to unfollow user {}".format( username ) )
        return False, status_file.FOLLOWING

    return True, status_file.UNFOLLOWED

##########################################################

def unfollow_user( driver, username ):

    link = "https://www.twitch.tv/" + username

    driver.get( link )

    return unfollow_user_core( driver, username )

##########################################################

def follow_unfollow_user( driver, username ):

    link = "https://www.twitch.tv/" + username

    driver.get( link )

    b1, status = follow_user_core( driver, username )

    if not b1:
        return False, status

    b2, status = unfollow_user_core( driver, username )

    if not b2:
        return False, status

    return True, status

##########################################################

def mode_to_text( mode ):
    if mode == MODE_UNFOLLOW:
        return "unfollowing"
    elif mode == MODE_FOLLOW:
        return "following"
    elif mode == MODE_FOLLOW_UNFOLLOW:
        return "following/unfollowing"
    elif mode == MODE_REFOLLOW:
        return "refollowing"
    else:
        return "?"

##########################################################

def mode_to_string( mode ):
    if mode == MODE_UNFOLLOW:
        return "MODE_UNFOLLOW"
    elif mode == MODE_FOLLOW:
        return "MODE_FOLLOW"
    elif mode == MODE_FOLLOW_UNFOLLOW:
        return "MODE_FOLLOW_UNFOLLOW"
    elif mode == MODE_REFOLLOW:
        return "MODE_REFOLLOW"
    else:
        return "?"

##########################################################

def process_user__throwing( driver, user, mode ):

    is_dirty = False
    follow_type = None

    if mode == MODE_UNFOLLOW:
        is_dirty, follow_type = unfollow_user( driver, user )
    elif mode == MODE_FOLLOW:
        is_dirty, follow_type = follow_user( driver, user )
    elif mode == MODE_FOLLOW_UNFOLLOW:
        is_dirty, follow_type = follow_unfollow_user( driver, user )
    else:
        print_fatal( "unsupported mode" )
        quit()

    return is_dirty, follow_type

##########################################################

def process_user( driver, user, mode ):

    try:
        return process_user__throwing( driver, user, mode )

    except NoSuchWindowException:

        print_fatal( "browser window/tab was closed" )
        quit()

    except WebDriverException:

        print_error( "page crashed" )
        # return will not help, as it looks like it is necessary to re-initialize the driver
        # the most appropriate handling now is to quit()
        #return False, status_file.BROKEN
        quit()

##########################################################

def process_users( driver, status, status_filename, users, mode ):

    num_users = len( users )

    i = 0

    for u in users:

        i += 1

        print_info( "{} user {} / {} - {}".format( mode_to_text( mode ), i, num_users, u ) )

        is_dirty, follow_type = process_user( driver, u, mode )

        if mode == MODE_UNFOLLOW:
            if is_dirty:
                print_info( "unfollowed user {} / {} - {}".format( i, num_users, u ) )
            else:
                print_error( "failed to unfollow user {} / {} - {}".format( i, num_users, u ) )
        elif mode == MODE_FOLLOW:
            if is_dirty:
                print_info( "followed user {} / {} - {}".format( i, num_users, u ) )
            else:
                print_error( "failed to follow user {} / {} - {}".format( i, num_users, u ) )

        elif mode == MODE_FOLLOW_UNFOLLOW:
            if is_dirty:
                print_info( "followed and unfollowed user {} / {} - {}".format( i, num_users, u ) )
            else:
                print_error( "failed to follow/unfollow user {} / {} - {}".format( i, num_users, u ) )

        if is_dirty:
            status_file.set_follow_type( status, u, follow_type )
            status_file.save_status_file( status_filename, status )

##########################################################

def determine_notfollowed_users( status, users_list ):

    res = []

    for u in users_list:
        if u in status:
            if status[u].follow_type == status_file.NOT_FOLLOWING:
                res.append( u )
        else:
            res.append( u )

    return res

##########################################################

def determine_followed_users( status ):

    res = []

    for u in status:
        if status[u].follow_type == status_file.FOLLOWING:
            res.append( u )

    return res

##########################################################

def load_credentials( credentials_filename ):

    print_debug( "load_credentials: from {}".format( credentials_filename ) )

    config = configparser.ConfigParser()
    config.read( credentials_filename )

    login    = config['credentials']['login']
    password = config['credentials']['password']

    print_debug( "login    = {}".format( login ) )
    #print_debug( "password = {}".format( password ) )

    print_info( "load_credentials: OK, from {}".format( credentials_filename ) )

    return login, password

##########################################################

def process( user_file, credentials_filename, status_filename, cookies_dir, mode, is_headless ):

    login, password = load_credentials( credentials_filename )

    status = status_file.load_status_file( status_filename )

    users = None

    if mode == MODE_FOLLOW or mode == MODE_FOLLOW_UNFOLLOW:
        users_all = status_file.read_users( user_file )
        users = determine_notfollowed_users( status, users_all )
        print_info( "total users - {}, still to follow - {}, already followed - {}".format( len( users_all ), len( users ), len( users_all) - len( users ) ) )
    elif mode == MODE_UNFOLLOW:
        users = determine_followed_users( status )
        print_info( "users to unfollow - {}".format( len( users ) ) )
    else:
        print_error( "unsupported mode {}".format( mode ) )
        quit()

    if len( users ) == 0:
        print_info( "nothing to do" )
        quit()

    driver = helpers.init_driver( config.DRIVER_PATH, config.BROWSER_BINARY, cookies_dir, is_headless )

    loginer.login( driver, login, password )

    process_users( driver, status, status_filename, users, mode )

    print_info( "done" )

##########################################################

def main( argv ):

    user_file = None
    status_filename = None
    user_dir = None
    is_headless = False
    mode = MODE_FOLLOW

    pagesize = 0
    pagenum = 0
    limit   = 0

    outputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:s:u:Hm:",["ifile=","ofile=","status=","userdir=","HEADLESS","mode","pagesize=","pagenum=","limit="])
    except getopt.GetoptError:
        print( 'follower.py -i <inputfile> -o <outputfile> -u <userdir> -s <statusfile> -m <MODE>' )
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print( 'follower.py -i <inputfile> -o <outputfile> -u <userdir> -s <statusfile> -m <MODE> [-H]' )
            sys.exit()
        elif opt in ("-i", "--ifile"):
            user_file = arg
        elif opt in ("-s", "--status"):
            status_filename = arg
        elif opt in ("-u", "--userdir"):
            user_dir = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-H", "--HEADLESS"):
            is_headless = True
        elif opt in ( "--pagesize" ):
            pagesize = int( arg )
        elif opt in ( "--pagenum" ):
            pagenum = int( arg )
        elif opt in ( "--limit" ):
            limit = int( arg )
        elif opt in ("-m", "--mode"):
            if arg == 'F':
                mode = MODE_FOLLOW
            elif arg == 'U':
                mode = MODE_UNFOLLOW
            elif arg == 'L':
                mode = MODE_FOLLOW_UNFOLLOW
            elif arg == 'R':
                mode = MODE_REFOLLOW
            else:
                print_fatal( "unsupported mode: {}".format( arg ) )
                quit()

    print_debug( "input file  = {}".format( user_file ) )
    print_debug( "status file = {}".format( status_filename ) )
    print_debug( "user dir    = {}".format( user_dir ) )
    print_debug( "output file = {}".format( outputfile ) )
    print_debug( "pagesize    = {}".format( pagesize ) )
    print_debug( "pagenum     = {}".format( pagenum ) )
    print_debug( "limit       = {}".format( limit ) )

    if not user_file:
        print_fatal( "user file is not given" )
        quit()

    if not user_dir:
        print_fatal( "user dir is not given" )
        quit()

    if pagesize < 0:
        print_fatal( "pagesize < 0" )
        quit()

    if pagenum < 0:
        print_fatal( "pagenum < 0" )
        quit()

    if limit < 0:
        print_fatal( "limit < 0" )
        quit()

    quit()

    print_info( "starting in {}".format( mode_to_string( mode ) ) )

    if is_headless:
        print_info( "starting in HEADLESS mode" )

    user_dir = harmonize_link( user_dir )

    credentials_filename = user_dir + "credentials.ini"
    cookies_dir          = user_dir + "cookies"

    if not status_filename:
        status_filename      = user_dir + "status.csv"

    process( user_file, credentials_filename, status_filename, cookies_dir, mode, is_headless )

##########################################################

if __name__ == "__main__":
   main( sys.argv[1:] )
