from lexer_parser import Lexer, Parser
import argparse

ap = argparse.ArgumentParser(description = "A cross-compiler from markdown-like syntax to Desmos mathquill.")
ap.add_argument('text', nargs='?')
ap.add_argument('-d', '--debug', action='store_true')
ap.add_argument('-c', '--colour', nargs=1)

inp = ap.add_mutually_exclusive_group()
inp.add_argument('-i', '--interactive', action='store_true')
inp.add_argument('-f', '--file')

ap.add_argument('-x', '--choose', nargs=1)

fonts = ap.add_mutually_exclusive_group()
fonts.add_argument('-s', '--sans-serif', action='store_true')
fonts.add_argument('-r', '--roman', action='store_true')

justify = ap.add_mutually_exclusive_group()
justify.add_argument('-cj', '--center-justify', action='store_true')
justify.add_argument('-rj', '--right-justify', action='store_true')

args = ap.parse_args()

if args.debug:
    print('Command flags:', args)

defaults = set()
if args.sans_serif: defaults.add('sans-serif')
elif args.roman: defaults.add('roman')

if args.center_justify: justify = 'center'
elif args.right_justify: justify = 'right'
else: justify = 'left'

if args.debug:
    print('Default flags set:', defaults)

colour = '#000' if not args.colour else args.colour[0]

config = {'defaults': defaults, 'justify': justify, 'colour': colour}

lexer = Lexer()
parser = Parser()

def translate(text):
    if args.debug:
        print('\n[Input]')
        print(text)
        print(config)

    l = lexer.lex(text, args.debug)
    result = parser.parse(l, config, args.debug)
    
    if args.debug:
        print('\n[Output]')
    print(result)

if args.interactive:
    buffer = []
    while (text := input(r'>> Type \end to compile or \exit to leave >> ')) != r'\exit':
        if text != r'\end':
            buffer.append(text)
        else:
            translate('\n'.join(buffer))
            buffer = []
elif args.file:
    with open(args.file) as f:
        split = f.read().split('\n\n\\next\n\n')
        
        if args.choose:
            translate(split[int(args.choose[0])])
        else:
            for s in split:
                translate(s)
elif args.text:
    translate(args.text)
else:
    print('No text provided to parse.')