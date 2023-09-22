import re

try:
    from grammar.CuneiformParser import CuneiformParser
    from grammar.CuneiformListener import CuneiformListener
except:
    from .grammar.CuneiformParser import CuneiformParser
    from .grammar.CuneiformListener import CuneiformListener


numberSigns = re.compile(r'(ŠAR2|IKU|AŠ|DIŠ|BUR3|GEŠ2|U|BARIG|EŠE3|BAN2|ŠAR’U|ŠARGAL|GEŠ’U|BUR’U|GEŠMIN’U|ŠAR’UGAL|ŠARKID|AŠ×DIŠ|AŠ×DIŠ@t|DIŠ@t|GEŠ2@t|BAD×DIŠ|BAD×DIŠ@t|IKU@t)(@[cf])?(@v)?|GEŠ2@c@d|GEŠ2@c@90|GEŠ’U@c@d|DIŠ×U@t|AŠ@c×AŠ|DIŠ@c×DIŠ')


class Listener(CuneiformListener):

    def __init__(self, errorListener, defaultLanguage, stem):
        self.errorListener = errorListener

        self.default_language = defaultLanguage
        self.default_stem = True if stem else None

        self.signs = []
        self.words = []
        self.compounds = []
        self.sections = []

        self.line_no = 0
        self.col = 0
        self.sign_type = None
        self.phonographic = None
        self.logogramm = False
        self.indicator = False
        self.alignment = None
        self.condition = 'intact'
        self.damaged = False
        self.newline = False
        self.inverted = False
        self.ligature = False

        self.value = ''
        self.signSpec = ''
        self.crits = ''

        self.spec = False

        self.capitalized = False

        self.pn_type = None
        self.language = self.default_language
        self.comments = []
        self.compoundComments = []
        self.section = False

        self.stem = self.default_stem

    def commit(self, start, stop):
        self.signs.append([self.line_no, 
                           len(self.words),
                           self.value if self.value else None,
                           self.signSpec if self.signSpec else None, 
                           'damage' if self.sign_type == 'sign' and self.value in '…X' else self.sign_type, 
                           self.alignment if self.indicator else 'none',
                           False if self.logogramm else self.phonographic, 
                           'lost' if self.value == '…' else 'damaged' if self.damaged else self.condition,
                           self.stem, 
                           self.crits.replace('!', '') if self.signSpec and self.sign_type in ['sign', 'value'] and not self.value.endswith('x') else self.crits,
                           '; '.join(self.comments) if self.comments else None, 
                           self.newline, 
                           self.inverted,
                           self.ligature,
                           start,
                           stop])
        self.sign_type = None
        self.value = ''
        self.signSpec = ''
        self.crits = ''
        self.newline = False
        self.inverted = False
        self.ligature = False
        self.comments = []
        self.col = -1
        self.damaged = False

    def commitWord(self):
        self.words.append([len(self.compounds), self.capitalized])
        self.capitalized = False

    def commitCompound(self):
        self.compounds.append([self.pn_type, self.language, len(self.sections)-1 if self.section else -1, '; '.join(self.compoundComments) if self.compoundComments else None])
        self.compoundComments = []
        self.pn_type = None

    def exitShift(self, ctx:CuneiformParser.ShiftContext):
        var = ctx.getText()[1:]
        val = None
        if '=' in var:
            var, val = var.split('=')
        if var in ['a', 'akk']:
            self.language = 'akkadian'
        elif var in ['s', 'sux', 'eg']:
            self.language = 'sumerian'
        elif var in ['h', 'hit']:
            self.language = 'hittite'
        elif var in ['person', 'place', 'god', 'water', 'field', 'temple', 'month', 'object', 'ethnicity']:
            self.pn_type = var
            self.capitalized = True
        elif var == 'sec':
            if val:
                self.sections.append(val)
                self.section = True
            else:
                self.section = False

    def exitLog(self, ctx:CuneiformParser.LogContext):
        self.logogramm = not self.logogramm

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

    def enterBreakAtom(self, ctx:CuneiformParser.BreakAtomContext):
        self.sign_type = 'sign'

    def enterNumberAtom(self, ctx:CuneiformParser.NumberAtomContext):
        self.sign_type = 'number'

    def enterMaybeNumberAtom(self, ctx:CuneiformParser.MaybeNumberAtomContext):
        self.sign_type = 'number'

    def enterHdividerAtom(self, ctx:CuneiformParser.HdividerAtomContext):
        self.sign_type = 'punctuation'

    def enterVdividerAtom(self, ctx:CuneiformParser.VdividerAtomContext):
        self.sign_type = 'punctuation'


    def exitValueAtom(self, ctx:CuneiformParser.ValueAtomContext):
        self.commit(ctx.start.column, ctx.start.column+len(ctx.getText()))

    def exitCvalueAtom(self, ctx:CuneiformParser.CvalueAtomContext):
        self.commit(ctx.start.column, ctx.start.column+len(ctx.getText()))

    def exitDetValueAtom(self, ctx:CuneiformParser.DetValueAtomContext):
        self.commit(ctx.start.column, ctx.start.column+len(ctx.getText()))

    def exitSignAtom(self, ctx:CuneiformParser.SignAtomContext):
        self.commit(ctx.start.column, ctx.start.column+len(ctx.getText()))

    def exitMaybeSignAtom(self, ctx:CuneiformParser.MaybeSignAtomContext):
        self.commit(ctx.start.column, ctx.start.column+len(ctx.getText()))
    
    def exitBreakAtom(self, ctx:CuneiformParser.BreakAtomContext):
        self.commit(ctx.start.column, ctx.stop.column)

    def exitNumberAtom(self, ctx:CuneiformParser.NumberAtomContext):
        self.processInternalConditions(self.value, ctx.start.line, self.col)
        self.commit(ctx.start.column, ctx.stop.column)

    def exitMaybeNumberAtom(self, ctx:CuneiformParser.MaybeNumberAtomContext):
        self.commit(ctx.start.column, ctx.stop.column)

    def exitHdividerAtom(self, ctx:CuneiformParser.HdividerAtomContext):
        self.commit(ctx.start.column, ctx.stop.column)

    def exitVdividerAtom(self, ctx:CuneiformParser.VdividerAtomContext):
        self.commit(ctx.start.column, ctx.stop.column)


    # Sign Spec

    def enterSignSpec(self, ctx:CuneiformParser.SignSpecContext):
        self.spec = True

    def exitSignSpec(self, ctx:CuneiformParser.SignSpecContext):
        self.spec = False
        if self.signSpec and self.sign_type == 'number':
            if not numberSigns.fullmatch(self.signSpec):
                self.errorListener.syntaxError(None, None, ctx.start.line, ctx.start.column, f'Invalid number specification: {self.signSpec}', None)
            self.value += '('+self.signSpec+')'
            self.signSpec = ''
            

    # Operators

    def exitDotOp(self, ctx:CuneiformParser.DotOpContext):
        if self.spec:
            self.signSpec += '.'
        else:
            self.value += '.'

    def exitPlusOp(self, ctx:CuneiformParser.PlusOpContext):
        if self.spec:
            self.signSpec += '+'
        else:
            self.value += '+'

    def exitTimesOp(self, ctx:CuneiformParser.TimesOpContext):
        if self.spec:
            self.signSpec += '×'
        else:
            self.value += '×'

    def exitDivOp(self, ctx:CuneiformParser.DivOpContext):
        if self.spec:
            self.signSpec += '/'
        else:
            self.value += '/'
            
    def exitSignOp(self, ctx:CuneiformParser.SignOpContext):
        if self.spec:
            self.signSpec += ctx.getText()
        else:
            self.value += ctx.getText()

    def exitLparenOp(self, ctx:CuneiformParser.LparenOpContext):
        if self.spec:
            self.signSpec += '('
        else:
            self.value += '('

    def exitRparenOp(self, ctx:CuneiformParser.RparenOpContext):
        if self.spec:
            self.signSpec += ')'
        else:
            self.value += ')'

    def exitUnaryMinusOp(self, ctx:CuneiformParser.UnaryMinusOpContext):
        self.value += '-'


    # Terminals

    def exitValueT(self, ctx:CuneiformParser.ValueTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += self.processInternalConditions(ctx.getText().lower(), ctx.start.line, self.col)

    def exitCvalueT(self, ctx:CuneiformParser.CvalueTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += self.processInternalConditions(ctx.getText().lower(), ctx.start.line, self.col)

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
        if self.spec:
            self.signSpec += ctx.getText()
        else:
            self.value += self.processInternalConditions(ctx.getText(), ctx.start.line, self.col)

    def exitNnsignT(self, ctx:CuneiformParser.NnsignTContext):
        if self.col < 0:
            self.col = ctx.start.column
        if self.spec:
            self.signSpec += ctx.getText()
        else:
            self.value += self.processInternalConditions(ctx.getText(), ctx.start.line, self.col)

    def exitNumberT(self, ctx:CuneiformParser.NumberTContext):
        if self.col < 0:
            self.col = ctx.start.column
        if ctx.N():
            self.value += 'N'
        else:
            self.value += ctx.getText()

    def exitNumberSpec(self, ctx:CuneiformParser.SignSpecContext):
        self.value += re.sub(r'[xX]', '×', ctx.getText())

    def exitXT(self, ctx:CuneiformParser.XTContext):
        if self.col < 0:
            self.col = ctx.start.column
        if self.sign_type == 'number':
            self.value += 'N'
        elif self.spec:
            self.signSpec += 'X'
        else:
            self.value += 'X'

    def exitEllipsisT(self, ctx:CuneiformParser.EllipsisTContext):
        if self.col < 0:
            self.col = ctx.start.column
        self.value += '…'

    def exitDescT(self, ctx:CuneiformParser.DescTContext):
        if self.col < 0:
            self.col = ctx.start.column
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
        if self.spec:
            self.signSpec += ctx.getText()
        elif self.sign_type == 'sign':
            self.value += ctx.getText()
        else:
            self.crits += ctx.getText()

    def exitVariant(self, ctx:CuneiformParser.VariantContext):
        if self.spec:
            self.signSpec += ctx.getText()
        elif self.sign_type == 'sign':
            self.value += ctx.getText()
        else:
            self.crits += ctx.getText()

    def exitCrit(self, ctx:CuneiformParser.CritContext):
        if ctx.getText() == '#':
            self.processHashCondition(ctx.start.line, ctx.start.column)
        elif self.sign_type == 'number':
            self.value += ctx.getText()
        else:
            self.crits += ctx.getText()

    def exitPlusCrit(self, ctx: CuneiformParser.PlusCritContext):
        self.value += '+'

    def exitComment(self, ctx:CuneiformParser.CommentContext):
        self.comments.append(ctx.getText()[1:-1].replace('\\', r'\\'))

    def exitCompoundComment(self, ctx:CuneiformParser.CompoundCommentContext):
        self.compoundComments.append(ctx.getText()[1:-1].replace('\\', r'\\'))


    # Separators

    def exitSlash(self, ctx:CuneiformParser.SlashContext):
        self.newline = True

    def exitColon(self, ctx:CuneiformParser.ColonContext):
        self.inverted = True

    def exitLigPlus(self, ctx:CuneiformParser.LigPlusContext):
        self.ligature = True


    # Newline

    def nl(self, ctx):
        self.line_no += 1
        if self.condition != 'intact':
            self.errorListener.syntaxError(None, None, ctx.start.line, ctx.start.column, 'Unclosed condition bracket', None)
            self.condition = 'intact'
        if self.logogramm:
            self.errorListener.syntaxError(None, None, ctx.start.line, ctx.start.column, 'Unpaired underscores', None)
            self.logogramm = False
        #self.language = self.default_language

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
    def exitTildeNl(self, ctx:CuneiformParser.TildeNlContext):
        self.nl(ctx)
    

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
        if re.search(r'[\[\]⸢⸣]', value):
            for i, c in enumerate(value):
                if c in '[]⸢⸣':
                    self.processCondition(c, line, col+i)
            value = re.sub(r'[\[\]⸢⸣]', '', value)
            self.damaged = True
        return value

    def processHashCondition(self, line, col):
        if self.condition != 'intact':
            self.errorListener.syntaxError(None, None, line, col, 'Invalid damage hash', None)
        else:
            self.damaged = True

    def exitOpenCondition(self, ctx:CuneiformParser.OpenConditionContext):
        if self.sign_type == 'number':
            self.value += ctx.getText()
        else:
            self.processCondition(ctx.getText(), ctx.start.line, ctx.start.column)

    def exitCloseCondition(self, ctx:CuneiformParser.CloseConditionContext):
        if self.sign_type == 'number':
            self.value += ctx.getText()
        else:
            self.processCondition(ctx.getText(), ctx.start.line, ctx.start.column)