grammar Cuneiform;


fragment LCON  : [bdgĝhḫjklmnpqrřsšṣtṭwyz’];
fragment LVOWEL: [aeiu];
fragment UCON  : [BDGĜHḪJKLMNPQRŘSŠṢTṬWYZ];
fragment UVOWEL: [AEIU];
fragment USYLL : ( ( UCON | '’' ) ']'? '['? )? UVOWEL ( ']'? '['? ( UCON | '’' ) )?;
fragment LSYLL : ( LCON ']'? '['? )? LVOWEL ( ']'? '['? LCON )?;
fragment CSYLL : UCON ']'? '['? LVOWEL ( ']'? '['? LCON )? 
               | ( '’' ']'? '['? ) UVOWEL ( ']'? '['? LCON )?
               | UVOWEL ']'? '['? LCON;
fragment PNUM  : [1-9] [0-9]*;
fragment FRAC  : [½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅐⅛⅜⅝⅞⅑⅒];
fragment INDEX : [1-9] [0-9]?;

fragment ABBR  : 'B' ']'? '['? 'A' ']'? '['? 'U' 
               | 'L' ']'? '['? 'A' ']'? '['? 'K' 
               | 'K' ']'? '['? 'W' ']'? '['? 'U' 
               | 'R' ']'? '['? 'E' ']'? '['? 'C' 
               | 'R' ']'? '['? 'S' ']'? '['? 'P' 
               | 'Z' ']'? '['? 'A' ']'? '['? 'T' ']'? '['? 'U' 
               | 'E' ']'? '['? 'L' ']'? '['? 'L' ']'? '['? 'E' ']'? '['? 'S'
               | 'U' ']'? '['? 'K' ']'? '['? 'N';

DESC           : '"' ~["\n]* '"';
SHIFT          : '%' [a-z] ~[ \n]*;
NUMBER         : '0' | ( PNUM ( '/' PNUM | FRAC )? | FRAC ) ( '(' [cdf] ')' )?;

VOWELSIGN      : UVOWEL INDEX?;
SIGN           : USYLL ( ']'? '['? USYLL )* INDEX?;
NNSIGN         : ABBR ( PNUM | [0-9] [0-9] [0-9] ) ( [a-c] | 'bis' | 'ter' )?;
VALUE          : LSYLL ( ']'? '['? LSYLL )* (INDEX | X)? ('⁺'+ | '⁻'+)?
               | '’';
CVALUE         : CSYLL ( ']'? '['? LSYLL )* (INDEX | X)? ('⁺'+ | '⁻'+)?
               | UVOWEL ( ']'? '['? LSYLL )+ (INDEX | X)? ('⁺'+ | '⁻'+)?;

X              : [Xx];
N              : [Nn] ( '(' [cdf] ')' )?;
D              : 'd';
DUAL           : 'II';
MOD            : '@' ( [tgšnkzicdfvabx] | '270' | '180' | '90' | '45' | '4' );
CRIT           : [!~*#];
VARIANT        : '~' ( [a-z] PNUM? )?;
OCONDITION     : [[⸢‹«];
CCONDITION     : [\]⸣›»];
DOUBLEBAR      : '||';

VDIVIDER       : '$' ~'$'* '$';

DASHNL         : '-' ' '* '\n' ' '*;
DOUBLEDASHNL   : '--' ' '* '\n' ' '*;
DOTNL          : '.' ' '* '\n' ' '*;
COMMANL        : ',' ' '* '\n' ' '*;
TILDENL        : '~' ' '* '\n' ' '*;
STILDENL       : ' '* '\n' ' '* '~';
SPACE          : ' '+;

DOUBLEDASH     : '--';

QMARK          : '?';

OTHER          : .;

text           : ( line ( nl line )* )? EOF;
line           : space? oConLog? ( compound | hdivCompound | shift ) ( spaceSep ( compound | hdivCompound | shift ) )* cConLog? space?
               | ( space? shift )? vdivCompound;

vdivCompound   : space? openCondition? vdividerAtom ( closeCondition? space? compoundComment)? closeCondition? space?;
hdivCompound   : hdividerAtom ( closeCondition? space? compoundComment )?;
compound       : word ( doubleDash word )* ( cConLog? space compoundComment )*;

word           : ( cprefix | prefix ) ( dash | colonSep ) ';' openCondition? stem ( closeCondition? ';' ( ( dash | colonSep ) suffix )? )?
               | ( ';' openCondition? )? ( cstem | stem ) closeCondition? ';' ( ( dash | colonSep ) suffix )
               | ';' openCondition? ( cstem | stem ) closeCondition? ';'
               | csegment
               | segment;

prefix         : segment;
cprefix        : csegment;
stem           : segment;
cstem          : csegment;
suffix         : segment;

segment        : part ( ( dash | colonSep ) part )*;
csegment       : cpart  ( ( dash | colonSep ) part )*;

part           : ( detp | pcp )* ( values | numbers | signsX ) ( ( detc | pcc )+ ( values | numbers | signsX ) )* ( dets | pcs )*;
cpart          : ( detp | pcp )* cvalues ( ( detc | pcc )+ ( values | numbers | signsX ) )* ( dets | pcs )*
               | '&' ( detp | pcp )* ( cvalues | values | numbers | signsX ) ( ( detc | pcc )+ ( values | numbers | signsX ) )* ( dets | pcs )*;

values         : valueAtom ( plusSep valueAtom )* ( plusSep ( numbers | signsX ) )?;
cvalues        : cvalueAtom ( plusSep valueAtom )* ( plusSep ( numbers | signsX ) )?;
numbers        : ( maybeNumberAtom numberSep )* numberAtom ( numberSep ( numberAtom | maybeNumberAtom ) )* ( plusSep ( values | signs ) )?;
signs          : ( maybeSignAtom ( dot | colonSep ) )* signAtom ( ( dot | colonSep ) ( signAtom | maybeSignAtom ) )* ( plusSep ( values | numbers ) )?;
signsX         : signs
               | breakAtom ( dot breakAtom )* ( plusSep values )?;


// Determinatives & Phonetic Complements

detp           : det ( colonSep | plusSep | nullSep );
dets           : ( colonSep | plusSep | nullSep ) det;
detc           : ( colonSep | plusSep | nullSep ) det ( colonSep | plusSep | nullSep );
pcp            : pc ( colonSep | plusSep | nullSep );
pcs            : ( colonSep | plusSep | nullSep ) pc;
pcc            : ( colonSep | plusSep | nullSep ) pc ( colonSep | plusSep | nullSep );

det            : '{' openCondition? ( detValueAtom | signAtom | maybeSignAtom | valueAtom ) ( ( dot | colonSep ) ( detValueAtom | signAtom | maybeSignAtom | valueAtom ) )* closeCondition? '}';
pc             : '<' openCondition? ( signAtom | maybeSignAtom | valueAtom ) ( ( dash | colonSep ) ( signAtom | maybeSignAtom | valueAtom ) )* closeCondition? '>';


// Atoms

valueAtom      : value;
cvalueAtom     : cvalue;
detValueAtom   : detValue;
signAtom       : signChar;
maybeSignAtom  : maybeSign;
numberAtom     : number;
maybeNumberAtom: maybeNumber;
hdividerAtom   : hdivider;
vdividerAtom   : vdivider;
breakAtom      : x 
               | ellipsis;


// Characters

value          : ( valueT | descT ) variant? mod* ( crit | signSpec | comment )*;
cvalue         : cvalueT variant? mod* ( crit | signSpec | comment )*;
detValue       : ( dT | dualT ) ( crit | signSpec | comment )*;
signChar       : sign ( crit | signSpec | comment )*;
simpleNumber   : ( ( plusCrit? | unaryMinusOp? ) numberT | unaryMinusOp? numberT plusCrit ) ( crit | signSpec | comment )*;
x              : xT ( crit | signSpec | comment )*;
ellipsis       : ellipsisT ( crit | comment )*;
vdivider       : vdividerT ( crit | comment )*;
hdivider       : hdividerT ( crit | comment )*;


// Signs

sign           : simpleSign
               | signComplex
               | modifiedSign
               | '|' openCondition? explicitSign closeCondition? '|';
explicitSign   : ( maybeSign dotOp )* sign ( dotOp ( sign | maybeSign ) )*;
signComplex    : signSum
               | signProd;
signSum        : ( maybeSign plusOp )* signSummand ( plusOp ( signSummand | maybeSign ) )+
               | ( maybeSign plusOp )+ signSummand;
signSummand    : simpleSign
               | signProd
               | modifiedSign;
signProd       : ( maybeSign ( timesOp | signOp ) )* signFactor ( ( timesOp | signOp ) ( signFactor | maybeSign ) )+
               | ( maybeSign ( timesOp | signOp ) )+ signFactor;
signFactor     : simpleSign
               | modifiedSign
               | lparenOp openCondition? explicitSign closeCondition? rparenOp;
modifiedSign   : lparenOp openCondition? explicitSign closeCondition? rparenOp mod+; 

simpleSign     : ( signT | nnsignT ) variant? mod*;
maybeSign      : x 
               | ellipsis;


// Numbers

number         : simpleNumber
               | numberComplex;
numberComplex  : numberSum
               | numberProd;
numberSum      : ( maybeNumber numberPlusOp )* ( numberProd | simpleNumber ) ( numberPlusOp ( numberProd | simpleNumber | maybeNumber ) )+
               | ( maybeNumber numberPlusOp )+ ( numberProd | simpleNumber );
numberProd     : ( maybeNumber ( numberTimesOp | numberDivOp ) )* numberFactor ( ( numberTimesOp | numberDivOp ) ( numberFactor | maybeNumber ) )+
               | ( maybeNumber ( numberTimesOp | numberDivOp ) )+ numberFactor;
numberFactor   : simpleNumber 
               | lparenOp openCondition? numberSum closeCondition? rparenOp;
maybeNumber    : x 
               | ellipsis;



// Separators

dash           : cConLog? ( '-' slash? | dashNl ) oConLog?;
doubleDash     : cConLog? ( DOUBLEDASH ( slash | colon | ligPlus )? | doubleDashNl ) oConLog?;
dot            : closeCondition? ( '.' ( slash )? | dotNl ) openCondition?;
colonSep       : cConLog? colon ( slash )? oConLog?;
plusSep        : closeCondition? ligPlus openCondition?;
spaceSep       : cConLog? ( space ( slash space | colon space )? ) oConLog?;
numberSep      : closeCondition? ( ('.'|',') ( slash )? | dotNl | commaNl ) openCondition?;
nullSep        : cConLog? ( slash | tildeNl )? oConLog?;
ligPlus        : '+';


// Operators

numberPlusOp   : closeCondition? plusOp openCondition?;
numberTimesOp  : closeCondition? timesOp openCondition?;
numberDivOp    : closeCondition? divOp openCondition?;

dotOp          : '.';
plusOp         : '+';
timesOp        : X | '×';
divOp          : '/';
signOp         : '&' | '%' | '@';
lparenOp       : '(';
rparenOp       : ')';
unaryMinusOp   : '-';


// Conditions

openCondition  : OCONDITION;
closeCondition : CCONDITION;

oConLog        : openCondition log?
               | log openCondition?;
cConLog        : closeCondition log?
               | log closeCondition?;


// Terminals

valueT         : VALUE;
cvalueT        : CVALUE;
dT             : D;
dualT          : DUAL;
signT          : SIGN | VOWELSIGN;
nnsignT        : NNSIGN;
numberT        : NUMBER | N;
xT             : X;
numberXT       : X;
ellipsisT      : '…';
descT          : DESC;
vdividerT      : '=' | '–' | VDIVIDER;
hdividerT      : '|' | DOUBLEBAR;
space          : SPACE;
colon          : ':';

mod            : MOD;
crit           : CRIT | QMARK;
variant        : VARIANT;
plusCrit       : '+';

log            : '_';

compoundComment: '(' ( subcomment | ~( '(' | ')' | '\n' ) )* ')';
subcomment     : '(' ( subcomment | ~( '(' | ')' | '\n' ) )* ')';
comment        : '(' ( subcomment | ~( '(' | ')' | '\n' ) )* QMARK ')';

signSpec       : '(' explicitSign ')';

shift          : SHIFT;

slash          : '/';
nl             : '\n';
dashNl         : DASHNL;
doubleDashNl   : DOUBLEDASHNL;
dotNl          : DOTNL;
commaNl        : COMMANL;
tildeNl        : TILDENL;
