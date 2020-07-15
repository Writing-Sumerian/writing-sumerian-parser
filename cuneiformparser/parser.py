#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import regex as re

LCONS = 'bdgĝhḫjklmnpqrřsšṣtṭwyz’'
LVOWELS = 'aeiu'
UCONS = 'BDGĜHḪJKLMNPQRŘSŠṢTṬWYZ'
UVOWELS = 'AEIU'
LCHARS = LCONS+LVOWELS
UCHARS = UCONS+UVOWELS
USYLL = '(?:[{ucons}’]?[{uvowels}][{ucons}’]?)'.format(ucons=UCONS, uvowels=UVOWELS)
LSYLL = '(?:[{lcons}]?[{lvowels}][{lcons}]?)'.format(lcons=LCONS, lvowels=LVOWELS)
CSYLL = '(?:[{ucons}][{lvowels}][{lcons}]?|’?[{uvowels}][{lcons}]?)'.format(ucons=UCONS, lcons=LCONS, uvowels=UVOWELS, lvowels=LVOWELS,)

INDEX = '(?:[0-9]?[0-9]?|[xX])'
MOD = '(?:@[tgšcv]|@90|@180)'
CRIT_MODS = re.compile(r'@(?:v|c|t|g|90|180)')
CON = '(?:[x:$+×&%]|ue)'
NUMBER_CON = r'\.,;+x'

NUMBER_TYPE = r'(?:ŠAR2|IKU|AŠ|DIŠ|BUR3|GEŠ2|U|BARIG|EŠE3|BAN2)(?:@(?:c|v|t|90|180))*'
SIMPLE_NUMBER = re.compile(r'(?:[1-9][0-9]*/[1-9][0-9]*|0|[1-9][0-9]*[½⅛⅜⅝¼½⅓⅔]?|[½⅛⅜⅝¼½⅓⅔]|[nNxX…])(?:\({number_type}\))?\+?'.format(number_type = NUMBER_TYPE))
NUMBER_CORE = r'(?P<number>{simple_number}\*?(?:[{con}]/?(?&number)|[{con}]?/?\((?:(?&number))\))*)'.format(simple_number=SIMPLE_NUMBER.pattern, con=NUMBER_CON)
NUMBER = re.compile(r'\+?{core}\+?\.?(?:{{ša}})?'.format(core=NUMBER_CORE))
SIMPLE_SIGN = r'(?:{usyll}+[0-9]*|{simple_number}|(?:LAK|KWU|REC|RSP)[0-9]+[a-c]?){mod}*'.format(usyll = USYLL, simple_number=SIMPLE_NUMBER.pattern, mod=MOD)
SIGN = re.compile(r'(?:{simple_sign}|\((?R)\))(?:(?:{con}|\.)(?R))?'.format(simple_sign=SIMPLE_SIGN, con=CON))
BROKENSIGN = re.compile(r'(?:{simple_sign}|[Xx…]|\((?R)\))(?:(?:{con}|\.)(?R))?'.format(simple_sign=SIMPLE_SIGN, con=CON))
VALUE = re.compile(r'(?:{lsyll}+{index}(?:{crit_mods})*|d)'.format(lsyll = LSYLL, index=INDEX, crit_mods=CRIT_MODS.pattern))
CAPITALIZED_VALUE = re.compile(r'{csyll}{lsyll}*{index}(?:{crit_mods})*'.format(csyll=CSYLL, lsyll=LSYLL, index=INDEX, crit_mods=CRIT_MODS.pattern))

DIVISION = re.compile(r'[1-9][0-9]*/[1-9][0-9]*')
CALCULATION = re.compile(r'(?P<calculation>{number}(?:[+x](?&calculation)|x\((?&calculation)\))+)'.format(number=SIMPLE_NUMBER.pattern))

RBRACKET_MAP = {'[': ']', '⸢': '⸣', '〈': '〉', '«': '»', '‹': '›', '{': '}', '<': '>'}
LCRITBRACKETS = r'\[⸢〈«'
RCRITBRACKETS = ''.join([c if c == '\\' else RBRACKET_MAP[c] for c in LCRITBRACKETS])
CRITBRACKETS = RCRITBRACKETS+LCRITBRACKETS
LOPBRACKETS = r'\{<‹'
ROPBRACKETS = ''.join([c if c == '\\' else RBRACKET_MAP[c] for c in LOPBRACKETS])
LBRACKETS = LCRITBRACKETS+LOPBRACKETS
RBRACKETS = RCRITBRACKETS+ROPBRACKETS

BRACKETS = LBRACKETS + RBRACKETS
CRITS = r'\?!~°^÷\*#'
RE_CRITS = re.compile(r'[{crits}]'.format(crits=CRITS))
OPS = r'{brackets}{crits}"\|\(\)\.\-/:,;'.format(brackets=BRACKETS, crits=CRITS)
OPERATORS = re.compile('[{operators}]'.format(operators=OPS))

SIMPLE_COMMENT = r'(?P<comment>\((?:[^\(\)]+|(?&comment))*\))'
COMMENT = re.compile(r'(?P<core>{comment}|\?)(?P<suffix>[{rbrackets}]*)'.format(comment=SIMPLE_COMMENT, rbrackets=RBRACKETS))
DESC = re.compile(r'"[^"]*"')

PREFIX = r'[{lbrackets}]*'.format(lbrackets=LBRACKETS)
SUFFIX = r'(?:[{rbrackets}{crits}]|{comment})*'.format(rbrackets=RBRACKETS, crits=CRITS, comment=SIMPLE_COMMENT)
TOKEN_CORE = r'(?:{desc}|{division}|(?:[^{operators}]|\[|\])*[^{operators}]|\|[^\|]+\|)'.format(desc = DESC.pattern, operators=OPS, division=DIVISION.pattern)
#TOKENS_CORE = r'(?:{desc}|{division}|(?:[^{operators}]|[{crits}{critbrackets}])*[^{operators}]|\|[^\|]+\|)'.format(desc = DESC.pattern, operators=OPS, division=DIVISION.pattern, crits=CRITS, critbrackets=CRITBRACKETS)

TOKENS_MAIN = r'(?:[^"\|\(\)\.\-/:,;{lopbrackets}{ropbrackets}]|(?P<comment2>\((?:[^\(\)]+|(?&comment2))*\)))*(?:[^"\|\(\)\.\-/:,;{lbrackets}{ropbrackets}]|(?P<comment3>\((?:[^\(\)]+|(?&comment3))*\)))'.format(lopbrackets = LOPBRACKETS, ropbrackets=ROPBRACKETS, lbrackets=LBRACKETS)
TOKENS_CORE = r'(?:{desc}|{division}|\|[^\|]+\||{main}|.)'.format(desc = DESC.pattern, division=DIVISION.pattern, main=TOKENS_MAIN)
TOKENS = re.compile(r'({prefix}{core}{suffix})'.format(prefix=PREFIX, core=TOKENS_CORE, suffix=SUFFIX))

#TOKENS = re.compile(r'({prefix}{core}{suffix}|.)'.format(prefix=PREFIX, core=TOKENS_CORE, suffix=SUFFIX, operators=OPS))
TOKEN = re.compile(r'(?P<prefix>{prefix})(?P<core>{core})(?P<suffix>{suffix})'.format(prefix=PREFIX, core=TOKEN_CORE, suffix=SUFFIX))



PN_MARKERS = re.compile(r'{(p|o|fl|fe|te|M)}')

WORD = re.compile(r'((?:{comment}|{desc}|[^ ()"]+)+)'.format(comment=SIMPLE_COMMENT, desc=DESC.pattern))


class State():
    def __init__(self, citation, annotated):
        self.citation = citation

        self.annotated = annotated

        self.signs = []              # [citation, lineID, wordID, signID, value, sign_type, value_type, segment_type, ppID, critic, comment]
        self.words = []              # [citation, wordID, lemmaID, akk, comment]
        self.lines = []              # [citation, lineID, part, col, line, comment]

        self.akk = False

        self.amended = False
        self.damaged = False
        self.corrected = False
        self.deleted = False

        self.inverted = False
        self.newline = False

        self.multiline = False

        self.wordInitial = True
        self.lineInitial = True

        self.signID = -1
        self.wordID = -1
        self.lineID = -1
        self.pnID = 0
        self.pnID_next = 2

        self.separated = False

        self.det = False
        self.PC = False
        self.prefixSuper = False
        self.previousSuper = False

        self.warnings = []


    def warning(self, warning_type, part=''):
        self.warnings.append((warning_type, part, self.content, self.lineID, self.citation, self.location))


    def initLine(self, line):

        self.lineInitial = True

        if self.separated or (self.previousSuper and self.prefixSuper):
            self.multiline = True
            #self.separated = False

        if self.amended:
            self.warning('Amendation Error1')
        self.amended = False

        if self.damaged or self.corrected or self.deleted:
            self.warning('Critics Error')        
        self.damaged = False
        self.corrected = False
        self.deleted = False

        if self.inverted or self.newline:
            self.warning('Inversion/Newline Error')
        self.inverted = False
        self.newline = False

        if self.det or self.PC:
            self.warning('Superscript Error9')
        self.det = False
        self.PC = False

        self.lineID, part, col, lineNo, self.content, comment = line
        self.lines.append([self.citation, str(self.lineID), part, col, lineNo, comment])
        self.location = ' '.join([part, col, lineNo])

    
    def processWord(self, word):
        self.akk = True if '{akk}' in word else False           # TODO Error checking
        word = word.replace('{akk}', '')

        res = COMMENT.fullmatch(word)
        if res:
            if self.lineInitial:
                self.warning('Comment Error', word)
            else:
                self.words[-1][4] += ('; ' if self.words[-1][4] else '') + re.sub(r'^\( *| *\)', '', res.group('core'))
                self._processSuffix(res.group('suffix'))
            return ''

        if self.multiline or re.match(r'^([\.-]|{ki})', word):
            if not self.lineInitial:
                self.warning('Multiline Error')
            else:
                self.warning('Multiline')
            self.multiline = False
            return word
    
        self.wordID += 1
        self.pnID = 0

        self.wordInitial = True
        self.separated = True

        if self.previousSuper and self.prefixSuper:
            self.warning('Superscript Error9')
        self.prefixSuper = False
        self.previousSuper = False

        if PN_MARKERS.match(word):
            word = PN_MARKERS.sub('', word)
            self.pnID = self.pnID_next
            self.pnID_next += 1
                                  
        self.segment = 'prefix' if '‹' in word else 'stem'  

        self.words.append([self.citation, str(self.wordID), '0', str(self.akk), ''])

        return word


    def processOperator(self, op):
        if not OPERATORS.fullmatch(op):
            return False

        if op == '/':
            self.newline = True
        elif op in '-.:,;':
            self._processSeparator(op)
        else:
            self.warning('Operator Error', op)
        return True


    def _processSeparator(self, sep):
        if self.separated:
            self.warning("Double separator", sep)

        if self.previousSuper and self.prefixSuper:
            if sep == ':':
                self.warning('Inverted Superscript')
            else:
                self.warning('Separator after DET/PC')
        self.previousSuper = False

        if sep == ':':
            self.inverted = True

        self.separated = True


    def processCalculation(self, segment):
        segment_stripped = re.sub(r'[{critbrackets}{crits}]'.format(critbrackets=CRITBRACKETS, crits=CRITS), '', segment)
        res = CALCULATION.fullmatch(segment_stripped)
        if not res:
            return False

        inverted, newline, pnID = self._process()
        crits, condition = self._getCalculationCondition(segment) 

        self.signs.append([self.citation, str(self.lineID), str(self.wordID), str(self.signID), segment_stripped, 'NUM', '', '', pnID, crits, condition, inverted, newline, ''])

        return True

    def _getCalculationCondition(self, segment):
        crits = ''.join(list(dict.fromkeys(RE_CRITS.findall(segment))))
        segment = RE_CRITS.sub('', segment)
        
        prefix = re.match(r'[{lcritbrackets}]*'.format(lcritbrackets=LCRITBRACKETS), segment).group(0)
        suffix = re.search(r'[{lcritbrackets}]*$'.format(lcritbrackets=LCRITBRACKETS), segment).group(0)
        brackets = ''.join(re.findall(r'[{critbrackets}]'.format(critbrackets=CRITBRACKETS), segment))
        lbrackets = re.sub(r'[^{lcritbrackets}]'.format(lcritbrackets=LCRITBRACKETS), '', brackets)
        
        brackets_ = re.sub(r'^[\]⸣]|[\[⸢]$', '', brackets)
        if len(brackets_) % 2:
            self.warning('Amendation Error', segment) 
        for l, r in zip(brackets_[::2], brackets_[1::2]):
            if l not in RBRACKET_MAP or r != RBRACKET_MAP[l]:
                self.warning('Amendation Error', segment) 

        condition = 'INTACT'
        if len(brackets) == len(prefix)+len(suffix):
            self._processPrefix(prefix)
            condition = self._getCondition('', 'NUM')
            self._processSuffix(suffix)
        else:
            hasState = self.amended or self.damaged or self.deleted or self.corrected
            if brackets.startswith(']'):
                if not self.amended:
                    self.warning('Amendation Error', segment)
                condition = 'DAMAGED'
                self.amended = False
            elif brackets.startswith('⸣'):
                if not self.damaged:
                    self.warning('Amendation Error', segment)
                condition = 'DAMAGED'
                self.damaged = False
            elif hasState:
                self.warning('Amendation Error', segment) 

            if brackets.endswith('['):
                condition = 'DAMAGED'
                self.amended = True
            if brackets.endswith('⸢'):
                condition = 'DAMAGED'
                self.damaged = True

            if '[' in lbrackets or '⸢' in lbrackets:
                condition = 'DAMAGED'
            if '«' in lbrackets or '〈' in lbrackets:
                crits += '!'

        return crits, condition


    def processToken(self, token):
        res = TOKEN.fullmatch(token)
        if not res:
            self.warning('Value Error', token)
            return
        
        self._processPrefix(res.group('prefix'))
        if not (self.det or self.PC) and self.previousSuper and not self.prefixSuper:
            self.warning('Superscript Error6', token)
        if not (self.previousSuper or ((self.det or self.PC) and not self.prefixSuper)) and not self.separated:
            self.warning('Separator Error', token)
        self.previousSuper = False

        cl, val, seg = self._examineCore(res.group('core'))
        if not cl:
            self.warning('Value Error', token)
            return

        condition = self._getCondition(res.group('core'), cl)
        sign, crits = self._processCore(res.group('core'), cl)

        crits2, condition2, comments = self._processSuffix(res.group('suffix'))
        crits += crits2
        if condition2:
            condition = condition2

        inverted, newline, pnID = self._process()

        self.signs.append([self.citation, str(self.lineID), str(self.wordID), str(self.signID), sign, cl, val, seg, pnID, crits, condition, inverted, newline, comments])


    def _process(self):      

        inverted = str(self.inverted)
        self.inverted = False
        newline = str(self.newline)
        self.newline = False

        pnID = str(self.pnID)
        if self.pnID > 1:
            self.pnID = 1
        
        self.signID += 1
        self.separated = False
        self.wordInitial = False
        self.lineInitial = False

        return inverted, newline, pnID

    
    def _getCondition(self, sign, cl):
    
        condition = 'INTACT'

        if self.damaged:
            condition = 'DAMAGED'
        if self.amended:
            condition = 'GONE'
        if self.corrected:
            condition = 'CORRECTED'
        if self.deleted:
            condition = 'DELETED'

        if '[' in sign:
            if self.amended or self.damaged or sign.endswith('['):
                self.warning('Amendation Error', sign)
            self.amended = True
            condition = 'DAMAGED'
        if ']' in sign:
            if not self.amended or sign.startswith(']'):
                self.warning('Amendation Error', sign)
            self.amended = False
            condition = 'DAMAGED'

        if cl == 'BRK':
            if sign == '…':
                condition = 'GONE'
            else:
                condition = 'DAMAGED'
        
        return condition


    def _processCore(self, core, cl):

        core = re.sub(r'[\[\]\|]', '', core) 

        if CAPITALIZED_VALUE.fullmatch(core):# and pnID > 0:
            core = core.lower()
        #if core == 'šu2+1':
        #    core = '1/3'
        #if core == 'šu2+2':
        #    core = '2/3'
        #if core == 'o':
        #    core = 'X'

        crit = ''
        if cl == 'VALUE':
            res = CRIT_MODS.findall(core)
            for r in res:
                if r == '@t':
                    crit += 't'
                elif r == '@c':
                    crit += '°'
                elif r == '@v':
                    crit += '~'
                elif r == '@g':
                    crit += 'g'
                elif r == '@90':
                    crit += '^'
                elif r == '@180':
                    crit += '÷'
            core = CRIT_MODS.sub('', core)

        if cl == 'SIGN':
            core = core.replace('x', '×')
            core = core.replace('ue', '&')
        elif cl == 'BRK':
            if core == 'x':
                core = 'X'
        elif cl in ['PCP', 'PCS', 'DETP', 'DETS', 'VALUE', '']:
            core = core.replace('X', 'x')

        return core, crit


    def _examineCore(self, core):
        core = re.sub(r'[\[\]\|]', '', core)
        seg = '' if not self.annotated else 'PREFIX' if self.segment == 'prefix' else 'STEM' if self.segment == 'stem' else 'SUFFIX'
        cl = ''
        val = ''
        if self.akk and self.segment == 'stem':
            cl = 'AKK'
            val = 'P'
        if core == '…' or core == 'X':
            cl = 'BRK'
        elif core == '=' or core=='□':
            cl = 'SPACE'
        elif DESC.fullmatch(core):
            cl = 'DESC'
        elif NUMBER.fullmatch(core):
            if re.search('[…xXnN]', core):
                cl = 'BRK'
            else:
                cl = 'NUM'
        elif VALUE.fullmatch(core):
            cl = 'VALUE'
            if seg in ['PREFIX', 'SUFFIX']:
                val = 'P'
        elif CAPITALIZED_VALUE.fullmatch(core):
            cl = 'VALUE'
            if not self.pnID:
                self.pnID = self.pnID_next
                self.pnID_next += 1
        elif SIGN.fullmatch(core):
            cl = 'SIGN'
        elif BROKENSIGN.fullmatch(core):
            cl = 'BRK'
        else:
            return '', '', ''

        if self.det:
            val = 'DET'
            if self.prefixSuper:
                cl = 'DETP'
            else:
                cl = 'DETS'
            if cl in ['SPACE', 'DESC', 'NUM', 'AKK']:
                self.warning('Superscript Error5')

        if self.PC:
            val = 'PC'
            if self.prefixSuper:
                cl = 'PCP'
            else:
                cl = 'PCS'
            if cl in ['SPACE', 'DESC', 'NUM']:
                self.warning('Superscript Error4')    

        return cl, val, seg

    
    def _processPrefix(self, prefix):
        for op in prefix:
            if op == '[':
                if self.amended:
                    self.warning('Prefix Error')
                self.amended = True
            elif op == '⸢':
                if self.damaged:
                    self.warning('Prefix Error')
                self.damaged = True
            elif op == '〈':
                if self.corrected:
                    self.warning('Prefix Error')
                self.corrected = True
            elif op == '«':
                if self.deleted:
                    self.warning('Prefix Error')
                self.deleted = True
            elif op == '‹':
                if self.segment != 'prefix':
                    self.warning('Segmentation Error')
                self.segment = 'stem'
            elif op in '{<':
                if self.PC or self.det:
                    self.warning('Superscript Error3')
                if not self.previousSuper:
                    self.prefixSuper = self.separated
                    if self.inverted:
                        self.warning('Inverted Superscript')
                if op == '{':
                    self.det = True 
                else:
                    self.PC = True
            else:
                self.warning('Logic Error1', prefix)


    def _processSuffix(self, suffix):
        comments = []
        crits = ''
        condition = ''
        for comment in re.findall(SIMPLE_COMMENT, suffix):
            comments.append(comment[1:-1])
            suffix = suffix.replace(comment, '')
        for op in suffix:
            if op in CRITS:
                crits += op
            elif op == ']':
                if not self.amended:
                    self.warning('Suffix Error')
                self.amended = False
            elif op == '⸣':
                if not self.damaged:
                    self.warning('Suffix Error')
                self.damaged = False
            elif op == '〉':
                if not self.corrected:
                    self.warning('Suffix Error')
                self.corrected = False
            elif op == '»':
                if not self.deleted:
                    self.warning('Suffix Error')
                self.deleted = False
            elif op == '›':
                if self.segment != 'stem':
                    self.warning('Segmentation Error')
                self.segment = 'suffix'
            elif op == '#':
                condition = 'DAMAGED'
            elif op == '}':
                if not self.det:
                    self.warning('Superscript Error2')
                self.det = False
                self.previousSuper = True
            elif op == '>':
                if not self.PC:
                    self.warning('Superscript Error1')
                self.PC = False
                self.previousSuper = True
            else:
                self.warning('Logic Error2', suffix)
        return crits, condition, '; '.join(comments)

    def finalize(self):
        if self.multiline or self.separated:
            self.warning('Multiline Error')
     


def parse(text, citation, annotated):

    state = State(citation, annotated)

    for line in text:
        state.initLine(line)

        for word in WORD.findall(state.content):
            word = state.processWord(word[0])    
            if not word:
                continue

            for token in TOKENS.findall(word):
                token = token[0]
                if state.processOperator(token):
                    continue        
                if state.processCalculation(token):
                    continue       
                state.processToken(token) 
    
    state.finalize()
    return state.signs, state.words, state.lines, state.warnings
