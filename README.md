
## Syntax

### Critical Symbols
The following critical symbols may be attached to any sign or number:
* `?` uncertain
* `!` corrected
* `*` collated
* `~` variant

### Sign Modifiers
Sign modifiers may be attached to the end of a sign. The following modifiers are used:
* `@g` *gunû*
* `@t` *tenû*
* `@š` *šeššig*
* `@n` *nutillû*
* `@k` *kaba-tenû*
* `@z` *zida-tenû*
* `@i` *inversum* (rotated 180°)
* `@c` written with a round stylus (may also denote a conventional variant, see below)
* `@a`, `@b`, `@c`, `@x` conventional (`a`, `b`, `c`) or new (`x`) variant of a sign

### Simplified and Augmented Sign Forms
Simplified or augmented sign forms, as introduced by Mittermeyer & Attinger in aBZL, are denoted by `⁻` (U+207B) and `⁺` (U+207A) respectively.

### Sign Conditions
Sign conditions are denoted using different types of brackets. Four types of conditions are distinguished:
* lost: `[]`
* damaged: `⸢⸣` (U+2E22 and U+2E23). Alternatively, a hash character (`#`) may be attached to a sign to denote that it is damaged.
* inserted: `‹›` (single guillemets, U+2039 and U+203A)
* deleted: `«»` (guillemets, U+00AB and U+00BB)

Square brackets may be placed inside a sign to denote that only part of it is lost. This information is not retained during parsing and the respective sign is simply marked as damaged.

### Puctuation
Punctuation structures a cuneiform text. 
There are two types of vertical dividers, which need to be placed on a line of their own:
* vertical space: `=`. This character can be left out as an empty line is interpreted as a dividing space.
* horizontal line: `–` (U+2013)

There are two types of horizontal dividers, which need to be seperated from the rest of the text by spaces:
* horizontal space: `||`
* vertical line: `|`

Comments and critical symbols may be added to punctuation.

> Example:  
> `Gu-ga-ga | gi-gu`

### Complex Signs
A complex sign may be wrapped in `|` characters. This is obligatory if the sign contains one or more dots, as these are otherwise interpreted as separators.

The following operators may be used to describe complex signs:
* juxtaposition: `.`
* ligature: `+`
* the second sign written in or over the first: `×` (U+00D7, preferred) or `x` (lower case letter x)
* the second sign written above the first: `&`
* grouping: `(` and `)` (may only be used before or after `×`, `x` or `&`)

### Separators
Two signs in the same line are separated by
* a space if the are in different compounds
* a double dash `--` if they are in different words
* a dot `.` if they are either both unread, both numbers, or both determinatives to the same sign
* a single dash `-` in all other cases except 
