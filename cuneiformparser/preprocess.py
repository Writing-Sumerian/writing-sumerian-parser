import re

def preprocess(text, f):
    parts = re.split(r'([\(\)]|"[^"]*"|_[^_]*_)', text)
    res = ''
    level = 0
    for i, part in enumerate(parts):
        if part:
            if i%2:
                res += part
                if part == '(':
                    level += 1
                elif part == ')':
                    level -= 1
            else:
                res += f(part) if not level else part
    return res