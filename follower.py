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

from datetime import datetime

DEBUG_CATEGORY = False

##########################################################

def harmonize_link( link ):

    if link.endswith('/'):
        return link

    return link + '/'

##########################################################

def find_first_top_stream_on_page( driver ):

    a = helpers.find_element_by_xpath_with_timeout( driver, "/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div/div/div/div[4]/div[2]/div[1]/div[1]/div[2]/div/div/div/article/div[1]/div/div[1]/div[1]/div/a", 10 )

    link = a.get_attribute( 'href' )

    link = harmonize_link( link )

    return link

##########################################################

def find_first_top_stream( driver ):

    # reopen the selected page again
    driver.get( 'https://www.twitch.tv/directory/game/Dota%202?sort=VIEWER_COUNT' )

    link = find_first_top_stream_on_page( driver )

    return link

##########################################################

def pause_player( driver ):

    paths = [
    "//button[@data-a-target='player-play-pause-button']"
#    "/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div[6]/div/div[2]/div[1]/div[1]/button",
#    "/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div[5]/div/div[2]/div[1]/div[1]/button",
#    "/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div[3]/div/div[2]/div[1]/div[1]/button",
#    "/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div[8]/div/div[2]/div[1]/div[1]/button",
]
    result = helpers.do_xpaths_exist_with_timeout( driver, paths, 10 )

    if result[0] == False:
        print( "WARNING: player button not found" )
        return False

    button = driver.find_element_by_xpath( result[1] )

    print( "INFO: pausing player" )

    button.click()

##########################################################

def show_chat_users( driver ):

    print( "TRACE: show_chat_users" )

    button = driver.find_element_by_xpath( "/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div/div/div/div/div/div[2]/div/button" )

    button.click()

##########################################################

def determine_number_of_viewers( driver ):

    print( "TRACE: determine_number_of_viewers" )

    counter = helpers.find_element_by_xpath_with_timeout( driver, "//p[@data-a-target='animated-channel-viewers-count']", 10 )

    val_str = counter.text

    val_str = val_str.translate( {ord(c): None for c in ','} )

    print( "DEBUG: val_str {}".format( val_str ) )

    val = int( val_str )

    return val

##########################################################

def scroll_user_list( driver, parent ):

    trigger = helpers.find_element_by_xpath_with_timeout( parent, "//div[@class='scrollable-trigger__wrapper']", 10 )

    driver.execute_script( "document.getElementsByClassName('scrollable-trigger__wrapper')[0].scrollIntoView();" )

##########################################################

def determine_users_in_category( driver, parent, category_name ):

    elements = parent.find_elements_by_css_selector( "div[role='listitem']" )

    print( "INFO: category {} - found {} users".format( category_name, len( elements ) ) )

    names = []

    for s in elements:

        if helpers.does_tag_exist( s, "button" ) == False:
            print( "WARNING: element without tag 'button', ignoring" )
            continue

        s2 = s.find_element_by_tag_name( "button" )

        name = s2.get_attribute( 'data-username' )

        print( "DEBUG: determine_users_in_category: {}".format( name ) )

        names.append( name )

    return names

##########################################################

def scroll_to_bottom( driver, parent, max_users ):

    max_iter = int( max_users / 100 )

    for i in range( max_iter ):

        print( "DEBUG: scroll_to_bottom: iter {} / {}".format( i + 1, max_iter ) )

        helpers.sleep( 2 )

        scroll_user_list( driver, parent )

##########################################################

def determine_categories_and_users( driver, max_users ):

    print( "TRACE: determine_categories_and_users" )

    paths = [
"//div[@class='tw-pd-b-5 tw-pd-x-2']"
]

    result = helpers.do_xpaths_exist_with_timeout( driver, paths, 10 )

    if result[0] == False:
        print( "ERROR: cannot determine categories" )
        return

    print( "DEBUG: found element link {}".format( result[2] ) )

    #d0 = driver.find_element_by_xpath( result[1] )

    if helpers.does_xpath_exist_with_timeout( driver, "//div[@class='chat-viewers-list tw-pd-b-2']", 10 ) == False:
        print( "ERROR: cannot find element with chat list" )
        quit()

    parent = driver.find_element_by_xpath( result[1] )

    scroll_to_bottom( driver, parent, max_users )

    elements = driver.find_elements_by_xpath( "//div[@class='chat-viewers-list tw-pd-b-2']" )

    print( "DEBUG: found {} categories".format( len( elements ) ) )

    names = dict()

    for s in elements:

        d1 = s.find_element_by_xpath( "div[1]" )

        name = d1.text

        print( "DEBUG: determine_categories_and_users: {}".format( name ) )

        if name.find( "pflanzensamen" ) == -1 and DEBUG_CATEGORY == True:
            print( "DEBUG: temporary ignoring" )
            continue

        list_elem = s.find_element_by_xpath( "div[2]" )

        users = determine_users_in_category( driver, list_elem, name )

        names[ name ] = users

    return names

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

    #button.click()

    return True

##########################################################

def follow_user( driver, f, category_name, user ):

    link = "https://www.twitch.tv/" + user

    driver.get( link )

    creation_time = int( time.time() )

    has_followed = click_follow_user( driver )

    line = category_name + ';' + user + ';' + str( creation_time ) + ';' + str( int( has_followed ) ) + "\n"

    f.write( line )

##########################################################

def follow_users( driver, f, users ):

    num_users = len( users )

    i = 0

    for u in users:

        i += 1

        print( "INFO: following user {} / {}".format( i, num_users ) )

        follow_user( driver, f, u )

##########################################################

def generate_filename():
    now = datetime.now()
    d1 = now.strftime( "%Y%m%d_%H%M" )
    res = "users_" + d1 + ".csv"
    return res

##########################################################

def read_users( fname ):

    with open(fname) as f:
        content = f.read().splitlines()

    return content

##########################################################

def process( user_file ):

    users = read_users( user_file )

    print( "INFO: read {} users from {}".format( len( user_file ), user_file ) )

    driver = helpers.init_driver( config.DRIVER_PATH, config.BROWSER_BINARY, harmonize_link( config.COOKIES_DIR ) + credentials.LOGIN )

    loginer.login( driver, credentials.LOGIN, credentials.PASSWORD )

    num_category_names = len( category_names )

    f = open( generate_filename(), "w" )

    follow_users( driver, f, users )

    print( "INFO: done" )

##########################################################

def main( argv ):

    user_file = None

    outputfile = ''

    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print 'follower.py -i <inputfile> -o <outputfile>'
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print 'follower.py -i <inputfile> -o <outputfile>'
            sys.exit()
        elif opt in ("-i", "--ifile"):
            user_file = arg
        elif opt in ("-o", "--ofile"):
            output_file = arg

    print "DEBUG: input file  = ", user_file
    print "DEBUG: output file = ", outputfile

    if not user_file:
        print "FATAL: user file is not given"
        quit()

    process( user_file )

##########################################################

if __name__ == "__main__":
   main( sys.argv[1:] )
