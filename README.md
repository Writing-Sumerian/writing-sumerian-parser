# The Writing Sumerian Parser

Parse cuneiform transliterations to Writing Sumerian compatible tables.

## Building

Requires [antlr4](https://github.com/antlr/antlr4).

```bash
cd cuneiformparser/grammar
antlr4 -Dlanguage=Python3 Cuneiform.g4
cd ../..
python3 -m build
```