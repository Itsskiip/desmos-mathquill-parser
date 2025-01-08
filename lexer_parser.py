import rply

class Op:
    def __init__(self, *args):
        #print('Parsed operation', self.__class__.__name__, args)
        self.args = list(args)
        self.config = dict()
    
    def debug(self, depth=0):
        return f"\n{'\t'*depth}{self.__class__.__name__}({','.join(arg.debug(depth + 1) for arg in self.args)})" 
    
    def eval(self):
        raise NotImplementedError
    
    def apply_config(self, config, update=None):
        self.config = config

        if update:
            config = config.copy()
            to_upd = config[update[0]]

            if isinstance(to_upd, set):
                to_upd = to_upd.copy()
                to_upd.add(update[1])
                if update[1] in ('italics', 'sans-serif', 'teletype', 'roman'):
                    to_upd.discard('bold')
                if update[1] in ('roman', 'sans-serif', 'teletype'):
                    to_upd.discard('italics')
                if update[1] in ('sans-serif', 'teletype'):
                    to_upd.discard('roman')
                config[update[0]] = to_upd
            else:
                config[update[0]] = update[1]

        for arg in self.args:
            arg.apply_config(config)
def wrap_if_not_block(token):
    cl = token.__class__
    if cl is str:
        return f'{{{token}}}'
    elif cl in (Text, Concat):
        return f'{{{token.eval()}}}'
    else:
        return token.eval()

def cmd(command, *args):
    return rf'\{command}{''.join(map(wrap_if_not_block, args))}'

class Italics(Op):
    def eval(self):
        return cmd('mathit', self.args[0].eval())


    def apply_config(self, config):
        arg = self.args[0]
        if 'bold' in config['font']:
            arg = Bold(arg)
        self.args[0] = arg
        super().apply_config(config, ('font', 'italics'))

replace_map = {
    ' ': r'\ ',
    '--': '―',
    '-': '‒',
    }
with open('reserved_words.txt') as f:
    replace_map.update({f: f[:len(f)//2] + '\u200c' + f[len(f)//2:] for f in f.read().splitlines()})

class Text(Op):
    def debug(self, depth=0):
        depth_s = '\t'*depth
        return f'\n{depth_s}Text({self.args[0]})'
    def eval(self):
        text = self.args[0]
        for k, v in replace_map.items():
            text = text.replace(k, v)
        return text
        
    def apply_config(self, config):
        self.config = config

class Bold(Op):
    def eval(self):
        return cmd('mathbf', self.args[0].eval())

    def apply_config(self, config):
        super().apply_config(config, ('font', 'bold'))

class Teletype(Op):
    def eval(self):
        return cmd('mathtt', self.args[0].eval())

    def apply_config(self, config):
        arg = self.args[0]
        if 'bold' in config['font']:
            arg = Bold(arg)
        if 'italics' in config['font']:
            arg = Italics(arg)
        if 'roman' in config['font']:
            arg = Roman(arg)
        self.args[0] = arg
        super().apply_config(config, ('font', 'teletype'))

class SansSerif(Op):
    def eval(self):
        return cmd('mathsf', self.args[0].eval())

    def apply_config(self, config):
        arg = self.args[0]
        if 'bold' in config['font']:
            arg = Bold(arg)
        if 'italics' in config['font']:
            arg = Italics(arg)
        if 'roman' in config['font']:
            arg = Roman(arg)
        self.args[0] = arg
        super().apply_config(config, ('font', 'sans-serif'))

class Roman(Op):
    def eval(self):
        if 'roman' in self.config['font']:
            return self.args[0].eval()
        return cmd('mathrm', self.args[0].eval())
    
    def apply_config(self, config):
        arg = self.args[0]
        if 'roman' in config['font']:
            super().apply_config(config)
        else:
            if 'bold' in config['font']:
                arg = Bold(arg)
            if 'italics' in config['font']:
                arg = Italics(arg)
            self.args[0] = arg
            super().apply_config(config, ('font', 'roman'))

class MultilineHeader(Op):
    def eval(self, first = False):
        arg = self.args[0].eval()
        if self.config['justify'] == 'center':
            return cmd('textcolor', self.config['colour'], arg)
        elif self.config['justify'] == 'right':
            return ([arg], cmd('class', 'dcg-expression-bottom', f'\u200F{arg}{{next_line}}'))
        else:
            return [arg]
        
class LineJoin(Op):
    def eval(self, first = True):
        left = self.args[0].eval(False)
        right = self.args[1].eval()

        if self.config['justify'] == 'center':
            result = cmd('binom', left, cmd('textcolor', self.config['colour'], right))
            if first:
                return cmd('textcolor', 'transparent', result)
            else:
                return result

        elif self.config['justify'] == 'right':
            ls = left[0] + [right]
            result = left[1].replace('{next_line}', cmd('class', 'dcg-expression-bottom', f'\u200F{right}{{next_line}}'))
            if first:
                final_line = max(ls, key=len)
                return result.replace('{next_line}', cmd('textcolor', 'transparent', final_line))
            else:
                return (ls, result)
        else:
            ls = left + [right]
            if first:
                return cmd('class', 'dcg-search-container', ''.join(ls[:-1])) + ls[-1]
            else:
                return ls
            
class Big(Op):
    def eval(self):
        return cmd('class', 'dcg-displaysize-large', self.args[0])

class Smol(Op):
    def eval(self):
        return cmd('class', 'dcg-mq-sub', self.args[0])

class Colour(Op):
    def eval(self):
        code = self.args[0].eval()
        return cmd('textcolor', code , self.args[1])
    
    def apply_config(self, config):
        super().apply_config(config, ('colour', self.args[0].eval().upper()))

class Concat(Op):
    def eval(self):
        return self.args[0].eval() + self.args[1].eval()
    
def translated_len(s):
    return len()
class Paren(Op):
    def eval(self):
        return self.shortest_def.format(self.args[0].eval())
    
    def apply_config(self, config):
        super().apply_config(config)
        c = ""
        if 'sans-serif' in config['font']:
            c = 'mathsf'
        elif 'teletype' in config['font']:
            c = 'mathtt'
        elif 'roman' in config['font']:
            c = 'mathrm'
        elif 'italics' in config['font']:
            c = 'mathit'
        elif 'bold' in config['font']:
            c = 'mathbb'
        else:
            c = f'textcolor{{{self.config['colour']}}}'
        self.shortest_def = '\\' + c + '{{{}}}'
            
class Lexer:
    def __init__(self):
        lg = rply.LexerGenerator()
        lg.add('ROMAN', '~')
        lg.add('TELETYPE', '`')
        lg.add('BOLDITALICS', r'\*\*\*')
        lg.add('BOLD', r'\*\*')
        lg.add('ITALICS', r'\*')
        lg.add('MOD', r'#[+-]+ ?')
        lg.add('OPEN_BR', '{')
        lg.add('CLOSE_BR', '}')
        lg.add('COLOUR', r'\\c\d{6}')
        lg.add('BREAK', '\n')
        lg.add('F', r'f+')
        lg.add('STRING', r'[^\\*\n{}`~f]+')

        self.lexer = lg.build()

    def lex(self, s, debug=False):
        result = self.lexer.lex(s)
        if debug:
            print('\n[Lexer]\n')
            for l in self.lexer.lex(s):
                print(l, l.getsourcepos())
        return result
    

class Parser:
    def __init__(self):
        pg = rply.ParserGenerator(
        ['F', 'ROMAN', 'TELETYPE', 'ITALICS', 'BOLD', 'BOLDITALICS', 'MOD', 'COLOUR', 'OPEN_BR', 'CLOSE_BR', 'BREAK', 'STRING'],
        
        precedence=[
            ('left', ['BREAK']),
            ('left', ['STRING', 'F']),
            ('left', ['COLOUR']),
            ('left', ['MOD']),
            ('left', ['OPEN_BR', 'CLOSE_BR', 'BOLD', 'ROMAN', 'TELETYPE', 'ITALICS', 'BOLDITALICS']),
            ('left', ['CONCAT'])
        ])

        @pg.production('expr : STRING')
        def text(p):
            return Text(p[0].value)
        
        @pg.production('expr : F')
        def f(p):
            return Roman(Text(f'\u200c{p[0].value}\u200c'))
        
        @pg.production('expr : BOLD expr BOLD')
        def bold(p):
            return Bold(p[1])
        
        @pg.production('expr : BOLDITALICS expr BOLDITALICS')
        def boldit(p):
            return Italics(Bold(p[1]))
            
        @pg.production('expr : ITALICS expr ITALICS')
        def italics(p):
            return Italics(p[1])
            
        @pg.production('expr : TELETYPE expr TELETYPE')
        def teletype(p):
            return Teletype(p[1])
            
        @pg.production('expr : ROMAN expr ROMAN')
        def roman(p):
            return Roman(p[1])
        
        @pg.production('expr : expr BREAK expr')
        def joinline(p):
            for i in (0, 2):
                if p[i].__class__ in (Text, Concat):
                    p[i] = Paren(p[i])

            if p[0].__class__ in (LineJoin, MultilineHeader):
                return LineJoin(p[0], p[2])
            else:
                return LineJoin(MultilineHeader(p[0]), p[2])
            
        @pg.production('expr : MOD expr')
        def mod(p):
            expr = p[1]
            for op in p[0].value[1:]:
                if op == '+':
                    expr = Big(expr)
                elif op == '-':
                    expr = Smol(expr)
            return expr
            
        @pg.production('expr : COLOUR expr')
        def colour(p):
            return Colour(Text(p[0].value[1:]), p[1])
            
        @pg.production('expr : expr expr', precedence='CONCAT')
        def concat(p):
            return Concat(p[0], p[1])
            
        @pg.production('expr : OPEN_BR expr CLOSE_BR')
        def paren(p):
            return p[1]
        
        @pg.error
        def error(token):
            raise ValueError(f"Unexpected token {token.gettokentype()} at {token.getsourcepos()}")
        
        self.parser = pg.build()
    
    def parse(self, l, config = {}, debug = False):
        ast = self.parser.parse(l)
        if debug:
            print('\n[Parser]')
            print(ast.debug())
        if defaults := config.get('defaults'):
            if 'roman' in defaults:
                ast = Roman(ast)
            if 'sans-serif' in defaults:
                ast = SansSerif(ast)
                
        if (col := config.get('colour')) != 'black' and col != '#000' and col != '#000000':
            print(col)
            ast = Colour(Text(col), ast)
            
        config.update({'font': {'italics'}})
        ast.apply_config(config)
        result = ast.eval()

        return result
