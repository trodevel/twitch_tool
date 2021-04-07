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
import status_file    # status_file
#import product_parser # parse_product
import re
from print_helpers import print_error, print_warning, print_debug

from datetime import datetime

DEBUG_CATEGORY = False

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

    return has_follow_or_unfollow_button( driver, False )

##########################################################

BTN_NONE = 0
BTN_FOLLOW = 1
BTN_UNFOLLOW = 2

##########################################################

def detect_follow_unfollow_button( driver ):

    paths = [
"//button[@data-a-target='unfollow-button']",
"//button[@data-a-target='follow-button']"
]
    result = helpers.do_xpaths_exist_with_timeout( driver, paths, 10 )

    if result[0] == False:
        print_error( "cannot find follow/unfollow button" )
        return NONE

    button = driver.find_element_by_xpath( result[1] )

    attr = button.get_attribute( "data-a-target" )

    print( "DEBUG: attr = {}, path = {}".format( attr, result[1] ) )

    if attr == "unfollow-button":
        print_debug( "found UNFOLLOW button" )
        return BTN_UNFOLLOW
    elif attr == "follow-button":
        print_debug( "found FOLLOW button" )
        return BTN_FOLLOW
    else:
        print_error( "unexpected value of attribute - {}".format( attr ) )

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

    print( "INFO: clicked follow button" )

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

    #print( "DEBUG: found element link {}".format( result[2] ) )

    print_debug( "clicked modal unfollow button" )

    button = driver.find_element_by_xpath( result[1] )

    helpers.wait_till_clickable_and_click( button, 10 )

    return True

##########################################################

def follow_user( driver, username ):

    link = "https://www.twitch.tv/" + username

    driver.get( link )

    b1 = detect_follow_unfollow_button( driver )

    if b1 == BTN_UNFOLLOW:
        print_warning( "user {} is already followed".format( username ) )
        return True

    if b1 == BTN_NONE:
        print_error( "user {} doesn't have follow/unfollow button".format( username ) )
        return False

    if not click_follow_user( driver ):
        return False

    helpers.sleep( 2, False )

    if has_follow_button( driver ):
        print_error( "failed to follow user {}".format( username ) )
        return False

    return True

##########################################################

def unfollow_user( driver, username ):

    link = "https://www.twitch.tv/" + username

    driver.get( link )

    b1 = detect_follow_unfollow_button( driver )

    if b1 == BTN_FOLLOW:
        print_warning( "user {} is already unfollowed".format( username ) )
        return True

    if b1 == BTN_NONE:
        print_error( "user {} doesn't have follow/unfollow button".format( username ) )
        return False

    if not click_follow_user( driver ):
        return False

    if not click_modal_unfollow_user( driver ):
        return False

    helpers.sleep( 2, False )

    if has_unfollow_button( driver ):
        print_error( "failed to unfollow user {}".format( username ) )
        return False

    return True

##########################################################

def follow_users( driver, status, status_filename, users, must_unfollow ):

    num_users = len( users )

    i = 0

    pref = ""
    if must_unfollow:
        pref="un"

    for u in users:

        i += 1

        print( "INFO: {}following user {} / {} - {}".format( pref, i, num_users, u ) )


        is_succeded = False

        if must_unfollow:
            is_succeded = unfollow_user( driver, u )
        else:
            is_succeded = follow_user( driver, u )

        follow_type = None
        is_dirty    = True

        if must_unfollow:
            if is_succeded:
                follow_type = status_file.UNFOLLOWED
                print( "INFO: unfollowed user {} / {} - {}".format( i, num_users, u ) )
            else:
                print_error( "failed to unfollow user {} / {} - {}".format( i, num_users, u ) )
                is_dirty    = False
        else:
            if is_succeded:
                follow_type = status_file.FOLLOWING
                print( "INFO: followed user {} / {} - {}".format( i, num_users, u ) )
            else:
                print_error( "failed to follow user {} / {} - {}".format( i, num_users, u ) )
                follow_type = status_file.NOT_FOLLOWING

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

def process( user_file, status_filename, must_unfollow, is_headless ):

    status = status_file.load_status_file( status_filename )

    users = None

    if not must_unfollow:
        users_all = status_file.read_users( user_file )
        users = determine_notfollowed_users( status, users_all )
        print( "INFO: total users - {}, still to follow - {}, already followed - {}".format( len( users_all ), len( users ), len( users_all) - len( users ) ) )
    else:
        users = determine_followed_users( status )
        print( "INFO: users to unfollow - {}".format( len( users ) ) )

    if len( users ) == 0:
        print( "INFO: nothing to do" )
        quit()

    driver = helpers.init_driver( config.DRIVER_PATH, config.BROWSER_BINARY, harmonize_link( config.COOKIES_DIR ) + credentials.LOGIN, is_headless )

    loginer.login( driver, credentials.LOGIN, credentials.PASSWORD )

    follow_users( driver, status, status_filename, users, must_unfollow )

    print( "INFO: done" )

##########################################################

def main( argv ):

    user_file = None
    status_filename = None
    is_headless = False
    must_unfollow = False

    outputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:s:HU",["ifile=","ofile=","status=","HEADLESS","UNFOLLOW"])
    except getopt.GetoptError:
        print( 'follower.py -i <inputfile> -o <outputfile> -s <userfile>' )
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print( 'follower.py -i <inputfile> -o <outputfile> -s <userfile> [-H] [-U]' )
            sys.exit()
        elif opt in ("-i", "--ifile"):
            user_file = arg
        elif opt in ("-s", "--status"):
            status_filename = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg
        elif opt in ("-H", "--HEADLESS"):
            is_headless = True
        elif opt in ("-U", "--UNFOLLOW"):
            must_unfollow = True

    print ( "DEBUG: input file  = {}".format( user_file ) )
    print ( "DEBUG: status file = {}".format( status_filename ) )
    print ( "DEBUG: output file = {}".format( outputfile ) )

    if not user_file:
        print( "FATAL: user file is not given" )
        quit()

    if not status_filename:
        print( "FATAL: status file is not given" )
        quit()

    if is_headless:
        print( "INFO: starting in HEADLESS mode" )

    if must_unfollow:
        print( "INFO: starting UNFOLLOW" )

    process( user_file, status_filename, must_unfollow, is_headless )

##########################################################

if __name__ == "__main__":
   main( sys.argv[1:] )
