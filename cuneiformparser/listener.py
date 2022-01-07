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
        self.damaged = False
        self.newline = False
        self.inverted = False

        self.value = ''
        self.crits = ''

        self.complex = 0

        self.capitalized = False

        self.pn_type = None
        self.language = self.default_language
        self.comments = []
        self.compoundComments = []
        self.section = None

        self.stem = self.default_stem

    def commit(self):
        self.signs.append([self.line_no, 
                           len(self.words),
                           self.value, 
                           'lost' if self.value == '…' else 'damaged' if self.damaged else self.condition, 
                           self.sign_type, 
                           self.phonographic, 
                           self.indicator, 
                           self.alignment,
                           self.stem, 
                           self.crits,
                           '; '.join(self.comments), 
                           self.newline, 
                           self.inverted])
        self.value = ''
        self.crits = ''
        self.newline = False
        self.inverted = False
        self.comments = []
        self.col = -1
        self.damaged = False

    def commitWord(self):
        self.words.append([len(self.compounds), False])
        self.capitalized = False

    def commitCompound(self):
        self.compounds.append([self.pn_type, self.language, self.section, '; '.join(self.compoundComments)])
        self.compoundComments = []
        self.pn_type = None

    def exitShift(self, ctx:CuneiformParser.ShiftContext):
        var = ctx.getText()[1:]
        val = ''
        if '=' in var:
            var, val = var.split('=')
        if var in ['a', 'akk']:
            self.language = 'akkadian'
        elif var in ['s', 'sux', 'eg']:
            self.language = 'sumerian'
        elif var in ['h', 'hit']:
            self.language = 'hittite'
        elif var in ['person', 'place', 'god', 'water', 'field', 'temple', 'month', 'object']:
            self.pn_type = var
            self.capitalized = True
        elif var == 'sec':
            self.section = val

    def exitCompound(self, ctx:CuneiformParser.CompoundContext):
        self.commitCompound()

    def exitHdivCompound(self, ctx:CuneiformParser.HdivCompoundContext):
        self.commitWord()
        self.commitCompound()

    def exitVdivCompound(self, ctx:CuneiformParser.VdivCompoundContext):
        self.commitWord()
        self.commitCompound()

    def exitWord(self, ctx:CuneiformParser.WordContext):
        self.commitWord()

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

    def enterValueAtom(self, ctx:CuneiformParser.ValueAtomContext):
        self.sign_type = 'value'

    def enterCvalueAtom(self, ctx:CuneiformParser.CvalueAtomContext):
        self.sign_type = 'value'

    def enterDetValueAtom(self, ctx:CuneiformParser.DetValueAtomContext):
        self.sign_type = 'value'

    def enterSignAtom(self, ctx:CuneiformParser.SignAtomContext):
        self.sign_type = 'sign'

    def enterMaybeSignAtom(self, ctx:CuneiformParser.MaybeSignAtomContext):
        self.sign_type = 'sign'

    def enterXAtom(self, ctx:CuneiformParser.XAtomContext):
        self.sign_type = 'sign'

    def enterNumberAtom(self, ctx:CuneiformParser.NumberAtomContext):
        self.sign_type = 'number'

    def enterMaybeNumberAtom(self, ctx:CuneiformParser.MaybeNumberAtomContext):
        self.sign_type = 'number'

    def enterHdividerAtom(self, ctx:CuneiformParser.HdividerAtomContext):
        self.sign_type = 'punctuation'

    def enterVdividerAtom(self, ctx:CuneiformParser.VdividerAtomContext):
        self.sign_type = 'punctuation'

    def enterEmptyLineAtom(self, ctx:CuneiformParser.EmptyLineAtomContext):
        self.sign_type = 'punctuation'


    def exitValueAtom(self, ctx:CuneiformParser.ValueAtomContext):
        self.commit()

    def exitCvalueAtom(self, ctx:CuneiformParser.CvalueAtomContext):
        self.commit()

    def exitDetValueAtom(self, ctx:CuneiformParser.DetValueAtomContext):
        self.commit()

    def exitSignAtom(self, ctx:CuneiformParser.SignAtomContext):
        self.commit()

    def exitMaybeSignAtom(self, ctx:CuneiformParser.MaybeSignAtomContext):
        self.commit()
    
    def exitXAtom(self, ctx:CuneiformParser.XAtomContext):
        self.commit()

    def exitNumberAtom(self, ctx:CuneiformParser.NumberAtomContext):
        self.commit()

    def exitMaybeNumberAtom(self, ctx:CuneiformParser.MaybeNumberAtomContext):
        self.commit()

    def exitHdividerAtom(self, ctx:CuneiformParser.HdividerAtomContext):
        self.commit()

    def exitVdividerAtom(self, ctx:CuneiformParser.VdividerAtomContext):
        self.commit()

    def exitEmptyLineAtom(self, ctx:CuneiformParser.EmptyLineAtomContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += '='
        self.commit()


    # Complexes

    def enterSignComplex(self, ctx:CuneiformParser.SignComplexContext):
        self.complex += 1

    def enterNumberComplex(self, ctx:CuneiformParser.NumberComplexContext):
        self.complex += 1

    def exitSignComplex(self, ctx:CuneiformParser.SignComplexContext):
        self.complex -= 1

    def exitNumberComplex(self, ctx:CuneiformParser.NumberComplexContext):
        self.complex -= 1


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
        self.value += self.processInternalConditions(ctx.getText().lower(), self.line_no, self.col)

    def exitCvalueT(self, ctx:CuneiformParser.CvalueTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += self.processInternalConditions(ctx.getText().lower(), self.line_no, self.col)

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
        self.value += self.processInternalConditions(ctx.getText(), self.line_no, self.col)

    def exitNnsignT(self, ctx:CuneiformParser.NnsignTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += self.processInternalConditions(ctx.getText(), self.line_no, self.col)

    def exitNumberT(self, ctx:CuneiformParser.NumberTContext):
        if self.col < 0:
            self.col = ctx.start.column
        if ctx.N():
            self.value += 'N'
        else:
            self.value += self.processInternalConditions(ctx.getText(), self.line_no, self.col)

    def exitXT(self, ctx:CuneiformParser.XTContext):
        if self.col < 0:
            self.col = ctx.start.column
        if self.sign_type == 'number':
            self.value += 'N'
        else:
            self.value += 'X'

    def exitEllipsisT(self, ctx:CuneiformParser.EllipsisTContext):
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
        else:
            self.crits += ctx.getText()

    def exitComment(self, ctx:CuneiformParser.CommentContext):
        self.comments.append(ctx.getText()[1:-1].replace('\\', r'\\'))

    def exitCompoundComment(self, ctx:CuneiformParser.CompoundCommentContext):
        self.compoundComments.append(ctx.getText()[1:-1].replace('\\', r'\\'))


    # Newline

    def nl(self, ctx):
        self.line_no += 1
        if self.condition != 'intact':
            self.errorListener.syntaxError(None, None, ctx.start.line, ctx.start.column, 'Unclosed condition bracket', None)
            self.condition = 'intact'
        self.language = self.default_language

    def exitNl(self, ctx:CuneiformParser.NlContext):
        self.nl(ctx)
    def exitDashNl(self, ctx:CuneiformParser.DashNlContext):
        self.nl(ctx)
    def exitDoubleDashNl(self, ctx:CuneiformParser.DoubleDashNlContext):
        self.nl(ctx)
    def exitDotNl(self, ctx:CuneiformParser.DotNlContext):
        self.nl(ctx)
    def exitCommaNl(self, ctx:CuneiformParser.CommaNlContext):
        self.nl(ctx)
    def exitSemicolonNl(self, ctx:CuneiformParser.SemicolonNlContext):
        self.nl(ctx)
    def exitTildeNl(self, ctx:CuneiformParser.TildeNlContext):
        self.nl(ctx)
    def exitSTildeNl(self, ctx:CuneiformParser.STildeNlContext):
        self.nl(ctx)

    def exitSlash(self, ctx:CuneiformParser.SlashContext):
        if self.complex:
            self.value += '/'
        else:
            self.newline = True

    # Conditions

    conditionMap = {
        '\n': 'intact',  
        '[': 'lost', 
        ']': 'lost', 
        '⸢': 'damaged', 
        '⸣': 'damaged', 
        '‹': 'inserted', 
        '›': 'inserted', 
        '«': 'deleted', 
        '»': 'deleted'}

    def processCondition(self, c, line, col):
        if c in '[⸢‹«':
            if self.condition != 'intact':
                self.errorListener.syntaxError(None, None, line, col, 'Nested condition brackets', None)
            self.condition = self.conditionMap[c]
        else:
            if self.condition != self.conditionMap[c]:
                self.errorListener.syntaxError(None, None, line, col, 'Unbalanced condition brackets', None)
            self.condition = 'intact'

    def processInternalConditions(self, value, line, col):
        if re.search(r'[\[\]]', value):
            for i, c in enumerate(value):
                if c in '[]':
                    self.processCondition(c, line, col+i)
            value = re.sub(r'[\[\]]', '', value)
            self.damaged = True
        return value

    def processHashCondition(self, line, col):
        if self.condition != 'intact':
            self.errorListener.syntaxError(None, None, line, col, 'Invalid damage hash', None)
        else:
            self.damaged = True

    def exitOpenCondition(self, ctx:CuneiformParser.OpenConditionContext):
        self.processCondition(ctx.getText(), ctx.start.line, ctx.start.column)

    def exitCloseCondition(self, ctx:CuneiformParser.CloseConditionContext):
        self.processCondition(ctx.getText(), ctx.start.line, ctx.start.column)