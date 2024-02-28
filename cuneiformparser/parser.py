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

SIGNS_COLS = [
    'line_no', 
    'word_no', 
    'value', 
    'sign_spec', 
    'type',  
    'indicator_type',
    'phonographic',
    'condition',
    'stem',
    'crits', 
    'comment',
    'newline',
    'inverted',
    'ligature',
    'start_col',
    'stop_col'
]

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

    signs =     pd.DataFrame(listener.signs,columns=SIGNS_COLS)
    compounds = pd.DataFrame(listener.compounds,
                             columns=['pn_type', 
                                      'language',
                                      'section_no',
                                      'comment'])
    compounds['section_no'] = compounds['section_no'].astype('Int64', copy=False)
    compounds['section_no'].replace(-1, pd.NA, inplace=True)
    words =     pd.DataFrame(listener.words,
                             columns=['compound_no', 
                                      'capitalized'])
    sections =  pd.DataFrame(listener.sections,
                             columns=['composition'])
    errors =    pd.DataFrame(errorListener.errors,
                             columns=['line_no', 
                                      'column', 
                                      'symbol', 
                                      'msg'])
    return signs, compounds, words, sections, errors
    

def parseLines(lines, language, stem):

    SURFACE = re.compile(r'\s*@(?P<surface>obverse|reverse|top|bottom|left|right|surface|fragment)(?:\s+(?P<data>[^?!*]*))?(?:\s*(?P<comment>[?!*]+))?\s*')
    BLOCK = re.compile(r'\s*@(?P<block>block|(?P<col>column|summary))(?:\s+(?P<data>(?(col)[1-9][0-9]*[a-g]?(?:\'+|[′″‴⁗])?(?:-[1-9][0-9]*[a-g]?(?:\'+|[′″‴⁗])?)?|[^?!*]*)))?(?:\s*(?P<comment>[?!*]+))?\s*')
    COMMENT = re.compile(r'\s*#\s*(?P<comment>.*)')

    class State:
        def __init__(self):
            self.validSurface = False
            self.validBlock = False

            self.surfaces = []
            self.blocks = []
            self.lines = []
            self.content = []
            self.lineNos = []
            self.colOffsets = []

            self.errorList = []

            self.lastAdded = None

        def convertToPrimes(text):
            if text is not None:
                text = text.replace("''''", "⁗")
                text = text.replace("'''", "‴")
                text = text.replace("''", "″")
                text = text.replace("'", "′")
            return text

        def addSurface(self, surface, data, comment):
            self.surfaces.append([surface, data, comment])
            self.validSurface = True
            self.validBlock = False
            self.lastAdded = self.surfaces[-1]

        def addBlock(self, block, data, comment):
            if not self.validSurface:
                self.addSurface('surface', None, None)
            self.validBlock = True
            self.blocks.append([len(self.surfaces)-1, block or None, State.convertToPrimes(data), comment])
            self.lastAdded = self.blocks[-1]

        def addLine(self, line, comment, content, lineNo):
            if not self.validBlock:
                self.addBlock('block', None, None)
            self.lines.append([len(self.blocks)-1, State.convertToPrimes(line), comment])
            self.content.append(content.strip())
            self.lineNos.append(lineNo)
            m = re.match(r'^\s*', content)
            self.colOffsets.append(len(line)+1+m.end())
            self.lastAdded = self.lines[-1]

        def addError(self, line, column, symbol, msg):
            self.errorList.append([line, column, symbol, msg])

        def parse(self, language, stem):
            lineInfo = pd.DataFrame({
                'line_no': list(range(len(self.lineNos))), 
                'line_no_code': self.lineNos, 
                'colOffset': self.colOffsets})

            signs, self.compounds, self.words, self.sections, errors = parse('\n'.join(self.content), language, stem)
            signs = signs.merge(lineInfo, on='line_no')
            signs['start_col_code'] = signs['start_col'] + signs['colOffset']
            signs['stop_col_code'] = signs['stop_col'] + signs['colOffset']
            self.signs = signs[SIGNS_COLS+['line_no_code', 'start_col_code', 'stop_col_code']]
            errors = errors.merge(lineInfo, on='line_no')
            errors['line_no'] = errors['line_no_code']
            errors['column'] = errors['column'] + errors['colOffset']
            self.errors = pd.concat([
                    pd.DataFrame(self.errorList, columns=['line_no', 'column', 'symbol', 'msg']), 
                    errors[['line_no', 'column', 'symbol', 'msg']]
                ], 
                ignore_index=True).sort_values(['line_no', 'column'])


    state = State()

    for lineNo, line in enumerate(lines):
        if not line.strip(' \n\r\f\v'):
            continue
        m = SURFACE.fullmatch(line)
        if m:
            state.addSurface(m.group('surface'), m.group('data'), m.group('comment'))
            continue
        m = BLOCK.fullmatch(line)
        if m:
            state.addBlock(m.group('block'), m.group('data'), m.group('comment'))
            continue

        m = COMMENT.fullmatch(line)
        if m:
            state.lastAdded[-1] = state.lastAdded[-1] + ' ' + m.group('comment') if state.lastAdded[-1] else m.group('comment')
            continue
        
        try:
            line, rest = line.split('\t', 1)
        except:
            state.addError(lineNo, 0, None, f'Invalid line: {lineNo}')
            continue
        content, *comment = re.split('\s+#\s*', rest, 1)
        comment = comment[0].strip() if comment else None
        state.addLine(line, comment if comment else None, content, lineNo)
    
    state.parse(language, stem)

    surfaces = pd.DataFrame(state.surfaces, columns=['surface', 'data', 'comment'])
    blocks = pd.DataFrame(state.blocks, columns=['surface_no', 'block', 'data', 'comment'])
    lines = pd.DataFrame(state.lines, columns=['block_no', 'line', 'comment'])
    sections = state.sections

    return surfaces, blocks, lines, state.signs, state.compounds, state.words, sections, state.errors


def parseText(text, language, stem):
    return parseLines(text.split('\n'), language, stem)


def parseFile(path, target, language, stem, corpus):

    def write(files, tables, identifier, corpus):
        if tables is not None:
            for of, table in zip(files, tables):
                table.insert(0, 'index', table.index)
                table.insert(0, 'transliterationIdentifier', corpus+identifier)
                table.to_csv(of, index=False, header=False, sep=',', na_rep=r'\N')

    tables = ['surfaces', 'blocks', 'lines', 'signs', 'compounds', 'words', 'sections', 'errors']
    filenames = target if isinstance(target, list) else [path.join(target, x+'csv') for x in tables]
    transliterations = []
    identifier = None
    lines = []
    with ExitStack() as stack:
        f = stack.enter_context(open(path))
        ofiles = [stack.enter_context(open(x, 'w')) for x in filenames[1:]]
        for line in f:
            m = re.match(r'^\s*@text\s+(.+)', line)
            if m:
                if identifier is not None:
                    print(identifier)
                    transliterations.append([identifier, corpus+identifier, corpus])
                    write(ofiles, parseLines(lines, language, stem), identifier, corpus)
                identifier = m.group(1)
                lines = []
            else:
                if line.strip() and identifier is None:
                    print(f'Warning: Line outside of text: "{line}".')
                lines.append(line)
        print(identifier)
        transliterations.append([identifier, corpus+identifier, corpus])
        write(ofiles, parseLines(lines, language, stem), identifier, corpus)
    pd.DataFrame(transliterations).to_csv(filenames[0], index=False, header=False, sep=',', na_rep=r'\N')    
