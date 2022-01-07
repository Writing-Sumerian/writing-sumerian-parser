import sys
import antlr4
from antlr4.error import DiagnosticErrorListener
from antlr4 import BailErrorStrategy
from antlr4 import PredictionMode
import pandas as pd
import re

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
                                      'condition', 
                                      'sign_type', 
                                      'phonographic', 
                                      'indicator', 
                                      'alignment', 
                                      'stem',
                                      'crits', 
                                      'comment',
                                      'newline',
                                      'inverted'])
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
    

OBJECT = re.compile(r'@(tablet|envelope|object .*)')
SURFACE = re.compile(r'@(obverse|reverse|top|bottom|left|right|surface .*|seal .*)')
SECTION = re.compile(r'@(section .*|column +[1-9][0-9]*\'*)')

def parseText(text, language, stem):
    content = []
    lines = []
    object = None
    surface = None
    section = None
    for line in text.split('\n'):
        line = line.rstrip()
        if not line:
            continue
        if OBJECT.fullmatch(line):
            object = re.sub(r'^@(object +)?', '', line)
            surface = None
            section = None
        elif SURFACE.fullmatch(line):
            surface = re.sub(r'^@(surface +)?', '', line)
            section = None
        elif SECTION.fullmatch(line):
            section = re.sub(r'^@(section|column) +', '', line)
        else:
            lineNo, rest = line.split('\t', 1)
            lineConent, *comment = re.split(' +# *', rest, 1)
            comment = comment[0] if comment else None
            lines.append([object, surface, section, lineNo, comment])
            content.append(lineConent)

    lines = pd.DataFrame(lines,
                         columns=['object', 
                                  'surface', 
                                  'section', 
                                  'lineNo',
                                  'comment'])

    signs, compounds, words, errors = parse('\n'.join(content), language, stem)
    return lines, signs, compounds, words, errors