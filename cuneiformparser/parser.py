import sys
import antlr4
from antlr4.error import DiagnosticErrorListener
import pandas as pd

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


def parse(text, language, stem):
    input = antlr4.InputStream(text)
    lexer = CuneiformLexer(input)
    stream = antlr4.CommonTokenStream(lexer)
    parser = CuneiformParser(stream)

    errorListener = ErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(errorListener)
    parser.removeErrorListeners()        
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