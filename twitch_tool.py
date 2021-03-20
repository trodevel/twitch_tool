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

import config         # DRIVER_PATH
import credentials    # LOGIN
import helpers        # find_element_by_tag_and_class_name
#import product_parser # parse_product
import re
import time

from datetime import datetime

DEBUG_CATEGORY = False

##########################################################

def accept_banner( driver ):

    button = helpers.find_element_by_xpath_with_timeout( driver, "/html/body/div[1]/div/div[2]/div[1]/div/div/div[3]/button", 5 )

    print( "DEBUG: clicking" )

    button.click()

##########################################################

def enter_credentials( driver ):

    login_input    = helpers.find_element_by_xpath_with_timeout( driver, "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/form/div/div[1]/div/div[2]/input", 10 )
    login_password = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/form/div/div[2]/div/div[1]/div[2]/div[1]/input" )
    login_button   = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/form/div/div[3]/button" )

    print( "INFO: sending login {}".format( credentials.LOGIN ) )

    login_input.send_keys( credentials.LOGIN )
    login_password.send_keys( credentials.PASSWORD )

    print( "DEBUG: clicking" )

    login_button.click()

##########################################################

def enter_validation_code( driver, code ):

    code_1    = helpers.find_element_by_xpath_with_timeout( driver, "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/div[2]/div/div[1]/div/input", 10 )
    code_2    = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/div[2]/div/div[2]/div/input" )
    code_3    = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/div[2]/div/div[3]/div/input" )
    code_4    = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/div[2]/div/div[4]/div/input" )
    code_5    = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/div[2]/div/div[5]/div/input" )
    code_6    = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/div[2]/div/div[6]/div/input" )

    print( "INFO: sending validation code {}".format( code ) )

    code_1.send_keys( code[0] )
    code_2.send_keys( code[1] )
    code_3.send_keys( code[2] )
    code_4.send_keys( code[3] )
    code_5.send_keys( code[4] )
    code_6.send_keys( code[5] )

##########################################################

def accept_welcome_screen( driver ):

    button = helpers.find_element_by_xpath_with_timeout( driver, "/html/body/div[3]/div/div/div/div/div/div/div[4]/button", 10 )

    print( "DEBUG: clicking" )

    button.click()

    close_button = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div/div[1]/div/div/button" )

    print( "DEBUG: clicking" )

    close_button.click()

##########################################################

def perform_login( driver ):

    login_button = helpers.find_element_by_xpath_with_timeout( driver, "/html/body/div[1]/div/div[2]/nav/div/div[3]/div[3]/div/div[1]/div[1]/button", 5 )

    print( "DEBUG: clicking" )

    login_button.click()

    enter_credentials( driver )

    validation_code = input( "Enter 6-digit validation code: " )

    enter_validation_code( driver, validation_code )

##########################################################

def is_logged_in( driver ):

    if helpers.does_xpath_exist_with_timeout( driver, "/html/body/div[1]/div/div[2]/nav/div/div[3]/div[6]/div/div/div/div/button", 5 ):
        return True

    return False

##########################################################

def harmonize_link( link ):

    if link.endswith('/'):
        return link

    return link + '/'

##########################################################

def open_first_top_stream( driver ):

    a = helpers.find_element_by_xpath_with_timeout( driver, "/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div/div/div/div[4]/div[2]/div[1]/div[1]/div[2]/div/div/div/article/div[1]/div/div[1]/div[1]/div/a", 10 )

    link = a.get_attribute( 'href' )

    link = harmonize_link( link )

    print( "INFO: opening top stream {}".format( link ) )

    driver.get( link )

##########################################################

def pause_player( driver ):

    paths = [
    "/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div[5]/div/div[2]/div[1]/div[1]/button",
    "/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div[3]/div/div[2]/div[1]/div[1]/button",
    "/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div/div/div[8]/div/div[2]/div[1]/div[1]/button",
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

def determine_users_in_category( driver, category_name ):

    elements = driver.find_elements_by_css_selector( "div[role='listitem']" )

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

def determine_categories_and_users( driver ):

    paths = [
"/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div/div/div/div/section/div/div[5]/section/div/div[2]/div[2]/div[3]/div/div",
"/html/body/div[1]/div/div[2]/div/div[2]/div/div[1]/div/div/div/div/div/section/div/div[6]/section/div/div[2]/div[2]/div[3]/div" ]

    result = helpers.do_xpaths_exist_with_timeout( driver, paths, 10 )

    if result[0] == False:
        print( "ERROR: cannot determine categories" )
        return

    print( "DEBUG: found element link {}".format( result[2] ) )

    d0 = driver.find_element_by_xpath( result[1] )

    elements = d0.find_elements_by_css_selector( "div[class='chat-viewers-list tw-pd-b-2']" )

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

        users = determine_users_in_category( list_elem, name )

        names[ name ] = users

    return names

##########################################################

def follow_user( driver ):

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

def parse_user_and_follow( driver, f, category_name, user ):

    link = "https://www.twitch.tv/" + user

    driver.get( link )

    creation_time = int( time.time() )

    has_followed = follow_user( driver )

    line = category_name + ';' + user + ';' + str( creation_time ) + ';' + str( int( has_followed ) ) + "\n"

    f.write( line )

##########################################################

def parse_category_and_follow( driver, f, category_name, users ):

    num_users = len( users )

    i = 0

    for u in users:

        i += 1

        print( "INFO: parsing subcategory {} / {} - {}".format( i, num_users, u ) )

        parse_user_and_follow( driver, f, category_name, u )

##########################################################

def generate_filename():
    now = datetime.now()
    d1 = now.strftime( "%Y%m%d_%H%M" )
    res = "users_" + d1 + ".csv"
    return res

##########################################################
driver = helpers.init_driver( config.DRIVER_PATH, config.BROWSER_BINARY, harmonize_link( config.COOKIES_DIR ) + credentials.LOGIN )

driver.get( 'https://www.twitch.tv' )

if is_logged_in( driver ) == False:

    accept_banner( driver )

    perform_login( driver )

    accept_welcome_screen( driver )

    accept_banner( driver )

else:
    print( "INFO: already logged in" )

# reopen the selected page again
driver.get( 'https://www.twitch.tv/directory/game/Dota%202?sort=VIEWER_COUNT' )

open_first_top_stream( driver )

pause_player( driver )

show_chat_users( driver )

category_names = determine_categories_and_users( driver )

num_category_names = len( category_names )

f = open( generate_filename(), "w" )

i = 0

for c in category_names:

    i += 1

    print( "INFO: parsing category {} / {} - {}".format( i, num_category_names, c ) )

    if c.find( "Users" ) == -1:
        print( "DEBUG: temporary ignoring category {}".format( c ) )
        continue

    users = category_names[ c ]

    parse_category_and_follow( driver, f, c, users )

print( "INFO: done" )
