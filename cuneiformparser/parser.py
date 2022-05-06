import antlr4
from antlr4.error import DiagnosticErrorListener
from antlr4 import BailErrorStrategy
from antlr4 import PredictionMode
import pandas as pd
from contextlib import ExitStack
from os import path
import re
import itertools

try:
    from .grammar import CuneiformLexer
    from .grammar import CuneiformParser
except:
    from grammar import CuneiformLexer
    from grammar import CuneiformParser

try:
    from .listener import Listener
except:
    from listener import Listener

class ErrorListener(antlr4.error.ErrorListener.ErrorListener):

    def __init__(self):
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append([line-1, column, offendingSymbol.text.replace('\n', r'\n') if offendingSymbol else '', msg.replace('\n', r'\n')])

    #def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
    #    print('Ambiguity:', dfa, exact, ambigAlts)

    #def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
    #    print('Conflict:', dfa, conflictingAlts)

    #def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
    #    print('Context:', dfa, prediction)


def parse(text, language, stem):
    input = antlr4.InputStream(text)
    lexer = CuneiformLexer(input)
    stream = antlr4.CommonTokenStream(lexer)
    parser = CuneiformParser(stream)

    #parser._interp.predictionMode = PredictionMode.SLL

    #parser.setTrace(True)

    errorListener = ErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(errorListener)
    parser.removeErrorListeners()        
    #parser.errHandler = BailErrorStrategy()
    parser.addErrorListener(errorListener)

    tree = parser.text()
    listener = Listener(errorListener, language, stem)
    walker = antlr4.ParseTreeWalker()
    walker.walk(listener, tree)

    signs =     pd.DataFrame(listener.signs, 
                             columns=['line_no', 
                                      'word_no', 
                                      'value', 
                                      'signSpec', 
                                      'sign_type',  
                                      'indicator', 
                                      'alignment', 
                                      'phonographic',
                                      'condition',
                                      'stem',
                                      'crits', 
                                      'comment',
                                      'newline',
                                      'inverted',
                                      'ligature'])
    compounds = pd.DataFrame(listener.compounds,
                             columns=['pn_type', 
                                      'language',
                                      'section',
                                      'comment'])
    words =     pd.DataFrame(listener.words,
                             columns=['compound_no', 
                                      'capitalized'])
    errors =    pd.DataFrame(errorListener.errors,
                             columns=['line', 
                                      'column', 
                                      'symbol', 
                                      'msg'])
    return signs, compounds, words, errors
    

def parseLines(lines, language, stem):

    OBJECT = re.compile(r'@(?P<custom>object\s+)?(?P<object>(?(custom).*|(?:tablet|envelope)))')
    SURFACE = re.compile(r'@(?P<surface>obverse|reverse|top|bottom|left|right|surface|seal|fragment)(?:\s+(?P<data>[^?!*]*))?(?:\s*(?P<comment>[?!*]+))?')
    BLOCK = re.compile(r'@(?P<block>block|(?P<col>column))(?:\s+(?P<data>(?(col)[1-9][0-9]*\'*|[^?!*]*)))?(?:\s*(?P<comment>[?!*]+))?')

    class State:
        def __init__(self, object):
            self.object = object
            self.validSurface = False
            self.validBlock = False

            self.blocks = []
            self.surfaces = []
            self.objects = []
            self.lines = []
            self.content = []

        def addSurface(self, surface, data, comment):
            self.surfaces.append([self.object, surface, data, comment])
            self.validSurface = True
            self.validBlock = False

        def addBlock(self, block, data, comment):
            if not self.validSurface:
                self.addSurface(None, None, None)
            self.validBlock = True
            self.blocks.append([self.object, len(self.surfaces)-1, block or None, data, comment])

        def addLine(self, line, comment, content):
            if not self.validBlock:
                self.addBlock(None, None, None)
            self.lines.append([self.object, len(self.blocks)-1, line, comment])
            self.content.append(content)

        def parse(self, language, stem):
            self.signs, self.compounds, self.words, self.errors = parse('\n'.join(self.content), language, stem)
            self.signs.insert(0, 'object', self.object)
            self.compounds.insert(0, 'object', self.object)
            self.words.insert(0, 'object', self.object)
            self.errors.insert(0, 'object', self.object)
            self.errors = self.errors.merge(pd.DataFrame({'line': list(range(len(self.content))), 'content': self.content}), on='line')


    state = State('')
    states = []

    for line in lines:
        if not line:
            continue
        if m := OBJECT.fullmatch(line):
            if len(state.content):
                states.append(state)
            state = State(m.group('object'))
        elif m := SURFACE.fullmatch(line):
            state.addSurface(m.group('surface'), m.group('data'), m.group('comment'))
        elif m := BLOCK.fullmatch(line):
            state.addBlock(m.group('block'), m.group('data'), m.group('comment'))
        else:
            try:
                line, rest = line.split('\t', 1)
            except:
                print(line)
                continue
            content, *comment = re.split('\s+#\s*', rest, 1)
            comment = comment[0] if comment else None
            state.addLine(line, comment if comment else None, content)

    if len(state.content):
        states.append(state)
    
    if not states:
        return None

    for state in states:
        state.parse(language, stem)

    objects = pd.DataFrame({'object': [state.object for state in states]})
    surfaces = pd.DataFrame([x for state in states for x in state.surfaces], columns=['object', 'surface', 'data', 'comment'])
    blocks = pd.DataFrame([x for state in states for x in state.blocks], columns=['object', 'surfaceNo', 'block', 'data', 'comment'])
    lines = pd.DataFrame([x for state in states for x in state.lines], columns=['object', 'blockNo', 'line', 'comment'])

    signs = pd.concat([state.signs for state in states])
    compounds = pd.concat([state.compounds for state in states])
    words = pd.concat([state.words for state in states])
    errors = pd.concat([state.errors for state in states])

    return objects, surfaces, blocks, lines, signs, compounds, words, errors


def parseText(text, language, stem):
    return parseLines([line.strip(' \n\r\f\v') for line in text.split('\n')], language, stem)


def parseFile(path, target, language, stem, corpus):

    def write(files, tables, identifier, corpus):
        if tables is not None:
            transliterations = tables[0]
            transliterations.insert(0, 'transliterationIdentifier', corpus+identifier)
            transliterations.insert(0, 'identifier', identifier)
            transliterations.insert(3, 'description', corpus)
            transliterations.to_csv(files[0], index=False, header=False, sep=',', na_rep=r'\N')
            for of, table in zip(files[1:], tables[1:]):
                table.insert(1, 'index', table.index)
                table.insert(0, 'transliterationIdentifier', corpus+identifier)
                table.to_csv(of, index=False, header=False, sep=',', na_rep=r'\N')

    tables = ['transliterations', 'surfaces', 'blocks', 'lines', 'signs', 'compounds', 'words', 'errors']
    filenames = target if isinstance(target, list) else [path.join(target, x+'csv') for x in tables]
    identifier = None
    lines = []
    with ExitStack() as stack:
        f = stack.enter_context(open(path))
        ofiles = [stack.enter_context(open(x, 'w')) for x in filenames]
        for line in f:
            line = line.strip(' \n\r\f\v')
            if m := re.match(r'^@text\s+(.+)', line):
                if identifier is not None:
                    print(identifier)
                    write(ofiles, parseLines(lines, language, stem), identifier, corpus)
                identifier = m.group(1)
                lines = []
            elif line:
                if identifier is None:
                    print('Blah')
                lines.append(line)
        write(ofiles, parseLines(lines, language, stem), identifier, corpus)
