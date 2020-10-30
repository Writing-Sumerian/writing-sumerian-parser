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
VALUE : LSYLL ( ']'? '['? LSYLL )* (PNUMBER | X)? ('⁺'+ | '⁻'+)?
      | '’';
CVALUE : CSYLL ( ']'? '['? LSYLL )* (PNUMBER | X)? ('⁺'+ | '⁻'+)?;
D : 'd';
MOD : '@' ( [tgšnkzcvabx] | '90' | '180' );
CRIT : [?!~*#];
ABOVE : '&' | '%';
OCONDITION : [[⸢‹«];
CCONDITION : [\]⸣›»];
SPACE : '   ';
BAR : ' | ';
OTHER : .;

text : ' '* openCondition? (vdivider nl)* section (nl (vdivider nl )+ section)* (nl vdivider)* closeCondition? ' '*  EOF
     | EOF;
section : hdivider? compound ( ( spaceSep | hdivider ) compound )* hdivider?;
compound : ( meta space )* word ( doubleDash word )* ( closeCondition? space comment )?;
//phrase : ( word | pn ( ( dash | colon ) pn )* ) ( space comment )?;
//phrase : ( word | pn ) ( ( dash | colon ) ( word | pn ) )* ( space comment )?;
word : ( prefix dash )? '⟨' stem '⟩' ( dash suffix )?
     | stem;
prefix : segment;
stem : segment;
suffix : segment;
segment : part ( ( dash | colon ) part )*;
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
pc : '<' openCondition? ( value | sign ) ( dash ( value | sign ) )* closeCondition? '>';


// Characters

appendage : ( conditionSuffix? ( crit | comment )+ )?;

value : ( valueT | descT ) mod* appendage;
cvalue : cvalueT mod* appendage;
d : dT appendage;
vdivider : vdividerT crit* ( ( conditionSuffix? space )? comment )?;

sign : simpleSign
     | x
     | dots
     | signSum
     | '|' signComplex '|' appendage;
signComplex : ( ( signSum | maybeSign ) dotOp )* signSum ( dotOp ( signSum | maybeSign ) )*;
signSum : ( ( signProd | maybeSign ) plus )* signProd ( plus ( signProd | maybeSign ) )*;
signProd : simpleSign
         | ( ( signFactor | maybeSign ) ( times | above ) )* signFactor ( ( times | above ) ( signFactor | maybeSign ) )+
         | ( ( signFactor | maybeSign ) ( times | above ) )+ signFactor ( ( times | above ) ( signFactor | maybeSign ) )*;
signFactor : simpleSign
           | '(' signComplex ')';
simpleSign : ( signT mod* | nnsignT  | descT ) appendage;
maybeSign : x 
          | numberT appendage;
x : xT appendage;
dots : dotsT appendage;

number : simpleNumber
       | numberComplex;
numberComplex : ( ( numberProd | numberX ) plus )* numberProd ( plus ( numberProd | numberX ) )*;
numberProd : ( ( numberFactor | numberX ) ( times | div ) )* numberFactor ( ( times | div ) ( numberFactor | numberX ) )*;
numberFactor : simpleNumber 
             | '(' number ')';
simpleNumber : ( plusCrit? numberT | numberT plusCrit? ) appendage;
numberX: numberXT appendage | dots;

numberXC: numberX;

// Separators

dash : closeCondition? '-' ( slash | nlT )? openCondition?;
doubleDash : closeCondition? '--' ( slash | nlT )? openCondition?;
dot : closeCondition? '.' ( slash | nlT )? openCondition?;
colon : closeCondition? ':' ( slash | nlT )? openCondition?;
spaceSep : closeCondition? ( space ( slash space | colon space | nlT space? )? | space? nlT space? ) openCondition?;
hdivider : closeCondition? ( spaceSep? hdividerT ( space? crit | comment )* spaceSep? ) openCondition?;
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
conditionSuffix : CCONDITION;


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
vdividerT: '=' | '–' |;
hdividerT: SPACE | BAR;
space : ' '+ ;

mod : MOD;
crit : CRIT;
plusCrit : '+';
comment : '(' ( comment | ~( '(' | ')' | '\n' ) )* ')';
meta : META;

nlT: '\n';
slash: '/';






