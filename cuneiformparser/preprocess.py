import regex as re

def preprocess(text, f):
    parts = re.split(r'(?P<comment>\((?:[^\(\)]+|(?&comment))*\))|("[^"]*"|_[^_]*_)', text)
    res = ''
    for i, part in enumerate(parts):
        if part:
            res += f(part) if not i%3 else part
    return res