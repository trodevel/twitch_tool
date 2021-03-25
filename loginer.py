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
from selenium.webdriver.common.keys import Keys

import helpers        # find_element_by_tag_and_class_name
import re

##########################################################

def accept_banner( driver ):

    link = "/html/body/div[1]/div/div[2]/div[1]/div/div/div[3]/button"

    if helpers.does_xpath_exist_with_timeout( driver, link, 5 ) == False:
        print( "INFO: no banner found" )
        return

    print( "INFO: found banner, clicking" )

    button = driver.find_element_by_xpath( link )

    button.click()

##########################################################

def enter_credentials( driver, login, password ):

    login_input    = helpers.find_element_by_xpath_with_timeout( driver, "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/form/div/div[1]/div/div[2]/input", 10 )
    login_password = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/form/div/div[2]/div/div[1]/div[2]/div[1]/input" )
    login_button   = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/form/div/div[3]/button" )

    print( "INFO: sending login {}".format( login ) )

    login_input.send_keys( Keys.CONTROL + "a" )
    login_input.send_keys( Keys.DELETE )
    login_input.send_keys( login )

    login_password.send_keys( Keys.CONTROL + "a" )
    login_password.send_keys( Keys.DELETE )
    login_password.send_keys( password )

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

    link = "/html/body/div[3]/div/div/div/div/div/div/div[4]/button"

    if helpers.does_xpath_exist_with_timeout( driver, link, 10 ) == False:
        print( "INFO: no welcome screen found" )
        return

    button = driver.find_element_by_xpath( link )

    print( "DEBUG: clicking" )

    button.click()

    close_button = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div/div[1]/div/div/button" )

    print( "DEBUG: clicking" )

    close_button.click()

##########################################################

def perform_login( driver, login, password ):

    login_button = helpers.find_element_by_xpath_with_timeout( driver, "/html/body/div[1]/div/div[2]/nav/div/div[3]/div[3]/div/div[1]/div[1]/button", 5 )

    print( "DEBUG: clicking" )

    login_button.click()

    enter_credentials( driver, login, password )

    validation_code = input( "Enter 6-digit validation code: " )

    enter_validation_code( driver, validation_code )

##########################################################

def is_logged_in( driver ):

    if helpers.does_xpath_exist_with_timeout( driver, "/html/body/div[1]/div/div[2]/nav/div/div[3]/div[3]/div/div[1]/div[1]/button", 1 ):
        return False

    if helpers.does_xpath_exist_with_timeout( driver, "/html/body/div[1]/div/div[2]/nav/div/div[3]/div[6]/div/div/div/div/button", 5 ):
        return True

    return False

##########################################################

def login( driver, login, password ):

    driver.get( 'https://www.twitch.tv' )

    if is_logged_in( driver ) == False:

        print( "INFO: not logged in" )

        accept_banner( driver )

        perform_login( driver, login, password )

        accept_welcome_screen( driver )

        accept_banner( driver )

    else:
        print( "INFO: already logged in" )

##########################################################
