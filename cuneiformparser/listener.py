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

    def __init__(self, errorListener, defaultLanguage, stem):
        self.errorListener = errorListener

        self.default_language = defaultLanguage
        self.default_stem = True if stem else None

        self.signs = []
        self.words = []
        self.compounds = []

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

        self.complex = 0

        self.capitalized = False

        self.pn_type = None
        self.language = self.default_language
        self.compoundComments = []

        self.stem = self.default_stem

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
                           self.stem, 
                           self.crits,
                          [], 
                           self.newline, 
                           self.inverted])
        self.value = ''
        self.crits = ''
        self.newline = False
        self.inverted = False
        self.col = -1


    def exitMeta(self, ctx:CuneiformParser.MetaContext):
        if ctx.getText() == '_akk_':
            self.language = 'akkadian'
        elif ctx.getText() == '_sum_':
            self.language = 'sumerian'
        elif ctx.getText() == '_hit_':
            self.language = 'hittite'
        elif ctx.getText() in ['_person_', '_place_', '_god_', '_water_', '_field_', '_temple_', '_month_', '_object_']:
            self.pn_type = ctx.getText()[1:-1]
            self.capitalized = True

    def exitCompound(self, ctx:CuneiformParser.CompoundContext):
        self.compounds.append([self.pn_type, self.language, '; '.join(self.compoundComments)])
        self.compoundComments = []
        self.pn_type = None
        self.language = self.default_language

    def exitWord(self, ctx:CuneiformParser.WordContext):
        self.words.append([len(self.compounds), self.capitalized])
        self.capitalized = False

    def enterCsegment(self, ctx:CuneiformParser.CsegmentContext):
        self.capitalized = True


    # Segments

    def enterStem(self, ctx:CuneiformParser.StemContext):
        self.stem = True

    def enterCstem(self, ctx:CuneiformParser.CstemContext):
        self.stem = True

    def exitStem(self, ctx:CuneiformParser.StemContext):
        self.stem = self.default_stem

    def exitCstem(self, ctx:CuneiformParser.CstemContext):
        self.stem = self.default_stem

    def enterPrefix(self, ctx:CuneiformParser.PrefixContext):
        self.stem = False

    def enterCprefix(self, ctx:CuneiformParser.CprefixContext):
        self.stem = False

    def enterSuffix(self, ctx:CuneiformParser.SuffixContext):
        self.stem = False

    def exitSuffix(self, ctx:CuneiformParser.SuffixContext):
        self.stem = self.default_stem
    

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

    def enterDetValue(self, ctx:CuneiformParser.DetValueContext):
        self.sign_type = 'value'

    def enterSign(self, ctx:CuneiformParser.SignContext):
        self.sign_type = 'sign'

    def enterMaybeSign(self, ctx:CuneiformParser.MaybeSignContext):
        self.sign_type = 'sign'

    def enterXSign(self, ctx:CuneiformParser.XContext):
        self.sign_type = 'sign'

    def enterNumber(self, ctx:CuneiformParser.NumberContext):
        self.sign_type = 'number'

    def enterMaybeNumber(self, ctx:CuneiformParser.MaybeNumberContext):
        self.sign_type = 'number'

    def enterHdivider(self, ctx:CuneiformParser.HdividerContext):
        self.sign_type = 'punctuation'

    def enterVdivider(self, ctx:CuneiformParser.VdividerContext):
        self.sign_type = 'punctuation'


    def exitValue(self, ctx:CuneiformParser.ValueContext):
        self.commit()

    def exitCvalue(self, ctx:CuneiformParser.CvalueContext):
        self.commit()

    def exitDetValue(self, ctx:CuneiformParser.DetValueContext):
        self.commit()

    def exitSimpleSign(self, ctx:CuneiformParser.SimpleSignContext):
        if not self.complex:
            self.commit()

    def exitNumberSign(self, ctx:CuneiformParser.NumberSignContext):
        if not self.complex:
            self.commit()
    
    def exitX(self, ctx:CuneiformParser.XContext):
        if not self.complex:
            self.commit()

    def exitDots(self, ctx:CuneiformParser.DotsContext):
        if not self.complex:
            self.sign_type = 'damage'
            self.commit()

    def exitSimpleNumber(self, ctx:CuneiformParser.SimpleNumberContext):
        if not self.complex:
            self.commit()

    def exitHdivider(self, ctx:CuneiformParser.HdividerContext):
        self.commit()
        self.words.append([len(self.compounds), False])
        self.capitalized = False
        self.compounds.append([None, self.language, '; '.join(self.compoundComments)])
        self.compoundComments = []
        self.pn_type = None
        self.language = self.default_language

    def exitVdivider(self, ctx:CuneiformParser.VdividerContext):
        self.commit()
        self.words.append([len(self.compounds), False])
        self.capitalized = False
        self.compounds.append([None, self.language, '; '.join(self.compoundComments)])
        self.compoundComments = []
        self.pn_type = None
        self.language = self.default_language


    # Complexes

    def enterSignComplex(self, ctx:CuneiformParser.SignComplexContext):
        self.complex += 1

    def enterSignSum(self, ctx:CuneiformParser.SignSumContext):
        self.complex += 1

    def enterNumberComplex(self, ctx:CuneiformParser.NumberComplexContext):
        self.complex += 1

    def exitSignComplex(self, ctx:CuneiformParser.SignComplexContext):
        self.complex -= 1
        if not self.complex:
            self.commit()

    def exitSignSum(self, ctx:CuneiformParser.SignSumContext):
        self.complex -= 1
        if not self.complex:
            self.commit()

    def exitNumberComplex(self, ctx:CuneiformParser.NumberComplexContext):
        self.complex -= 1
        if not self.complex:
            self.commit()


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
        self.value += ctx.getText().lower()

    def exitCvalueT(self, ctx:CuneiformParser.CvalueTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += ctx.getText().lower()

    def exitDT(self, ctx:CuneiformParser.DTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += 'd'

    def exitDualT(self, ctx:CuneiformParser.DualTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += 'II'

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
        if self.sign_type == 'number':
            self.value += 'N'
        else:
            self.value += 'X'

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
            self.sign_type = 'description'

    def exitHdividerT(self, ctx:CuneiformParser.HdividerTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += ctx.getText()

    def exitVdividerT(self, ctx:CuneiformParser.VdividerTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += ctx.getText() if ctx.getText() else '='


    def exitMod(self, ctx:CuneiformParser.ModContext):
        if self.sign_type == 'value':
            self.crits += ctx.getText()
        else:
            self.value += ctx.getText()

    def exitVariant(self, ctx:CuneiformParser.VariantContext):
        if self.sign_type == 'value':
            self.crits += ctx.getText()
        else:
            self.value += ctx.getText()

    def exitCrit(self, ctx:CuneiformParser.CritContext):
        if ctx.getText() == '#':
            self.processHashCondition(ctx.start.line, ctx.start.column)
        elif self.signs:
            self.signs[-1][9] += ctx.getText()

    def exitComment(self, ctx:CuneiformParser.CommentContext):
        if self.signs:
            self.signs[-1][10].append(ctx.getText()[1:-1].replace('\\', r'\\'))

    def exitCompoundComment(self, ctx:CuneiformParser.CompoundCommentContext):
        self.compoundComments.append(ctx.getText()[1:-1].replace('\\', r'\\'))


    # Newline

    def exitNlT(self, ctx:CuneiformParser.NlTContext):
        self.line_no += 1
        if self.condition != 'intact':
            self.errorListener.syntaxError(None, None, ctx.start.line, ctx.start.column, 'Unclosed condition bracket', None)
            self.condition = 'intact'

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
        if re.search(r'[\[\]]', self.value):
            for i, c in enumerate(self.value):
                if c in '[]':
                    self.processCondition(c, line, col+i)
            self.value = re.sub(r'[\[\]]', '', self.value)
            return 'damaged'
        return self.condition

    def processHashCondition(self, line, col):
        if self.signs:
            if self.signs[-1][3] != 'intact':
                self.errorListener.syntaxError(None, None, line, col, 'Invalid damage hash', None)
            else:
                self.signs[-1][3] = 'damaged'

    def exitOpenCondition(self, ctx:CuneiformParser.OpenConditionContext):
        self.processCondition(ctx.getText(), ctx.start.line, ctx.start.column)

    def exitCloseCondition(self, ctx:CuneiformParser.CloseConditionContext):
        self.processCondition(ctx.getText(), ctx.start.line, ctx.start.column)