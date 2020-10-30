import pandas as pd
import re

try:
    from .grammar import CuneiformListener
    from .grammar import CuneiformLexer
    from .grammar import CuneiformParser
except:
    from grammar import CuneiformListener
    from grammar import CuneiformLexer
    from grammar import CuneiformParser

class Listener(CuneiformListener):

    def __init__(self, errorListener):
        self.errorListener = errorListener

        self.signs = []
        self.words = []
        self.compounds = []
        #self.signs = pd.DataFrame({'line_no': pd.Series([], dtype='int32'),
        #                           'word_no': pd.Series([], dtype='int32'),  
        #                           'value': pd.Series([], dtype='string'), 
        #                           'condition': pd.Series([], dtype='string'), 
        #                           'sign_type': pd.Series([], dtype='string'),
        #                           'phonographic': pd.Series([], dtype='boolean'), 
        #                           'indicator': pd.Series([], dtype='boolean'), 
        #                           'alignment': pd.Series([], dtype='string'), 
        #                           'crits': pd.Series([], dtype='string'), 
        #                           'comment': pd.Series([], dtype='object'), 
        #                           'newline': pd.Series([], dtype='boolean'), 
        #                           'inverted': pd.Series([], dtype='boolean')})
        #self.words = pd.DataFrame({'compound_no': pd.Series([], dtype='int32'),
        #                           'PN': pd.Series([], dtype='boolean'), 
        #                           'language': pd.Series([], dtype='string')})
        #self.compounds = pd.DataFrame({'PN': pd.Series([], dtype='boolean'), 
        #                               'comment': pd.Series([], dtype='object')})
        self.line_no = 0
        self.col = 0
        self.sign_type = None
        self.phonographic = None
        self.indicator = False
        self.alignment = None
        self.condition = 'intact'
        self.newline = False
        self.inverted = False

        self.value = ''
        self.crits = ''
        self.comments = []

        self.complex = False

        self.pn_type = None
        self.default_language = 'sumerian'
        self.language = self.default_language

        self.condition_suffix = None

    def commit(self):
        condition = self.processInternalConditions(self.line_no, self.col)
        self.signs.append([self.line_no, 
                           len(self.words), 
                           self.value, 
                           condition, 
                           self.sign_type, 
                           self.phonographic, 
                           self.indicator, 
                           self.alignment, 
                           self.crits, 
                           self.comments, 
                           self.newline, 
                           self.inverted])
        #self.signs = self.signs.append(pd.DataFrame({'line_no': pd.Series([self.line_no], dtype='int32'),
        #                                             'word_no': pd.Series([len(self.words.index)], dtype='int32'),  
        #                                             'value': pd.Series([self.value], dtype='string'), 
        #                                             'condition': pd.Series([condition], dtype='string'), 
        #                                             'sign_type': pd.Series([self.sign_type], dtype='string'),
        #                                             'phonographic': pd.Series([self.phonographic], dtype='boolean'), 
        #                                             'indicator': pd.Series([self.indicator], dtype='boolean'), 
        #                                             'alignment': pd.Series([self.alignment], dtype='string'), 
        #                                             'crits': pd.Series([self.crits], dtype='string'), 
        #                                             'comment': pd.Series([self.comments], dtype='object'), 
        #                                             'newline': pd.Series([self.newline], dtype='boolean'), 
        #                                             'inverted': pd.Series([self.inverted], dtype='boolean')}))
        self.value = ''
        self.crits = ''
        self.comments = []
        self.newline = False
        self.inverted = False
        self.phonographic = None
        self.indicator = False
        self.alignment = None
        self.col = -1


    def exitMeta(self, ctx:CuneiformParser.MetaContext):
        if ctx.META == '_akk_':
            self.language = 'akkadian'

    def exitCompound(self, ctx:CuneiformParser.CompoundContext):
        self.compounds.append([False if ctx.word() else True, self.comments])
        #self.compounds = self.compounds.append(pd.DataFrame({'PN': pd.Series([False if ctx.word() else True], dtype='boolean'), 
        #                                                     'comment': pd.Series([self.comments], dtype='object')}))
        self.comments = []
        self.language = self.default_language

    def exitWord(self, ctx:CuneiformParser.WordContext):
        #self.words = self.words.append(pd.DataFrame({'compound_no': pd.Series([len(self.compounds.index)], dtype='int32'),
        #                                             'PN': pd.Series([False], dtype='boolean'), 
        #                                             'language': pd.Series(['sumerian'], dtype='string')}))
        self.words.append([len(self.compounds), False, self.language])

    
    # Determinatives 

    def enterDetp(self, ctx:CuneiformParser.DetpContext):
        self.phonographic = False
        self.indicator = True
        self.alignment = 'right'

    def exitDetp(self, ctx:CuneiformParser.DetpContext):
        self.phonographic = None
        self.indicator = False
        self.alignment = None

    def enterDets(self, ctx:CuneiformParser.DetsContext):
        self.phonographic = False
        self.indicator = True
        self.alignment = 'left'

    def exitDets(self, ctx:CuneiformParser.DetsContext):
        self.phonographic = None
        self.indicator = False
        self.alignment = None

    def enterDetc(self, ctx:CuneiformParser.DetsContext):
        self.phonographic = False
        self.indicator = True
        self.alignment = 'center'

    def exitDetc(self, ctx:CuneiformParser.DetsContext):
        self.phonographic = None
        self.indicator = False
        self.alignment = None


    # Phonetic Complements

    def enterPcp(self, ctx:CuneiformParser.PcpContext):
        self.phonographic =True
        self.indicator = True
        self.alignment = 'right'

    def exitPcp(self, ctx:CuneiformParser.PcpContext):
        self.phonographic = None
        self.indicator = False
        self.alignment = None

    def enterPcs(self, ctx:CuneiformParser.PcsContext):
        self.phonographic = True
        self.indicator = True
        self.alignment = 'left'

    def exitPcs(self, ctx:CuneiformParser.PcsContext):
        self.phonographic = None
        self.indicator = False
        self.alignment = None

    def enterPcc(self, ctx:CuneiformParser.PcsContext):
        self.phonographic = True
        self.indicator = True
        self.alignment = 'center'

    def exitPcc(self, ctx:CuneiformParser.PcsContext):
        self.phonographic = None
        self.indicator = False
        self.alignment = None

    
    # Commits

    def enterValue(self, ctx:CuneiformParser.ValueContext):
        self.sign_type = 'value'

    def enterCvalue(self, ctx:CuneiformParser.CvalueContext):
        self.sign_type = 'value'

    def enterD(self, ctx:CuneiformParser.DContext):
        self.sign_type = 'value'

    def enterSign(self, ctx:CuneiformParser.SignContext):
        self.sign_type = 'sign'

    def enterNumber(self, ctx:CuneiformParser.NumberContext):
        self.sign_type = 'number'

    def enterNumberXC(self, ctx:CuneiformParser.NumberContext):
        self.sign_type = 'number'


    def exitValue(self, ctx:CuneiformParser.ValueContext):
        self.commit()

    def exitCvalue(self, ctx:CuneiformParser.CvalueContext):
        self.commit()

    def exitD(self, ctx:CuneiformParser.DContext):
        self.commit()

    def exitSign(self, ctx:CuneiformParser.SignContext):
        self.commit()

    def exitNumber(self, ctx:CuneiformParser.NumberContext):
        self.commit()

    def exitNumberXC(self, ctx:CuneiformParser.NumberContext):
        self.commit()

    # Complexes

    def enterSignComplex(self, ctx:CuneiformParser.SignComplexContext):
        self.complex = True

    def enterSignSum(self, ctx:CuneiformParser.SignSumContext):
        self.complex = True

    def enterNumberComplex(self, ctx:CuneiformParser.NumberComplexContext):
        self.complex = True


    # Operators

    def exitDotOp(self, ctx:CuneiformParser.DotOpContext):
        self.value += '.'

    def exitPlus(self, ctx:CuneiformParser.PlusContext):
        self.value += '+'

    def exitTimes(self, ctx:CuneiformParser.TimesContext):
        self.value += '×'

    def exitAbove(self, ctx:CuneiformParser.AboveContext):
        self.value += '&'


    # Terminals

    def exitValueT(self, ctx:CuneiformParser.ValueTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += ctx.getText()

    def exitCvalueT(self, ctx:CuneiformParser.CvalueTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += ctx.getText().lower()

    def exitDT(self, ctx:CuneiformParser.DTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += 'd'

    def exitSignT(self, ctx:CuneiformParser.SignTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += ctx.getText()

    def exitNnsignT(self, ctx:CuneiformParser.NnsignTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += ctx.getText()

    def exitNumberT(self, ctx:CuneiformParser.NumberTContext):
        if self.col < 0:
            self.col = ctx.start.column
        if ctx.N():
            self.value += 'N'
        else:
            self.value += ctx.getText()

    def exitXT(self, ctx:CuneiformParser.XTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += 'X'
    
    def exitNumberXT(self, ctx:CuneiformParser.NumberXTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += 'N'

    def exitDotsT(self, ctx:CuneiformParser.DotsTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += '…'

    def exitDescT(self, ctx:CuneiformParser.DescTContext):
        if self.col < 0:
            self.col = ctx.start.column
        if self.complex:
            self.value += ctx.DESC().getText().replace('\\', r'\\')
        else:
            self.value += ctx.DESC().getText()[1:-1].replace('\\', r'\\')
            self.sign_type = 'desc'


    def exitMod(self, ctx:CuneiformParser.ModContext):
        if self.sign_type == 'value':
            self.crits += ctx.getText()
        else:
            self.value += ctx.getText()

    def exitCrit(self, ctx:CuneiformParser.CritContext):
        self.crits += ctx.getText()

    def exitComment(self, ctx:CuneiformParser.CommentContext):
        self.comments.append(ctx.getText()[1:-1].replace('\\', r'\\'))


    # Newline

    def exitNl(self, ctx:CuneiformParser.NlContext):
        self.line_no += 1

    def exitSlash(self, ctx:CuneiformParser.SlashContext):
        if self.complex:
            self.value += '/'
        else:
            self.newline = True


    # Conditions

    conditionMap = {'\n': 'intact',  '[': 'lost', ']': 'lost', '⸢': 'damaged', '⸣': 'damaged', '‹': 'inserted', '›': 'inserted', '«': 'deleted', '»': 'deleted'}

    def processCondition(self, c, line, col):
        if c in '[⸢‹«':
            if self.condition != 'intact':
                self.errorListener.syntaxError(None, None, line, col, 'Nested condition brackets', None)
            self.condition = self.conditionMap[c]
        else:
            if self.condition != self.conditionMap[c]:
                self.errorListener.syntaxError(None, None, line, col, 'Unbalanced condition brackets', None)
            self.condition = 'intact'

    def processInternalConditions(self, line, col):
        condition = self.condition
        suffix_col = col+len(self.value)
        if re.search(r'[\[\]]', self.value):
            for i, c in enumerate(self.value):
                if c in '[]':
                    self.processCondition(c, line, col+i)
            self.value = re.sub(r'[\[\]]', '', self.value)
            condition = 'damaged'
        if self.condition_suffix:
            self.processCondition(self.condition_suffix, line, suffix_col)
            self.condition_suffix = None
        return condition

    def exitOpenCondition(self, ctx:CuneiformParser.OpenConditionContext):
        self.processCondition(ctx.getText(), ctx.start.line, ctx.start.column)

    def exitCloseCondition(self, ctx:CuneiformParser.CloseConditionContext):
        self.processCondition(ctx.getText(), ctx.start.line, ctx.start.column)

    def exitConditionSuffix(self, ctx:CuneiformParser.ConditionSuffixContext):
        self.condition_suffix = ctx.getText()