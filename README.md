# Specials

Akciok is a repository for processing grocery store specials and making decisions about what foods to buy each week.

## The Present

### akciok.py

akciok.py is a work in progress. So far it builds a list of local grocery websites, scans these websites for categories, and learns which categories the user cares about.

If you are using it for yourself, you may want to throw out the whitelists and blacklists in [files](https://github.com/youve/akciok/tree/master/files) because they contain sample data. If you don't live in Hungary, you may want to remove websites.json and parsewebsite.json too. akciok.py will walk you through setting those up for the websites you want to search. 

The first time you run the program, it will take a while to learn what you care about and what you don't, but as it learns more about you and your preferences, each run will be faster.

### Spreadsheet and Python script
`2018_prices.xlsx` is a spreadsheet that tracks how much various items cost at various stores in Hungary. It provides feedback on which food items provide the most calories / Hungarian Forint, the most potassium/serving, and which foods are the cheapest non-carbohydrate sources of energy.

`gen_excel.py` is a script that accompanies the spreadsheet that generates a formula for estimating the cost of buying a list of items at that store. The formula works in libreoffice calc, and I imagine it would work in openoffice and excel as well. 

For example if you want to buy chicken thighs, ginger, and kohlrabi:

1. Run `gen_excel.py 12 43 44` 
2. Paste the resulting excel formula into the grocery shopping row, into `B102`
3. Copy it with `ctrl-c`
4. Highlight the other cells in that row, `C102:J102`
5. Paste special with `ctrl-shift-v`
6. Check the "formulae" checkbox and uncheck the other checkboxes, then hit "Ok"

The cheapest store will be highlighted in green. The numbers don't reflect the exact amount you will pay at the store because it assumes you'll buy 1kg of everything, but the smallest number is still going to be the cheapest.

## The problem with the spreadsheet

These work well enough but the problem is keeping them updated. Stores change their prices every Thursday, and they only list the sale items on their website; last week's specials are removed. You can spend a few hours each week entering the new prices into the spreadsheet by hand, but there's no way to know about stale price data. The only way to keep it up to date would be to visit every store with a notebook and pen every week, which is a ridiculous waste of time.

## The Future

`akciok.py` is a paradigm shift. Each week, it will:

* scan the websites for the specials
* filter the results for stuff I actually care about
* blacklist products I'm never interested in
* learn which products I'm interested in at what price

In the beginning, it will need a lot of feedback from me about my interests, but over time, it will learn enough about my preferences to not have to ask for my feedback so much.

Eventually, it will be able to take an input like `1kg meat 2kg vegetables` and deliver an answer like:

1. Buy ground pork, butternut squash, onions, and carrots at Auchan for $amount
2. Buy chicken thighs, zucchini, tomatoes, and cauliflower at Lidl for $otheramount.

It might even search [Supercook](http://www.supercook.com) for recipes containing those ingredients.