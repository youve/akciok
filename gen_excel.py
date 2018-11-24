#!/usr/bin/python3

#for use with 2018_prices.ods
import readline
from optparse import OptionParser

parser = OptionParser()

(options, args) = parser.parse_args()

def gen_excel(rows, cols=['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']):
    #uses absolute references, so it can be easily copy pasted to the other cells
    #libreoffice calc will change col[0] to col[1] on its own where col[0] is not
    #preceded by a $.
    #If there's an error, prints "none" because otherwise the spreadsheet makes
    #value error be green which is dumb. i don't want to go to a store that doesn't
    #sell what i want.
    formula = "=IFERROR(SUM("
    for row in rows:
        formula += f"IF({cols[0]}{row};{cols[0]}{row};"
        formula += f"MEDIAN(${cols[0]}${row}:${cols[-1]}${row}));"
    formula += ');"none")'
    return formula

def which_rows(args):
    if len(args) < 1:
        args = input("enter rows as CSV: ").split(",")
    for index, row in enumerate(args[:]):
        try: 
            args[index] = int(row.strip(' "\''))
        except(ValueError): #only ints allowed. no empty strings
            del args[index]
    return gen_excel(args)

def main():
    print('\n' + which_rows(args) + '\n')

if __name__ == '__main__':
    main()