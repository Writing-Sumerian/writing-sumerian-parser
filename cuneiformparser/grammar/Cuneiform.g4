grammar Cuneiform;


fragment LCON : [bdgĝhḫjklmnpqrřsšṣtṭwyz’];
fragment LVOWEL : [aeiu];
fragment UCON : [BDGĜHḪJKLMNPQRŘSŠṢTṬWYZ];
fragment UVOWEL : [AEIU];
fragment USYLL : ( UCON ']'? '['? )? UVOWEL ( ']'? '['? UCON )?;
fragment LSYLL : ( LCON ']'? '['? )? LVOWEL ( ']'? '['? LCON )?;
fragment CSYLL : UCON ']'? '['? LVOWEL ( ']'? '['? LCON )? 
               | ( '’' ']'? '['? ) UVOWEL ( ']'? '['? LCON )?
               | UVOWEL ']'? '['? LCON;
fragment PNUMBER : [1-9] [0-9]*;
fragment FRAC : [½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅐⅛⅜⅝⅞⅑⅒];

X : [Xx];
N : [Nn];

DESC : '"' ~["\n]* '"';
META : '_' ~[_\n]+ '_';
NUMBER : '0' | PNUMBER ( '/' PNUMBER | FRAC )? | FRAC;

VOWELSIGN : UVOWEL PNUMBER?;
SIGN : USYLL ( ']'? '['? USYLL )* PNUMBER?;
NNSIGN: ( 'LAK' | 'KWU' | 'REC' | 'RSP' | 'ZATU' | 'ELLES' ) ( PNUMBER | [0-9] [0-9] [0-9] ) ( [a-c] | 'bis' | 'ter' )?;
VALUE : LSYLL ( ']'? '['? LSYLL )* (PNUMBER | X)? ('⁺'+ | '⁻'+)?
      | '’';
CVALUE : CSYLL ( ']'? '['? LSYLL )* (PNUMBER | X)? ('⁺'+ | '⁻'+)?
       | UVOWEL ( ']'? '['? LSYLL )+ (PNUMBER | X)? ('⁺'+ | '⁻'+)?;

D : 'd';
DUAL : 'II';
MOD : '@' ( [tgšnkzicvabx] | '90' );
CRIT : [?!~*#];
VARIANT : '~' ( [a-z] PNUMBER? )?;
ABOVE : '&' | '%';
OCONDITION : [[⸢‹«];
CCONDITION : [\]⸣›»];
DOUBLEBAR : '||';
OTHER : .;


text : space? ( decoratedVdivider nl )* ( compound | decoratedHdivider ) ( ( spaceSep | nl decoratedVdivider ( nl decoratedVdivider )* nl ) ( compound | decoratedHdivider ) )* ( nl decoratedVdivider )* space? EOF
     | space? EOF;
compound : ( meta space )* word ( doubleDash word )* ( ( space compoundComment )+ closeCondition? )?;
word : ( ( cprefix | prefix ) ( dash | colon ) )? openCondition? '⟨' stem '⟩' closeCondition? ( ( dash | colon ) suffix )?
     | '⟨' ( cstem | stem ) '⟩' closeCondition? ( ( dash | colon ) suffix )?
     | csegment
     | segment;
prefix : segment;
cprefix : csegment;
stem : segment;
cstem: csegment;
suffix : segment;
segment : part ( ( dash | colon ) part )*;
csegment : cpart  ( ( dash | colon ) part )*;
part : ( detp | pcp )* ( decoratedValue | signs | numbers ) ( ( detc | pcc )+ ( decoratedValue | signs | numbers ) )* ( dets | pcs )*;
cpart : ( detp | pcp )* decoratedCvalue ( ( detc | pcc )+ ( decoratedValue | signs | numbers ) )* ( dets | pcs )*;
numbers : ( ( number | maybeNumber ) numberSep )* number ( numberSep ( number | maybeNumber ) )*;
signs : ( ( sign | maybeSign ) ( dot | colon ) )* sign ( ( dot | colon ) ( sign | maybeSign ) )*
      | decoratedX ( ( dot | colon ) decoratedX )*;



// Determinatives & Phonetic Complements

detp : det decoration;
dets : decoration det;
detc : decoration det decoration;
pcp : pc decoration;
pcs : decoration pc;
pcc : decoration pc decoration;

decoration : closeCondition? ( colon | slash )? openCondition?;

det : openCondition? '{' ( decoratedDetValue | sign | decoratedValue ) ( ( dot | colon ) ( decoratedDetValue | sign | decoratedValue ) )* '}' closeCondition?;
pc : openCondition? '<' ( sign | decoratedValue ) ( ( dash | colon ) ( sign | decoratedValue ) )* '>' closeCondition?;


// Signs

maybeSign : maybeSignL;
sign : decoratedSimpleSign
     | decoratedDots
     | signSum
     | openCondition? '|' signComplex '|' closeCondition? appendage?;
signComplex : ( ( signSum | maybeSignL ) dotOp )* signSum ( dotOp ( signSum | maybeSignL ) )*;
signSum : ( ( signProd | maybeSignL ) plus )* signProd ( plus ( signProd | maybeSignL ) )*;
signProd : decoratedSimpleSign
         | ( ( signFactor | maybeSignL ) ( times | above ) )* signFactor ( ( times | above ) ( signFactor | maybeSignL ) )+
         | ( ( signFactor | maybeSignL ) ( times | above ) )+ signFactor ( ( times | above ) ( signFactor | maybeSignL ) )*;
signFactor : decoratedSimpleSign
           | '(' signComplex ')';
maybeSignL : decoratedX 
           | decoratedNumberSign;


// Numbers

maybeNumber : numberX;
number : decoratedSimpleNumber
       | numberComplex;
numberComplex : ( ( numberProd | numberX ) plus )* numberProd ( plus ( numberProd | numberX ) )*;
numberProd : ( ( numberFactor | numberX ) ( times | div ) )* numberFactor ( ( times | div ) ( numberFactor | numberX ) )*;
numberFactor : decoratedSimpleNumber 
             | '(' number ')';
numberX : decoratedX 
        | decoratedDots;


// Characters

appendage : ( crit | comment )+ closeCondition?;

decoratedValue : openCondition? value closeCondition? appendage?;
decoratedCvalue : openCondition? cvalue closeCondition? appendage?;
decoratedDetValue : openCondition? detValue closeCondition? appendage?;
decoratedSimpleSign : openCondition? simpleSign closeCondition? appendage?;
decoratedNumberSign : openCondition? numberSign closeCondition? appendage?;
decoratedX : openCondition? x closeCondition? appendage?;
decoratedDots : openCondition? dots closeCondition? appendage?;
decoratedSimpleNumber : openCondition? simpleNumber closeCondition? appendage?;
decoratedVdivider : openCondition? vdivider closeCondition? ( ( crit+ | space? compoundComment ) closeCondition? )?;
decoratedHdivider : openCondition? hdivider closeCondition? ( ( crit+ | space? compoundComment ) closeCondition? )?;

value : ( valueT | descT ) variant? mod*;
cvalue : cvalueT variant? mod*;
detValue : dT | dualT;
simpleSign : ( signT | nnsignT )  variant? mod* | descT;
numberSign : numberT variant? mod*;
x : xT;
dots : dotsT;
simpleNumber : ( plusCrit? numberT | numberT plusCrit? );
vdivider : vdividerT;
hdivider : hdividerT;

// Separators

dash : '-' ( slash | nlT )?;
doubleDash : '--' ( slash | nlT )?;
dot : '.' ( slash | nlT )?;
colon : ':' ( slash | nlT )?;
spaceSep : space ( slash space | colon space )? 
         | nl;
nl : space? nlT space?;
numberSep : ('.'|','|';') ( slash | nlT )?;

// Operators

dotOp : '.';
plus : '+';
times : X | '×';
div : '/';
above : ABOVE;


// Conditions

openCondition : OCONDITION;
closeCondition : CCONDITION;


// Terminals

valueT : VALUE;
cvalueT : CVALUE | VOWELSIGN;
dT : D;
dualT : DUAL;
signT : SIGN | VOWELSIGN;
nnsignT : NNSIGN;
numberT : NUMBER | N;
xT : X;
numberXT : X;
dotsT : '…';
descT : DESC;
vdividerT : '=' | '–' |;
hdividerT : '|' | DOUBLEBAR;
space : ' '+ ;

mod : MOD;
crit : CRIT;
variant : VARIANT;
plusCrit : '+';
compoundComment : '(' ( subcomment | ~( '(' | ')' | '\n' ) )* ')';
comment : '(' ( subcomment | ~( '(' | ')' | '\n' ) )* ')';
subcomment : '(' ( subcomment | ~( '(' | ')' | '\n' ) )* ')';
meta : META;

nlT : '\n';
slash : '/';






