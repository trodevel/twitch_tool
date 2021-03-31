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
from print_helpers import print_error, print_warning

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
"//button[contains(@data-a-target,'follow-button')]",
"//button[contains(@data-a-target,'unfollow-button')]"
]
    result = helpers.do_xpaths_exist_with_timeout( driver, paths, 10 )

    if result[0] == False:
        print_error( "cannot find follow/unfollow button" )
        return False

    button = driver.find_element_by_xpath( result[1] )

    attr = button.get_attribute( "data-a-target" )

    #print( "DEBUG: attr = {}".format( attr ) )

    if attr == "unfollow-button":
        return True
    elif attr == "follow-button":
        return False
    else:
        print_error( "unexpected value of attribute - {}".format( attr ) )

    return False

##########################################################

def click_follow_user( driver ):

    paths = [
"//button[contains(@data-a-target,'follow-button')]",
"//button[contains(@data-a-target,'unfollow-button')]"
]
    result = helpers.do_xpaths_exist_with_timeout( driver, paths, 10 )

    if result[0] == False:
        print_error( "cannot find follow button" )
        return False

    #print( "DEBUG: found element link {}".format( result[2] ) )

    print( "INFO: clicked follow button" )

    button = driver.find_element_by_xpath( result[1] )

    button.click()

    return True

##########################################################

def follow_user( driver, username ):

    link = "https://www.twitch.tv/" + username

    driver.get( link )

    if has_unfollow_button( driver ):
        print( "WARNING: user {} is already followed".format( username ) )
        return True

    has_followed = False

    if( click_follow_user( driver ) ):
        helpers.sleep( 2, False )
        if has_unfollow_button( driver ):
            has_followed = True
        else:
            print_error( "failed to follow user {}".format( username ) )


    return has_followed

##########################################################

def follow_users( driver, status, status_filename, users ):

    num_users = len( users )

    i = 0

    for u in users:

        i += 1

        print( "INFO: following user {} / {} - {}".format( i, num_users, u ) )

        is_following = follow_user( driver, u )

        status_file.set_follow( status, u, is_following )

        status_file.save_status_file( status_filename, status )

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

def process( user_file, status_filename ):

    users_all = status_file.read_users( user_file )

    status = status_file.load_status_file( status_filename )

    users = determine_notfollowed_users( status, users_all )

    print( "INFO: total users - {}, still to follow - {}, already followed - {}".format( len( users_all ), len( users ), len( users_all) - len( users ) ) )

    if len( users ) == 0:
        print( "INFO: nothing to do" )
        quit()

    driver = helpers.init_driver( config.DRIVER_PATH, config.BROWSER_BINARY, harmonize_link( config.COOKIES_DIR ) + credentials.LOGIN )

    loginer.login( driver, credentials.LOGIN, credentials.PASSWORD )

    follow_users( driver, status, status_filename, users )

    print( "INFO: done" )

##########################################################

def main( argv ):

    user_file = None
    status_filename = None

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
            status_filename = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg

    print ( "DEBUG: input file  = {}".format( user_file ) )
    print ( "DEBUG: status file = {}".format( status_filename ) )
    print ( "DEBUG: output file = {}".format( outputfile ) )

    if not user_file:
        print( "FATAL: user file is not given" )
        quit()

    if not status_filename:
        print( "FATAL: status file is not given" )
        quit()

    process( user_file, status_filename )

##########################################################

if __name__ == "__main__":
   main( sys.argv[1:] )
