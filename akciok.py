#!/usr/bin/python3
# akciók.py - scrapes deals from local grocery store websites, 
# remembers what I like at what prices. gets smarter each week.

import json
import argparse
import sys
import random
import pprint
import readline
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys    
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
#logging.disable()
logging.basicConfig(filename=f'log-akciok.txt', level=logging.DEBUG, format='
%(asctime)s - %(levelname)s - %(message)s')
logging.debug("Start of program.")

websites = {'tesco' : ['https://tesco.hu/akciok/akcios-termekek/', '?sort=cheapest']
            'auchan' : ['https://www.auchan.hu/akcio/', '/mind/48',]
            'lidl' : ['https://www.lidl.hu/hu/Ajanlataink.htm', '']
            'penny': ['https://www.penny.hu/offers', '']
            'aldi' : ['https://www.aldi.hu/hu/ajanlatok', '']
            #'real' : "http://real.hu/",  #requires OCR
            #'spar' : "https://sparajanlatok.kolrus.cloud/akcios_ujsag/spar-akcios-ujsag-DATE-DATEPLUSSEVENDAYS/2850/PAGENUMBER", # requies OCR
            #'coop' : "http://www.coop.hu/", #requires OCR
            }

#PARSE ARGS: WEBSITES TO TRAVERSE, HOW MANY KG MEAT, HOW MANY KG VEGETABLES, BUSPASS = TRUE/FALSE

#LOAD JSON FILES
    # USER'S PREVIOUS SHOPPING PREFERENCES
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
            #'unitprice' : '<b class="new-price">',
            #    'kgprice' : '<span class="description">(1 kg = \d+)<span>',
            #   'itemname' : '<b class="name">',
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
            #    'kgprice' : ' <p>Kiszerelés:\dg<br>', # do some math to this
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
            # 'unitprice' : '<div class="col-8 px-0 penny-red-well-color h3 d-block offers-module-text-price-font">
            #                                <div class="">
            #                                    <strong>PRICE Ft</strong>',
            #    'kgprice' : '<div class="text-muted col-12 px-0 h6 d-block text-right offers-module-text-font" style="height: 17px;">
            #                                
            #                                
            #                                    
            #                                        <span>100</span> <span>gramm</span> = <span>100</span>', # do some math to this
            #   'itemname' : '<h5 class="m-0 well-dark-grey-color modal-article-title bigger-line-height">NAME</h5>',
            #   'categories' : None,
            #    'buspass' : False,
            #}
            #
            # ALDI
            # aldi = {'itemdelineator' : '<a class="box--wrapper ym-gl ym-g25 " title="Tovább a termék leírásához">'}
            # 'unitprice' : '<span class="box--value">',
            #    'kgprice' : '<span class="box--baseprice">1 398 Ft/kg</span>', # do some math
            #   'itemname' : '<div class="box--description--header">NAME</div>',
            #   'categories' : '<li class="footer-sitemap--list--item dropdown--list--item">',
            #    'buspass' : True,
            #}

#FOREACH WEBSITE

    #LOAD WEBSITE

    #DETECT CATEGORIES
        #IF CATEGORY NOT IN BLACKLIST
            #IF CATEGORY NOT IN WHITELIST
                #ASK ABOUT CATEGORY
            #IF CATEGORY IN WHITELIST
                #TRAVERSE CATEGORY


    #TRAVERSE CATEGORIES

        #IF ITEM NOT IN BLACKLIST            
            #IF ITEM NOT IN WHITELIST
                #ASK ABOUT ITEM: 
                    #YES AT THIS PRICE
                    #YES AT THIS PRICE BUT NOT THIS WEEK
                    #YES BUT NOT THIS BRAND
                    #YES BUT ONLY AT LOWER PRICE
                    #NO NEVER
                    #STORE ENGLISH NAME FOR SUPERCOOK
                    #SAVE JSON FILE
                #LEARN CATEGORY
            #IF ITEM IN WHITELIST AND PRICE OKAY
                #ADD ITEM TO POTENTIAL LIST

    #COMPILE 2-3 SAMPLE MENUS OF X KG MEAT, Y KG VEGETABLES, Z MISCELLANEOUS ITEMS
    #SEARCH SUPERCOOK FOR RECIPES

#SEARCH SUPERCOOK
    #https://www.supercook.com/#/recipes

#SORT MENUS BY CHEAPEST TOTAL PRICE

#FOREACH MENU
    #DISPLAY STORE, SHOPPING LIST, PRICE, SUPERCOOK RECIPES