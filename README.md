`2018_prices.xlsx` is a spreadsheet that tracks how much various items cost at various stores in Hungary. It provides feedback on which food items provide the most calories / Hungarian Forint, the most potassium/serving, and which foods are the cheapest non-carbohydrate sources of energy.

`gen_excel.py` is a script that accompanies the spreadsheet that generates an excel formula for estimating the cost of buying a list of items at that store. For example if you want to buy chicken thighs, ginger, and kohlrabi, you would run `gen_excel.py 12 43 44` and then you would paste the resulting excel formula into the grocery shopping row, in B102. Then you hit ctrl-c to copy it, highlight the other cells in that row, hit ctrl-shift-v to paste special and select only the "formulae" item. The cheapest store will be highlighted in green.

These work well enough but the problem is keeping them updated. Stores change their prices every Thursday, and they only list the sale items on their website; last week's specials are removed. The only way to keep it up to date would be to visit every store with a notebook and pen every week, which is ridiculous.

`akciok.py` will scan the websites each week for the specials, will filter the results for stuff I actually care about, will learn at what prices I begin to be interested in certain items, and will, eventually, be able to take an input like "1kg meat 2kg vegetables" and turn that into "Buy ground pork, butternut squash, onions, and carrots at Auchan for $amount or chicken thighs, zucchini, tomatoes, and cauliflower at Lidl for $otheramount." It might even search [Supercook](http://www.supercook.com) for recipes containing those ingredients. Alpha version coming soon.