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
               | 'E' ']'? '['? 'L' ']'? '['? 'L' ']'? '['? 'E' ']'? '['? 'S';

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
SIGNOP         : '&' | '%' | '@';
OCONDITION     : [[⸢‹«];
CCONDITION     : [\]⸣›»];
DOUBLEBAR      : '||';

VDIVIDER       : '$' ~'$'* '$';

DASHNL         : '-' ' '* '\n' ' '*;
DOUBLEDASHNL   : '--' ' '* '\n' ' '*;
DOTNL          : '.' ' '* '\n' ' '*;
COMMANL        : ',' ' '* '\n' ' '*;
SEMICOLONNL    : ';' ' '* '\n' ' '*;
TILDENL        : '~' ' '* '\n' ' '*;
STILDENL       : ' '* '\n' ' '* '~';
SPACE          : ' '+;

QMARK          : '?';

OTHER          : .;


text           : line ( nl line )* EOF;
line           : space? oConLog? ( compound | hdivCompound | shift ) ( spaceSep ( compound | hdivCompound | shift ) )* cConLog? space?
               | vdivCompound;

vdivCompound   : space? openCondition? vdividerAtom ( closeCondition? space? compoundComment)? closeCondition? space?
               | emptyLineAtom;
hdivCompound   : hdividerAtom ( closeCondition? space? compoundComment )?;
compound       : word ( doubleDash word )* ( cConLog? space compoundComment )*;

word           : ( cprefix | prefix ) ( dash | colon ) '⟨' openCondition? stem closeCondition? '⟩'( ( dash | colon ) suffix )?
               | '⟨' openCondition? ( cstem | stem ) closeCondition? '⟩' ( ( dash | colon ) suffix )?
               | csegment
               | segment;

prefix         : segment;
cprefix        : csegment;
stem           : segment;
cstem          : csegment;
suffix         : segment;

segment        : part ( ( dash | colon ) part )*;
csegment       : cpart  ( ( dash | colon ) part )*;

part           : ( detp | pcp )* ( values | numbers | signs ) ( ( detc | pcc )+ ( values | numbers | signs ) )* ( dets | pcs )*;
cpart          : ( detp | pcp )* cvalues ( ( detc | pcc )+ ( values | numbers | signs ) )* ( dets | pcs )*;

values         : valueAtom ( plus valueAtom )* ( plus ( numbers | signs ) )?;
cvalues        : cvalueAtom ( plus valueAtom )* ( plus ( numbers | signs ) )?;
numbers        : ( maybeNumberAtom numberSep )* numberAtom ( numberSep ( numberAtom | maybeNumberAtom ) )* ( plus ( values | signs ) )?;
signs          : ( maybeSignAtom ( dot | colon ) )* signAtom ( ( dot | colon ) ( signAtom | maybeSignAtom ) )* ( plus ( values | numbers ) )?
               | xAtom ( dot xAtom )* ( plus values )?;


// Determinatives & Phonetic Complements

detp           : det ( colon | plus | nullSepP );
dets           : ( colon | plus | nullSepS ) det;
detc           : ( colon | plus | nullSepS ) det ( colon | plus | nullSepP );
pcp            : pc ( colon | plus | nullSepP );
pcs            : ( colon | plus | nullSepS ) pc;
pcc            : ( colon | plus | nullSepS ) pc ( colon | plus | nullSepP );

det            : '{' openCondition? ( detValueAtom | signAtom | valueAtom ) ( ( dot | colon ) ( detValueAtom | signAtom | valueAtom ) )* closeCondition? '}';
pc             : '<' openCondition? ( signAtom | valueAtom ) ( ( dash | colon ) ( signAtom | valueAtom ) )* closeCondition? '>';


// Atoms

valueAtom      : value;
cvalueAtom     : cvalue;
detValueAtom   : detValue;
signAtom       : sign;
maybeSignAtom  : maybeSign;
numberAtom     : number;
maybeNumberAtom: maybeNumber;
hdividerAtom   : hdivider;
vdividerAtom   : vdivider;
emptyLineAtom  : space?;
xAtom          : x;


// Signs

sign           : ellipsis
               | simpleSign
               | signComplex
               | modifiedSign
               | '|' openCondition? explicitSign closeCondition? '|' ( crit | comment )*;
explicitSign   : ( maybeSign dotOp )* sign ( dotOp ( sign | maybeSign ) )*;
signComplex    : signSum
               | signProd;
signSum        : ( maybeSign plusOp )* signSummand ( plusOp ( signSummand | maybeSign ) )+
               | ( maybeSign plusOp )+ signSummand;
signSummand    : simpleSign
               | signProd
               | modifiedSign;
signProd       : ( maybeSign ( times | signOp ) )* signFactor ( ( times | signOp ) ( signFactor | maybeSign ) )+
               | ( maybeSign ( times | signOp ) )+ signFactor;
signFactor     : simpleSign
               | modifiedSign
               | lparenOp openCondition? explicitSign closeCondition? rparenOp;
modifiedSign   : lparenOp openCondition? explicitSign closeCondition? rparenOp mod+; 
maybeSign      : x;


// Numbers

number         : simpleNumber
               | numberComplex;
numberComplex  : numberSum
               | numberProd;
numberSum      : ( maybeNumber plusOp )* ( numberProd | simpleNumber ) ( plusOp ( numberProd | simpleNumber | maybeNumber ) )+
               | ( maybeNumber plusOp )+ ( numberProd | simpleNumber );
numberProd     : ( maybeNumber ( times | div ) )* numberFactor ( ( times | div ) ( numberFactor | maybeNumber ) )+
               | ( maybeNumber ( times | div ) )+ numberFactor;
numberFactor   : simpleNumber 
               | lparenOp openCondition? numberSum closeCondition? rparenOp;
maybeNumber    : x 
               | ellipsis;


// Characters

value          : ( valueT | descT ) variant? mod* ( crit | signSpec | comment )*;
cvalue         : cvalueT variant? mod* ( crit | signSpec | comment )*;
detValue       : ( dT | dualT ) ( crit | signSpec | comment )*;
simpleSign     : ( signT | nnsignT ) variant? mod* ( crit | signSpec | comment )*;
simpleNumber   : ( plusCrit? numberT | numberT plusCrit ) ( crit | signSpec | comment )*;
x              : xT ( crit | signSpec | comment )*;
ellipsis       : ellipsisT ( crit | comment )*;
vdivider       : vdividerT ( crit | comment )*;
hdivider       : hdividerT ( crit | comment )*;


// Separators

dash           : cConLog? ( '-' ( slash )? | DASHNL ) oConLog?;
doubleDash     : cConLog? ( '--' ( slash )? | DOUBLEDASHNL ) oConLog?;
dot            : closeCondition? ( '.' ( slash )? | DOTNL ) openCondition?;
colon          : cConLog? ':' ( slash )? oConLog?;
plus           : closeCondition? '+' openCondition?;
spaceSep       : cConLog? ( space ( slash space | colon space )? ) oConLog?;
numberSep      : closeCondition? ( ('.'|','|';') ( slash )? | DOTNL | COMMANL | SEMICOLONNL ) openCondition?;
nullSepP       : cConLog? ( slash | TILDENL )? oConLog?;
nullSepS       : cConLog? ( slash | STILDENL )? oConLog?;

// Operators

dotOp          : closeCondition? '.' openCondition?;
plusOp         : closeCondition? '+' openCondition?;
times          : closeCondition? X | '×' openCondition?;
div            : closeCondition? '/' openCondition?;
signOp         : closeCondition? SIGNOP openCondition?;
lparenOp       : '(';
rparenOp       : ')';


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
semicolonNl    : SEMICOLONNL;
tildeNl        : TILDENL;
sTildeNl       : STILDENL;
