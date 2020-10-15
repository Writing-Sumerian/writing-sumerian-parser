grammar Cuneiform;


fragment LCON : [bdgĝhḫjklmnpqrřsšṣtṭwyz’];
fragment LVOWEL : [aeiu];
fragment UCON : [BDGĜHḪJKLMNPQRŘSŠṢTṬWYZ];
fragment UVOWEL : [AEIU];
fragment USYLL : ( UCON ']'? '['? )? UVOWEL ( ']'? '['? UCON )?;
fragment LSYLL : ( LCON ']'? '['? )? LVOWEL ( ']'? '['? LCON )?;
fragment CSYLL : UCON ']'? '['? LVOWEL ( ']'? '['? LCON )? | ( '’' ']'? '['? )? UVOWEL ( ']'? '['? LCON )?;
fragment PNUMBER : [1-9] [0-9]*;
fragment FRAC : [½⅓⅔¼¾⅕⅖⅗⅘⅙⅚⅐⅛⅜⅝⅞⅑⅒];

X : [Xx];
N : [Nn];

DESC : '"' ~["\n]* '"';
META : '_' ~[_\n]+ '_';
NUMBER : '0' | PNUMBER ( '/' PNUMBER | FRAC )? | FRAC;
VOWELSIGN : UVOWEL PNUMBER?;
SIGN : USYLL ( ']'? '['? USYLL )* PNUMBER?;
NNSIGN: ( 'LAK' | 'KWU' | 'REC' | 'RSP' | 'ZATU' ) PNUMBER [a-c]?;
VALUE : LSYLL ( ']'? '['? LSYLL )* (PNUMBER | X)? ('⁺'+ | '⁻'+)?;
CVALUE : CSYLL ( ']'? '['? LSYLL )* (PNUMBER | X)? ('⁺'+ | '⁻'+)?;
D : 'd';
MOD : '@' ( [tgšnkzcvabx] | '90' | '180' );
CRIT : [?!~*#];
ABOVE : '&' | '%';
OCONDITION : [[⸢‹«];
CCONDITION : [\]⸣›»];
OTHER : .;


text : ' '* openCondition? ( section | divider ) (nl ( section | divider ) )* closeCondition? ' '*  EOF
     | EOF;
section : ( meta space )? compound ( space ( compound | meta) )*;
compound : word;
//phrase : ( word | pn ( ( dash | colon ) pn )* ) ( space comment )?;
//phrase : ( word | pn ) ( ( dash | colon ) ( word | pn ) )* ( space comment )?;
word : part ( ( dash | colon ) part )*;
//pn : (detp | pcp)* ( cvalue | signs ) (dets | pcs)* ( ( dash | colon ) part)*;
part : ( detp | pcp )* ( value | cvalue | signs | numbers ) ( ( detc | pcc )+ ( value | cvalue | signs | numbers ) )* ( dets | pcs )*;
signs : ( ( sign | maybeSign ) ( dot | colon ) )* sign ( ( dot | colon ) ( sign | maybeSign ) )*;
numbers : ( ( number | numberXC ) numberSep )* number ( numberSep ( number | numberXC ) )*;


// Determinatives & Phonetic Complements

detp : det decoration;
dets : decoration det;
detc : decoration det decoration;
pcp : pc decoration;
pcs : decoration pc;
pcc : decoration pc decoration;

decoration : closeCondition? ( colon | slash | nl )? openCondition?;

det : '{' openCondition? ( d | sign | value ) ( dot ( d | sign | value ) )* closeCondition? '}';
pc : '<' openCondition? value ( dash value )* closeCondition? '>';


// Characters

value : ( valueT | descT ) mod* ( crit| comment )*;
cvalue : cvalueT mod* ( crit | comment )*;
d : dT ( crit | comment )*;
divider : dividerT ( crit | comment )*;

sign : simpleSign
     | x
     | dots
     | signSum
     | '|' signComplex '|' ( crit | comment )*;
signComplex : ( ( signSum | maybeSign ) dotOp )* signSum ( dotOp ( signSum | maybeSign ) )*;
signSum : ( ( signProd | maybeSign ) plus )* signProd ( plus ( signProd | maybeSign ) )*;
signProd : simpleSign
         | ( ( signFactor | maybeSign ) ( times | above ) )* signFactor ( ( times | above ) ( signFactor | maybeSign ) )+
         | ( ( signFactor | maybeSign ) ( times | above ) )+ signFactor ( ( times | above ) ( signFactor | maybeSign ) )*;
signFactor : simpleSign
           | '(' signComplex ')';
simpleSign : ( signT mod* | nnsignT  | descT ) ( crit | comment )*;
maybeSign : x 
          | numberT ( crit | comment )*;
x : xT ( crit | comment )*;
dots : dotsT ( crit | comment )*;

number : simpleNumber
       | numberComplex;
numberComplex : ( ( numberProd | numberX ) plus )* numberProd ( plus ( numberProd | numberX ) )*;
numberProd : ( ( numberFactor | numberX ) ( times | div ) )* numberFactor ( ( times | div ) ( numberFactor | numberX ) )*;
numberFactor : simpleNumber 
             | '(' number ')';
simpleNumber : ( plusCrit? numberT | numberT plusCrit? ) ( crit | comment )*;
numberX: numberXT ( crit | comment )* | dots;

numberXC: numberX;

// Separators

dash : closeCondition? '-' ( slash | nlT )? openCondition?;
dot : closeCondition? '.' ( slash | nlT )? openCondition?;
colon : closeCondition? ':' ( slash | nlT )? openCondition?;
space : closeCondition? ' '+ ( slash ' '+ )? openCondition?;
nl : closeCondition? ' '* nlT ' '* openCondition?;
numberSep : closeCondition? ('.'|','|';') ( slash | nlT )? openCondition?;

// Operators

dotOp : closeCondition? '.' openCondition?;
plus : closeCondition? '+' openCondition?;
times : closeCondition? ( X | '×' ) openCondition?;
div : closeCondition? '/' openCondition?;
above : closeCondition? ABOVE openCondition?;


// Conditions

openCondition : OCONDITION;
closeCondition : CCONDITION;


// Terminals

valueT : VALUE;
cvalueT : CVALUE | VOWELSIGN;
dT: D;
signT : SIGN | VOWELSIGN;
nnsignT : NNSIGN;
numberT : NUMBER | N;
xT: X;
numberXT: X;
dotsT: '…';
descT: DESC;
dividerT: '□' | '=' | '–' |;

mod : MOD;
crit : CRIT;
plusCrit : '+';
comment : '(' ( comment | ~( '(' | ')' | '\n' ) )* ')';
meta : META;

nlT: '\n';
slash: '/';






