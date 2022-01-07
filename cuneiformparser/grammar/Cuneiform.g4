grammar Cuneiform;


fragment LCON  : [bdgĝhḫjklmnpqrřsšṣtṭwyz’];
fragment LVOWEL: [aeiu];
fragment UCON  : [BDGĜHḪJKLMNPQRŘSŠṢTṬWYZ];
fragment UVOWEL: [AEIU];
fragment USYLL : ( UCON ']'? '['? )? UVOWEL ( ']'? '['? UCON )?;
fragment LSYLL : ( LCON ']'? '['? )? LVOWEL ( ']'? '['? LCON )?;
fragment CSYLL : UCON ']'? '['? LVOWEL ( ']'? '['? LCON )? 
               | ( '’' ']'? '['? ) UVOWEL ( ']'? '['? LCON )?
               | UVOWEL ']'? '['? LCON;
fragment PNUM  : [1-9] [0-9]*;
fragment FRAC  : [½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅐⅛⅜⅝⅞⅑⅒];

DESC           : '"' ~["\n]* '"';
SHIFT           : '%' ~[ \n]+;
NUMBER         : '0' | PNUM ( '/' PNUM | FRAC )? | FRAC;

VOWELSIGN      : UVOWEL PNUM?;
SIGN           : USYLL ( ']'? '['? USYLL )* PNUM?;
NNSIGN         : ( 'BAU' | 'LAK' | 'KWU' | 'REC' | 'RSP' | 'ZATU' | 'ELLES' ) ( PNUM | [0-9] [0-9] [0-9] ) ( [a-c] | 'bis' | 'ter' )?;
VALUE          : LSYLL ( ']'? '['? LSYLL )* (PNUM | X)? ('⁺'+ | '⁻'+)?
               | '’';
CVALUE         : CSYLL ( ']'? '['? LSYLL )* (PNUM | X)? ('⁺'+ | '⁻'+)?
               | UVOWEL ( ']'? '['? LSYLL )+ (PNUM | X)? ('⁺'+ | '⁻'+)?;

X              : [Xx];
N              : [Nn];
D              : 'd';
DUAL           : 'II';
MOD            : '@' ( [tgšnkzicvabx] | '90' );
CRIT           : [?!~*#];
VARIANT        : '~' ( [a-z] PNUM? )?;
ABOVE          : '&' | '%';
OCONDITION     : [[⸢‹«];
CCONDITION     : [\]⸣›»];
DOUBLEBAR      : '||';

DASHNL         : '-' ' '* '\n' ' '*;
DOUBLEDASHNL   : '--' ' '* '\n' ' '*;
DOTNL          : '.' ' '* '\n' ' '*;
COMMANL        : ',' ' '* '\n' ' '*;
SEMICOLONNL    : ';' ' '* '\n' ' '*;
TILDENL        : '~' ' '* '\n' ' '*;
STILDENL       : ' '* '\n' ' '* '~';
SPACE          : ' '+;

OTHER          : .;


text           : line ( nl line )* EOF;
line           : space? openCondition? ( compound | hdivCompound ) ( spaceSep ( compound | hdivCompound ) )* closeCondition? space?
               | vdivCompound;

vdivCompound   : space? openCondition? vdividerAtom ( closeCondition? space? compoundComment)? closeCondition? space?
               | emptyLineAtom;
hdivCompound   : hdividerAtom ( closeCondition? space? compoundComment )?;
compound       : ( shift space openCondition? )* word ( doubleDash word )* ( closeCondition? space compoundComment )*;

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

part           : ( detp | pcp )* ( valueAtom | signs | numbers ) ( ( detc | pcc )+ ( valueAtom | signs | numbers ) )* ( dets | pcs )*;
cpart          : ( detp | pcp )* cvalueAtom ( ( detc | pcc )+ ( valueAtom | signs | numbers ) )* ( dets | pcs )*;

numbers        : ( maybeNumberAtom numberSep )* numberAtom ( numberSep ( numberAtom | maybeNumberAtom ) )*;
signs          : ( maybeSignAtom ( dot | colon ) )* signAtom ( ( dot | colon ) ( signAtom | maybeSignAtom ) )*
               | xAtom ( dot xAtom )*;



// Determinatives & Phonetic Complements

detp           : det ( colon | nullSepP );
dets           : ( colon | nullSepS ) det;
detc           : ( colon | nullSepS ) det ( colon | nullSepP );
pcp            : pc ( colon | nullSepP );
pcs            : ( colon | nullSepS ) pc;
pcc            : ( colon | nullSepS ) pc ( colon | nullSepP );

det            : '{' openCondition? ( detValueAtom | signAtom | valueAtom ) ( ( dot | colon ) ( detValueAtom | signAtom | valueAtom ) )* closeCondition? '}';
pc             : '<' openCondition? ( sign | valueAtom ) ( ( dash | colon ) ( sign | valueAtom ) )* closeCondition? '>';


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
               | '|' openCondition? explicitSign closeCondition? '|' ( crit | comment )*;
explicitSign   : ( maybeSign dotOp )* sign ( dotOp ( sign | maybeSign ) )*;
signComplex    : signSum
               | signProd;
signSum        : ( maybeSign plus )* ( signProd | simpleSign ) ( plus ( signProd | simpleSign | maybeSign ) )+
               | ( maybeSign plus )+ ( signProd | simpleSign );
signProd       : ( maybeSign ( times | above ) )* signFactor ( ( times | above ) ( signFactor | maybeSign ) )+
               | ( maybeSign ( times | above ) )+ signFactor;
signFactor     : simpleSign
               | '(' openCondition? explicitSign closeCondition? ')';
maybeSign      : x
               | ambiguousSign;


// Numbers

number         : simpleNumber
               | numberComplex;
numberComplex  : numberSum
               | numberProd;
numberSum      : ( maybeNumber plus )* ( numberProd | simpleNumber ) ( plus ( numberProd | simpleNumber | maybeNumber ) )+
               | ( maybeNumber plus )+ ( numberProd | simpleNumber );
numberProd     : ( maybeNumber ( times | div ) )* numberFactor ( ( times | div ) ( numberFactor | maybeNumber ) )+
               | ( maybeNumber ( times | div ) )+ numberFactor;
numberFactor   : simpleNumber 
               | '(' openCondition? numberSum closeCondition? ')';
maybeNumber    : x 
               | ellipsis;


// Characters

value          : ( valueT | descT ) variant? mod* ( crit | comment )*;
cvalue         : cvalueT variant? mod* ( crit | comment )*;
detValue       : ( dT | dualT ) ( crit | comment )*;
simpleSign     : ( signT | nnsignT ) variant? mod* ( crit | comment )*;
ambiguousSign  : ( numberT | descT ) variant? mod* ( crit | comment )*;
simpleNumber   : ( plusCrit? numberT | numberT plusCrit ) ( crit | comment )*;
x              : xT ( crit | comment )*;
ellipsis       : ellipsisT ( crit | comment )*;
vdivider       : vdividerT crit*;
hdivider       : hdividerT crit*;


// Separators

dash           : closeCondition? ( '-' ( slash )? | DASHNL ) openCondition?;
doubleDash     : closeCondition? ( '--' ( slash )? | DOUBLEDASHNL ) openCondition?;
dot            : closeCondition? ( '.' ( slash )? | DOTNL ) openCondition?;
colon          : closeCondition? ':' ( slash )? openCondition?;
spaceSep       : closeCondition? ( space ( slash space | colon space )? ) openCondition?;
numberSep      : closeCondition? ( ('.'|','|';') ( slash )? | DOTNL | COMMANL | SEMICOLONNL ) openCondition?;
nullSepP       : closeCondition? ( slash | TILDENL )? openCondition?;
nullSepS       : closeCondition? ( slash | STILDENL )? openCondition?;

// Operators

dotOp          : closeCondition? '.' openCondition?;
plus           : closeCondition? '+' openCondition?;
times          : closeCondition? X | '×' openCondition?;
div            : closeCondition? '/' openCondition?;
above          : closeCondition? ABOVE openCondition?;


// Conditions

openCondition  : OCONDITION;
closeCondition : CCONDITION;


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
vdividerT      : '=' | '–';
hdividerT      : '|' | DOUBLEBAR;
space          : SPACE;

mod            : MOD;
crit           : CRIT;
variant        : VARIANT;
plusCrit       : '+';

compoundComment: '(' ( subcomment | ~( '(' | ')' | '\n' ) )* ')';
comment        : '(' ( subcomment | ~( '(' | ')' | '\n' ) )* ')';
subcomment     : '(' ( subcomment | ~( '(' | ')' | '\n' ) )* ')';

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





