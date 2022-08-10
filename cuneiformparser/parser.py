import antlr4
from antlr4.error import DiagnosticErrorListener
from antlr4 import BailErrorStrategy
from antlr4 import PredictionMode
import pandas as pd
from contextlib import ExitStack
import re

try:
    from grammar.CuneiformLexer import CuneiformLexer
    from grammar.CuneiformParser import CuneiformParser
except:
    from .grammar.CuneiformLexer import CuneiformLexer
    from .grammar.CuneiformParser import CuneiformParser

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
                                      'sign_spec', 
                                      'type',  
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

    OBJECT = re.compile(r'@(?P<object>tablet|envelope|seal|object)(?:\s+(?P<data>[^?!*]*))?(?:\s*(?P<comment>[?!*]+))?')
    SURFACE = re.compile(r'@(?P<surface>obverse|reverse|top|bottom|left|right|surface|fragment)(?:\s+(?P<data>[^?!*]*))?(?:\s*(?P<comment>[?!*]+))?')
    BLOCK = re.compile(r'@(?P<block>block|(?P<col>column))(?:\s+(?P<data>(?(col)[1-9][0-9]*\'*|[^?!*]*)))?(?:\s*(?P<comment>[?!*]+))?')

    class State:
        def __init__(self):
            self.validObject = False
            self.validSurface = False
            self.validBlock = False

            self.objects = []
            self.surfaces = []
            self.blocks = []
            self.lines = []
            self.content = []

        def addObject(self, object, data, comment):
            self.objects.append([object, data, comment])
            self.validObject = True
            self.validSurface = False
            self.validBlock = False

        def addSurface(self, surface, data, comment):
            if not self.validObject:
                self.addObject('object', None, None)
            self.surfaces.append([len(self.objects)-1, surface, data, comment])
            self.validSurface = True
            self.validBlock = False

        def addBlock(self, block, data, comment):
            if not self.validSurface:
                self.addSurface('surface', None, None)
            self.validBlock = True
            self.blocks.append([len(self.surfaces)-1, block or None, data, comment])

        def addLine(self, line, comment, content):
            if not self.validBlock:
                self.addBlock('block', None, None)
            self.lines.append([len(self.blocks)-1, line, comment])
            self.content.append(content)

        def parse(self, language, stem):
            self.signs, self.compounds, self.words, self.errors = parse('\n'.join(self.content), language, stem)
            self.errors = self.errors.merge(pd.DataFrame({'line': list(range(len(self.content))), 'content': self.content}), on='line')


    state = State()

    for line in lines:
        if not line:
            continue
        m = OBJECT.fullmatch(line)
        if m:
            state.addObject(m.group('object'), m.group('data'), m.group('comment'))
            continue
        m = SURFACE.fullmatch(line)
        if m:
            state.addSurface(m.group('surface'), m.group('data'), m.group('comment'))
            continue
        m = BLOCK.fullmatch(line)
        if m:
            state.addBlock(m.group('block'), m.group('data'), m.group('comment'))
            continue
        
        try:
            line, rest = line.split('\t', 1)
        except:
            print(line)
            continue
        content, *comment = re.split('\s+#\s*', rest, 1)
        comment = comment[0] if comment else None
        state.addLine(line, comment if comment else None, content)
    
    if not state.objects:
        return None

    state.parse(language, stem)

    objects = pd.DataFrame(state.objects, columns = ['object', 'data', 'comment'])
    surfaces = pd.DataFrame(state.surfaces, columns=['object_no', 'surface', 'data', 'comment'])
    blocks = pd.DataFrame(state.blocks, columns=['surface_no', 'block', 'data', 'comment'])
    lines = pd.DataFrame(state.lines, columns=['block_no', 'line', 'comment'])

    return objects, surfaces, blocks, lines, state.signs, state.compounds, state.words, state.errors


def parseText(text, language, stem):
    return parseLines([line.strip(' \n\r\f\v') for line in text.split('\n')], language, stem)


def parseFile(path, target, language, stem, corpus):

    def write(files, tables, identifier, corpus):
        if tables is not None:
            for of, table in zip(files, tables):
                table.insert(0, 'index', table.index)
                table.insert(0, 'transliterationIdentifier', corpus+identifier)
                table.to_csv(of, index=False, header=False, sep=',', na_rep=r'\N')

    tables = ['objects', 'surfaces', 'blocks', 'lines', 'signs', 'compounds', 'words', 'errors']
    filenames = target if isinstance(target, list) else [path.join(target, x+'csv') for x in tables]
    transliterations = []
    identifier = None
    lines = []
    with ExitStack() as stack:
        f = stack.enter_context(open(path))
        ofiles = [stack.enter_context(open(x, 'w')) for x in filenames[1:]]
        for line in f:
            line = line.strip(' \n\r\f\v')
            m = re.match(r'^@text\s+(.+)', line)
            if m:
                if identifier is not None:
                    print(identifier)
                    transliterations.append([identifier, corpus+identifier, corpus])
                    write(ofiles, parseLines(lines, language, stem), identifier, corpus)
                identifier = m.group(1)
                lines = []
            elif line:
                if identifier is None:
                    print('Blah')
                lines.append(line)
        print(identifier)
        transliterations.append([identifier, corpus+identifier, corpus])
        write(ofiles, parseLines(lines, language, stem), identifier, corpus)
    pd.DataFrame(transliterations).to_csv(filenames[0], index=False, header=False, sep=',', na_rep=r'\N')    
