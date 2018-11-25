#!/usr/bin/python3
# akciók.py - scrapes deals from local grocery store websites, 
# remembers what I like at what prices. gets smarter each week.

import json
import argparse
import sys
import os
import random
import pprint
import readline
import requests
import getkey
from selenium import webdriver
from selenium.webdriver.common.keys import Keys    
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
#logging.disable()
logging.basicConfig(level=logging.DEBUG, format='%(lineno)d - %(asctime)s - %(levelname)s - %(message)s') #filename=f'log-akciok.txt', 
logging.debug("Start of program.")

parser = argparse.ArgumentParser(description='Scrape specials from grocery store websites.')
parser.add_argument('-b', '--buspass', dest="buspass", action='store_true', help='Do you have a buspass?')
parser.add_argument('-m', '--meat', dest='meat', type=float, help='How many kg meat?', nargs='?', default='1')
parser.add_argument('-v', '--veg', dest='veg', type=float, help='How many kg vegetables?', nargs='?', default='1')
args = parser.parse_args()
logging.debug(f"args: {args}")

def getDirectory():
    '''return the directory where the files are stored'''
    abspath = os.path.abspath(__file__)
    fileDirectory = os.path.dirname(abspath) + '/files/'
    return fileDirectory

def loadFiles():
    """Load all the files in the files directory.  Return a dict of files and
    their contents.
    """
    jsonFiles = os.listdir(getDirectory())
    jsonFiles.sort()
    allFiles = {}
    for file in jsonFiles:
        with open(getDirectory() + file, "r") as f:
            allFiles[file] = json.loads(f.readline().rstrip())
    return allFiles

def saveFiles(files):
    '''Save everything we learned in json format for next time'''
    for file in files:
        with open(getDirectory() + file, "w") as f:
            f.write(json.dumps(files[file]))

def setupFiles(files):
    '''Create all the files we need'''
    logging.debug(f'Files: {files}')
    while not files['websites'] or again("Add a new website? [y/N]"):
        siteName = input('Name of site: ')
        urlHead = input('Enter a URL to visit: ')
        urlTail = input('What should be appended to URLs from this site? (e.g. ?sort=cheapest')
        files['websites'][siteName] = [urlHead, urlTail]
    if 'parsewebsite' not in files.keys():
        files['parsewebsite'] = {}
    for website in files['websites']:
        logging.debug(f'Files["websites"]: {files["websites"]}')
        logging.debug(f'website: {website}')
        if website not in files['parsewebsite'].keys():
            print(f'\nMissing parsing data for {website.capitalize()}:\n')
            files['parsewebsite'][website] = adjustWebsiteParser()
            logging.debug(f'files["parsewebsite"]: {files["parsewebsite"]}')
    if 'blacklist' not in files.keys(): # ['eggplant', 'liver']
        files['blacklist'] = []
    if 'whitelist' not in files.keys(): # {'onion' : 150, 'chicken breast' : 1200}
        files['whitelist'] = {}
    return files

def adjustWebsiteParser(website=None):
    if not website:
        website={}
    '''What tags to look for in each website + whether a bus pass is needed to access the store'''
    website['itemdelineator'] = input('Html to look for at the start of each item: ')
    website['unitprice'] = input('Html element for unitprice: ')
    website['kgprice'] = input('Html element for kgprice: ')
    website['itemname'] = input('Html element for item name ')
    website['categories'] = input('Html element for categories: ')
    website['buspass'] = again('Buspass required for store? [y/N] ')
    logging.debug(f'website: {website}')
    return website

def again(msg='Again? [y/N]', default="no"):
    '''return true or false'''
    whatDo = input(msg + ' ') or default
    if whatDo[0].upper() == 'yes'.upper():
        return True
    else:
        return False

memory = setupFiles(loadFiles())
logging.debug(pprint.pprint(memory))
saveFiles(memory)

    # HOW TO PARSE EACH SITE
            #TESCO 
            #<div class="title">
            # <b class="name">
            # Hajnal lecsókolbász                                            </b>
            # <span class="description">
            # kétféle, csemegepultban kapható                                        </span>
            # <span>(1 kg = 890 Ft)</span>
            # </div>

            # pseudocode:
            # tesco = {'itemdelineator' : '<div class="a-productListing__productsGrid__element">',
            #'unitprice' : '<b class="new-price">PRICE',
            #    'kgprice' : '<span class="description">(1 kg = PRICE)<span>',
            #   'itemname' : '<b class="name">NAME',
            #   'categories' : '<li class="a-categories__list__item ">'
            #    'buspass' : False,
            # }
            #
            # AUCHAN
            #  <div class="box p10px prodItem">
      #<a href="https://www.auchan.hu/termekek/reszletek/friss-elelmiszer/tojas/friss-tojas-24" title=" FRISS TOJÁS"  class="title red"> FRISS TOJÁS</a>
   #<span><a href="https://www.auchan.hu/termekek/reszletek/friss-elelmiszer/tojas/friss-tojas-24" title=" FRISS TOJÁS" ><img src="https://www.auchan.hu/userfiles//e/b/ebf3c2bf98a69da70241fb7f546866c2_thum_185x138.png" alt=""></a></span>
   #<strong class="red featuredPrice">35 Ft</strong>
#            <p>Kiszerelés:Ft/db<br>
            #
            # auchan = { 'itemdelineator' : '<div class="box p10px prodItem">',
            #    'unitprice' : '<strong class="red featuredPrice">',
            #    'kgprice' : ' <p>Kiszerelés:PRICEg<br>', # do some math to this
            #   'itemname' : '<div class=box p10px prodItem><a href>',
            #   'categories' : '<ul class="submenu"><li class="">'
            #    'buspass' : True,
            # }
            #
            # LIDL
            #
            # <li class="
#          productgrid__item" data-currency="HUF" data-id="27035" data-name="Narancs" data-position="2" data-price="249" data-tracking="gtm" data-tracking-type="EECproduct" data-list="Ajánlataink/Zöldség és gyümölcs akcióink">

            #
            # lidl = { 'itemdelineator' : '<li class="productgrid__item',
            #'unitprice' : '<li class=productgrid__item data-price=PRICE',
            #    'kgprice' : '<span class="pricefield__footer" data-controller="pricefield/footer">150 g,&nbsp; 1 kg = 1994 Ft</span>', # do some math to this
            #   'itemname' : '<li class=productgrid__item data-name=NAME>',
            #   'categories' : '<li class="navigation__item"><a class="navigation__link">'
            #    'buspass' : False,
            # }
            #
            # PENNY
            # penny = {'itemdelineator' : '<div class="card card-hover h-100 rounded-0 cursor-pointer" data-toggle="modal" data-target="#productDetailsModal1">',
            # 'unitprice' : '<div class="col-8 px-0 penny-red-well-color h3 d-block offers-module-text-price-font">\n<div class="">\n<strong>PRICE Ft</strong>',
            #    'kgprice' : '<div class="text-muted col-12 px-0 h6 d-block text-right offers-module-text-font" style="height: 17px;">\n<span>100</span> <span>gramm</span> = <span>100</span>', # do some math to this
            #   'itemname' : '<h5 class="m-0 well-dark-grey-color modal-article-title bigger-line-height">NAME</h5>',
            #   'categories' : None,
            #    'buspass' : False,
            #}
            #
            # ALDI
            # aldi = {'itemdelineator' : '<a class="box--wrapper ym-gl ym-g25 " title="Tovább a termék leírásához">'}
            # 'unitprice' : '<span class="box--value">',
            #    'kgprice' : '<span class="box--baseprice">PRICE Ft/kg</span>', # do some math
            #   'itemname' : '<div class="box--description--header">NAME</div>',
            #   'categories' : '<li class="footer-sitemap--list--item dropdown--list--item">',
            #    'buspass' : True,
            #}

#TODO: For each website

    #load the website

    #detect categories
        #if category not in blacklist
            #if category not in whitelist
                #ask about category
            #if category in whitelist
                #traverse category


    #traverse categories

        #if item not in blacklist            
            #if item not in whitelist
                #ask about item: 
                    #yes at this price
                    #yes at this price but not this week
                    #yes but not this brand
                    #yes but only at lower price
                    #no never
                    #store english name for supercook
                    #save json file
                #learn category
            #if item in whitelist and price okay
                #add item to potential list

    #compile 2-3 sample menus of x kg meat, y kg vegetables, z miscellaneous items
    #search supercook for recipes

#search supercook
    #https://www.supercook.com/#/recipes

#sort menus by cheapest total price

#foreach menu
    #display store, shopping list, price, supercook recipes