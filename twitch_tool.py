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

from datetime import datetime

DEBUG_CATEGORY = False

##########################################################

def accept_banner( driver ):

    button = driver.find_element_by_xpath( "/html/body/div[1]/div/div[2]/div[1]/div/div/div[3]/button" )

    helpers.sleep(2)

    #d0 = driver.find_element_by_id( "root" )
    #d1 = d0.find_element_by_css_selector( "div[class='tw-absolute tw-bottom-0 tw-flex tw-flex-column tw-flex-nowrap tw-left-0 tw-overflow-hidden tw-right-0 tw-top-0']" )
    #d2 = d1.find_element_by_css_selector( "div[data-dmid='cookiebar-dm-overlay']" )
    #d3 = d2.find_element_by_css_selector( "div[data-dmid='cookiebar']" )
    #d4 = d3.find_element_by_css_selector( "button[data-dmid='cookiebar-ok']" )

    #print( "DEBUG: found banner" )

    print( "DEBUG: clicking" )

    button.click()

##########################################################

def enter_credentials( driver ):

    login_input    = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/form/div/div[1]/div/div[2]/input" )
    login_password = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/form/div/div[2]/div/div[1]/div[2]/div[1]/input" )
    login_button   = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/form/div/div[3]/button" )

    print( "INFO: sending login {}".format( credentials.LOGIN ) )

    login_input.send_keys( credentials.LOGIN )
    login_password.send_keys( credentials.PASSWORD )

    helpers.sleep(1)

    print( "DEBUG: clicking" )

    login_button.click()

##########################################################

def enter_validation_code( driver, code ):

    code_1    = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div[1]/div/div/div[3]/div[2]/div/div[1]/div/input" )
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

    helpers.sleep(1)

##########################################################

def accept_welcome_screen( driver ):

    button = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div/div[4]/button" )

    helpers.sleep(1)

    print( "DEBUG: clicking" )

    button.click()

    close_button = driver.find_element_by_xpath( "/html/body/div[3]/div/div/div/div/div/div/div[1]/div/div/button" )

    print( "DEBUG: clicking" )

    close_button.click()

    helpers.sleep(1)

##########################################################

def select_found_shop( driver ):

    d0 = driver.find_element_by_id( "app" )
    d1 = d0.find_element_by_css_selector( "div[data-dmid='app-container']" )
    d2 = d1.find_element_by_css_selector( "div[data-dmid='main-container']" )
    d3 = d2.find_element_by_xpath( "//div" )
    d4 = d3.find_element_by_xpath( "//div" )
    d5 = d4.find_element_by_css_selector( "div[data-dmid='storefinder-wrapper']" )
    d6 = d5.find_element_by_css_selector( "div[data-dmid='store-list-overlay-wrapper']" )

    d8 = WebDriverWait( d6, 15 ).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-dmid='store-list-container']"))
        )

    d9 = d8.find_element_by_css_selector( "div[data-dmid='store-list']" )
    d10 = d9.find_element_by_css_selector( "div[data-dmid='store-teaser']" )
    d11 = d10.find_element_by_css_selector( "div[data-dmid='store-teaser-info-container']" )
    d12 = d11.find_element_by_css_selector( "div[data-dmid='store-teaser-button-container']" )
    d13 = d12.find_element_by_css_selector( "button[data-dmid='store-teaser-button']" )

    print( "DEBUG: selecting shop" )

    d13.click()

    helpers.sleep(2)

##########################################################

def perform_login( driver ):

    login_button = driver.find_element_by_xpath( "/html/body/div[1]/div/div[2]/nav/div/div[3]/div[3]/div/div[1]/div[1]/button" )

    print( "DEBUG: clicking" )

    login_button.click()

    helpers.sleep( 5 )

    enter_credentials( driver )

    validation_code = input( "Enter 6-digit validation code: " )

    enter_validation_code( driver, validation_code )

    helpers.sleep(3)

##########################################################

def is_logged_in( driver ):

    if helpers.does_xpath_exist( driver, "/html/body/div[1]/div/div[2]/nav/div/div[3]/div[6]/div/div/div/div/button" ):
        return True

    return False

##########################################################

def harmonize_link( link ):

    if link.endswith('/'):
        return link

    return link + '/'

##########################################################

def open_first_top_stream( driver ):

    a = driver.find_element_by_xpath( "/html/body/div[1]/div/div[2]/div/main/div[2]/div[3]/div/div/div/div/div/div[4]/div[2]/div[1]/div[1]/div[2]/div/div/div/article/div[1]/div/div[1]/div[1]/div/a" )

    link = a.get_attribute( 'href' )

    link = harmonize_link( link )

    print( "INFO: opening top stream {}".format( link ) )

    driver.get( link )

    helpers.sleep( 3 )

##########################################################

def determine_categories( driver ):

    d0 = driver.find_element_by_id( "app" )
    d1 = d0.find_element_by_css_selector( "div[data-dmid='app-container']" )
    d2 = d1.find_element_by_css_selector( "div[data-dmid='main-container']" )
    d3 = d2.find_element_by_xpath( "div" )
    d4 = d3.find_element_by_css_selector( "div[data-dmid='dm-modules-container']" )
    d5 = d4.find_element_by_css_selector( "div[data-dmid='modules-container']" )

    el2 = d5.find_elements_by_css_selector( "div[data-dmid='module-container']" )

    #print( "DEBUG: found {} el2".format( len( el2 ) ) )

    d10 = d2.find_element_by_xpath( "/html/body/div[1]/div/div[5]/div/div/div/div[10]/div/div/div[2]/div[1]/div" )

    elements = d10.find_elements_by_xpath( "div[starts-with(@class,'odt_TeaserGroup-module_item')]" )

    print( "INFO: found {} categories".format( len( elements ) ) )

    links = []

    for s in elements:

        d14 = s.find_element_by_xpath( "a[starts-with(@class,'odt_TeaserGroup-module_teaserLink')]" )

        link = d14.get_attribute( 'href' )

        link = harmonize_link( link )

        print( "DEBUG: determine_categories: {}".format( link ) )

        if link.find( "pflanzensamen" ) == -1 and DEBUG_CATEGORY == True:
            print( "DEBUG: temporary ignoring" )
            continue

        links.append( link )

    return links

##########################################################

def determine_subcategories( driver ):

    d1 = driver.find_element_by_class_name( 'products-sub-categories' )

    d2 = d1.find_element_by_css_selector( "div[class='products-sub-categories__container swiper-container']" )

    d3 = d2.find_element_by_css_selector( "div[class='products-sub-categories__items swiper-wrapper']" )

    elements = d3.find_elements_by_css_selector( "div[class='products-sub-categories__item swiper-slide']" )

    print( "INFO: found {} sub categories".format( len( elements ) ) )

    links = dict()

    for s in elements:

        if helpers.does_tag_exist( s, "a" ) == False:
            print( "WARNING: element without tag 'a', ignoring" )
            continue

        s2 = s.find_element_by_tag_name( "a" )

        link = s2.get_attribute( 'href' )
        name = s2.text

        if link == None:
            print( "WARNING: empty link {}, ignoring".format( s2 ) )
            continue

        link = harmonize_link( link )

        print( "DEBUG: determine_subcategories: {} - {}".format( link, name ) )
        links[ link ] = name

    return links

##########################################################

def determine_products( driver ):

    d1 = driver.find_element_by_css_selector( "div[class='search-results-container container']" )

    d2 = d1.find_element_by_css_selector( "div[class='row search-results-wrapper']" )

    element = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "search-results-item" ))
        )

    elements = d2.find_elements_by_class_name( 'search-results-item' )

    print( "INFO: found {} products".format( len( elements ) ) )

    if len( elements ) == 0:
        print( "FATAL: no products found on page" )
        exit()

    links = []

    for e in elements:

        e1 = e.find_element_by_class_name( 'product-teaser' )

        link = e1.get_attribute( 'href' )

        if link == None:
            print( "WARNING: empty link {}, ignoring".format( s2 ) )
            continue

        link = harmonize_link( link )

        print( "DEBUG: determine_products: {}".format( link ) )

        links.append( link )

    return links

##########################################################

def determine_number_of_pages( driver ):

    element = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "pagination-wrapper"))
        )

    i2 = element.find_element_by_id( 'pagination' )

    # we need to wait for element
    active = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.CLASS_NAME, "active_page"))
        )

    elems = i2.find_elements_by_class_name( 'page_button' )

    if len( elems ) == 0:
        print( "WARNING: no multiple pages found, using active page" )
        return int( active.text )

    last = elems[-1]

    return int( last.text )

##########################################################

def extract_handle_from_url( url ):
    p = re.compile( "/([a-z_\-]*)/$" )
    result = p.search( url )
    res = result.group( 1 )
    return res

##########################################################

def parse_product( driver, f, category_handle, category_name, subcategory_handle, subcategory_name, product_url ):

    driver.get( product_url )

    helpers.wait_for_page_load( driver )

    if helpers.does_class_exist( driver, 'product-detail-page' ) == False:
        print( "WARNING: cannot find product on {}".format( product_url ) )
        return

    if helpers.does_css_selector_exist( driver, "div[class='message message--error']" ) == True:
        print( "ERROR: technical problem on page {}".format( product_url ) )
        return

    d1 = driver.find_element_by_class_name( 'product-detail-page' )

    p = product_parser.parse_product( d1 )
    line = category_handle + ';' + subcategory_handle + ';' + category_name + ';' + subcategory_name + ';' + p + "\n"
    f.write( line )

##########################################################

def parse_page( driver, f, category_handle, category_name, subcategory_handle, subcategory_name ):

    product_urls = determine_products( driver )

    for e in product_urls:

        parse_product( driver, f, category_handle, category_name, subcategory_handle, subcategory_name, e )

    print()

##########################################################

def parse_subcategory( driver, f, category_handle, category_name, subcategory_link, subcategory_name ):

    subcategory_handle = extract_handle_from_url( subcategory_link )

    driver.get( subcategory_link )

    helpers.wait_for_page_load( driver )

    num_pages = determine_number_of_pages( driver )

    print( "INFO: number of pages {} on {}".format( num_pages, subcategory_link ) )

    page = 1

    print( "INFO: parsing page {} / {}".format( page, num_pages ) )

    parse_page( driver, f, category_handle, category_name, subcategory_handle, subcategory_name )

    page += 1

    while page <= num_pages:
        print( "INFO: parsing page {} / {}".format( page, num_pages ) )

        driver.get( subcategory_link + '?page=' + str( page ) )

        helpers.wait_for_page_load( driver )

        parse_page( driver, f, category_handle, category_name, subcategory_handle, subcategory_name )

        page += 1

##########################################################

def determine_category_name( driver ):

    d0 = driver.find_element_by_id( "app" )
    d1 = d0.find_element_by_css_selector( "div[data-dmid='app-container']" )
    d2 = d1.find_element_by_css_selector( "div[data-dmid='main-container']" )
    d4 = d2.find_element_by_xpath( "div/div[@data-dmid='dm-modules-container']" )
    d5 = d4.find_element_by_css_selector( "div[data-dmid='modules-container']" )

    d6 = d5.find_element_by_xpath( "div[@data-dmid='module-container']/div/div[@data-dmid='richtextContainer']/div[@data-dmid='richtext']/h1" )

    name = d6.text

    return name

##########################################################

def parse_category( driver, f, category_link ):

    category_handle = extract_handle_from_url( category_link )

    driver.get( category_link )

    helpers.wait_for_page_load( driver )

    helpers.sleep(2)

    category_name = determine_category_name( driver )

    print( "DEBUG: category name - {}".format( category_name ) )

    # "ostern" page has another structure, so we'll not bother us with parsing sub-categories
    #if category_link.find( "/ostern" ) != -1:
    #    parse_page( driver, f, category_handle, category_name, category_handle, category_name )
    #    return

    return

    links = determine_subcategories( driver )

    num_links = len( links )

    i = 0

    for c, name in links.items():

        i += 1

        print( "INFO: parsing subcategory {} / {} - {}".format( i, num_links, name ) )

        parse_subcategory( driver, f, category_handle, category_name, c, helpers.to_csv_conform_string( name ) )


##########################################################

def generate_filename():
    now = datetime.now()
    d1 = now.strftime( "%Y%m%d_%H%M" )
    res = "products_" + d1 + ".csv"
    return res

##########################################################
driver = helpers.init_driver( config.DRIVER_PATH, config.BROWSER_BINARY, harmonize_link( config.COOKIES_DIR ) + credentials.LOGIN )

driver.get( 'https://www.twitch.tv' )

helpers.sleep( 3 )

if is_logged_in( driver ) == False:

    accept_banner( driver )

    perform_login( driver )

    helpers.sleep( 5 )

    accept_welcome_screen( driver )

    accept_banner( driver )

# reopen the selected page again
driver.get( 'https://www.twitch.tv/directory/game/Dota%202?sort=VIEWER_COUNT' )

quit()

links = determine_categories( driver )

num_links = len( links )

f = open( generate_filename(), "w" )

i = 0

for c in links:

    i += 1

    print( "INFO: parsing category {} / {} - {}".format( i, num_links, c ) )

    parse_category( driver, f, c )

print( "INFO: done" )
