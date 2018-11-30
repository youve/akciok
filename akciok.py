#!/usr/bin/python3
# akciók.py - scrapes deals from local grocery store websites, 
# remembers what I like at what prices. gets smarter each week.

import json
import argparse
import sys
import os
#import random
import pprint
import readline
import requests
#import getkey
import urllib
from bs4 import BeautifulSoup
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
        if os.path.isfile(getDirectory() + file):
            logging.debug(f'Loading {file}')
            with open(getDirectory() + file, "r") as f:
                allFiles[os.path.splitext(file)[0]] = json.load(f)
        else:
            logging.debug(f'{getDirectory() + file} is not a file.')
    return allFiles

def saveFiles(files):
    '''Save everything we learned in json format for next time'''
    for file in files:
        with open(getDirectory() + file + '.json', "w") as f:
            f.write(json.dumps(files[file], indent=4, sort_keys=True))

def setupFiles(files):
    '''Create all the files we need'''
    logging.debug(f'Files: {files}')
    while not files['websites'] or again("Add a new website? [y/N]"):
        siteName = input('Name of site (e.g. Lidl): ')
        baseURL = input('Base URL of site (e.g. https://www.lidl.com): ')
        catsURL = input('Enter a URL to find categories (e.g. https://www.lidl.com/specials): ')
        urlTail = input('What should be appended to URLs from this site? (e.g. ?sort=cheapest):')
        files['websites'][siteName] = {'base' : baseURL, 'cats' : catsURL, 'tail' : urlTail}
    if 'parsewebsite' not in files.keys():
        files['parsewebsite'] = {}
    for website in files['websites']:
        logging.debug(f'Files["websites"]: {files["websites"]}')
        logging.debug(f'website: {website}')
        if website not in files['parsewebsite'].keys():
            print(f'\nMissing parsing data for {website.capitalize()}:\n')
            files['parsewebsite'][website] = adjustWebsiteParser()
            logging.debug(f'files["parsewebsite"]: {files["parsewebsite"]}')
    if 'foodBlacklist' not in files.keys(): # ['eggplant', 'liver']
        files['foodBlacklist'] = []
    if 'foodWhitelist' not in files.keys(): # {'onion' : 150, 'chicken breast' : 1200}
        files['foodWhitelist'] = {}
    if 'categoryBlacklist' not in files.keys(): # ['Kertészet']
        files['categoryBlacklist'] = []
    if 'categoryWhitelist' not in files.keys(): # ['Zöldség, gyümölcs', 'Hús, hal, felvágott']
        files['categoryWhitelist'] = [] 
    return files

def adjustWebsiteParser(website=None):
    if not website:
        website={}
    '''What tags to look for in each website + whether a bus pass is needed to access the store'''
    print('''\nakciok.py needs to know how to find each category and each item on a page.
        You will need to view-source on the webpage and find something unique that
        BeautifulSoup.select can find. Look here if you need more help: https://www.crummy.com/software/BeautifulSoup/bs4/doc/index.html?highlight=select#css-selectors \n''')
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
    if whatDo[0].upper() == 'Y':
        return True
    else:
        return False

def findCategories(website):
    '''Returns a dictionary of categories to search: {catName: website, url}
    e.g.: {"vegetables" : ("tesco", "https://www.tesco.com/specials/vegetables")}'''
    logging.info(f'Finding categories in {website}')
    websiteUrls = memory['websites'][website]
    res = requests.get(websiteUrls['cats'])
    res.raise_for_status()
    websiteSoup = BeautifulSoup(res.text, "html.parser")
    cats = websiteSoup.select(memory['parsewebsite'][website]['categories'])
    categoriesToSearch = {}
    for cat in cats:
        catName = cat.getText().strip().lower()
        if catName not in memory['categoryBlacklist']:
            care = True
            if catName not in memory['categoryWhitelist']:
                if again(f"Do you care about {catName.capitalize()} [Y/n]", default="yes"):
                    logging.debug(f'Whitelisting {catName}')
                    memory['categoryWhitelist'].append(catName)
                else:
                    care = False
                    logging.debug(f"Blacklisting {catName}")
                    memory['categoryBlacklist'].append(catName)
            if care:
                if website == 'penny':
                    url = websiteUrls['cats'] + '?c=' + cats[0].input.attrs['value']
                else:
                    url = cat.attrs['href']
                if not url.startswith('http'):
                    url = urllib.parse.urljoin(websiteUrls['base'], url)
                    logging.debug(f'url: {url}')
                categoriesToSearch[catName] = (website, url)

    return categoriesToSearch

def findPages(website, url):
    '''Finds all pages in a given category at a URL and then returns a list of these pages'''
    logging.info(f'Finding pages.')
    pageurls = [url]
    res = requests.get(url)
    res.raise_for_status()
    websiteSoup = BeautifulSoup(res.text, "html.parser")
    #TODO: Does this work if there's only one page?
    pages = websiteSoup.select(memory['parsewebsite'][website]['pageseparator'])
    for page in pages:
        if page.attrs['href'].startswith('http'):
            pageurls.append(page.attrs['href'])
        else:
            pageurls.append(urllib.parse.urljoin(website, page.attrs['href']))
    return pageurls

def findItems(cat, website, url):
    '''Returns a dictionary of items that might be bought. 
    Example: a 10g packet of basil that costs 99 forints:
    {'basil' : ('9900', '99')}
    '''
    logging.info(f'Finding products in {cat} on {url}')
    pages = findPages(website, url)
    products = {}
    for page in pages:
        res = requests.get(page)
        res.raise_for_status()
        itemdelineator = websiteSoup.select(memory['parsewebsite'][website]['itemdelineator'])
        for index, items in enumerate(itemdelineator):
            itemname = itemdelineator[index].select(memory['parsewebsite'][website]['itemname'])
            kgprice = itemdelineator[index].select(memory['parsewebsite'][website]['kgprice'])
            unitprice = itemdelineator[index].select(memory['parsewebsite'][website]['unitprice'])
            products[itemname] = (kgprice, unitprice)
    return products

def considerProducts(products):
    '''Returns a dictionary of products to buy this week. Updates blacklists and whitelists.
    interested = {'item' : ('kgprice', 'unitprice')}
    '''
    for product, (kgprice, unitprice) in products:
        blacklisted = False
        interested = {}
        for item in memory[foodBlacklist]:
            if item in product:
                blacklisted = True
                break
        if blacklisted:
            continue
        if product in memory[foodWhitelist].keys():
            if kgprice <= foodWhitelist[product]:
                interested[product] = (kgprice, unitprice)
            else:
                continue
        # Ask user what to do:
        whatDo = input(f'''Are you interested in {product} for {unitprice}, {kgprice}/kg? 
            [Y]es/[x 500] not at this e[x]pense; 500 is the max I'd pay for it/[b STRING] blacklist this string.''').lower()
        if whatDo.startswith('x'):
            match = re.search('\d+', whatDo)
            while not match:
                whatDo = input("Max you'd pay for this item: ")
                match = re.search('\d+', whatDo)
            memory[foodWhitelist][product] = int(match)
        elif whatDo.startswith('b'):
            match = re.search('(b )(.*)', whatDo)
            while not match:
                whatDo = input('Substring to blacklist. Type nothing to blacklist the whole string: ') or 'b ' + product
                match = re.search('(b )(.*)', whatDo)
            memory[foodBlacklist].append(match.groups[1])
        else:
            interested[product] = (kgprice, unitprice)
            memory[foodWhitelist][product] = kgprice
    return interested

memory = setupFiles(loadFiles())
logging.debug(pprint.pprint(memory))
catsToSearch = {}

for website in memory['websites'].keys():
    catsToSearch[website] = findCategories(website)
    again('Keep going? [Y/n]', default="yes")

logging.debug(f'catsToSearch: {catsToSearch}')

interestingProducts = {}

for site in catsToSearch.keys():
    for category, (website, url) in catsToSearch[site].items():
        if website in interestingProducts.keys():
            interestingProducts[website].update(considerProducts(findItems(category, website, url)))
        else:
            interestingProducts[website] = considerProducts(findItems(category, website, url))
        if again(f'Finished {category}. Keep going? [Y/n]', default="yes"):
            continue
        else:
            #save results for later
            break



#TODO: For each website

    #load the website

    #traverse categories

        #if item not in foodBlacklist            
            #if item not in foodWhitelist
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

saveFiles(memory)