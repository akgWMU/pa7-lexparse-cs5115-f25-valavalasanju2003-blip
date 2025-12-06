# lexer.py
import sys
import os

# Attempt to import PLY. If not available in the current interpreter, try
# to locate a local virtualenv at `.venv` and add its site-packages to
# `sys.path` so the module can be loaded when the user forgets to activate
# the venv. If that still fails, print actionable instructions and exit.
try:
    import ply.lex as lex
except ModuleNotFoundError:
    # try to find .venv site-packages (common layout: .venv/lib/pythonX.Y/site-packages)
    venv_root = os.path.join(os.path.dirname(__file__), '.venv')
    if os.path.isdir(venv_root):
        lib_dir = os.path.join(venv_root, 'lib')
        if os.path.isdir(lib_dir):
            for entry in os.listdir(lib_dir):
                if entry.startswith('python'):
                    candidate = os.path.join(lib_dir, entry, 'site-packages')
                    if os.path.isdir(candidate):
                        sys.path.insert(0, candidate)
                        break
    try:
        import ply.lex as lex
    except ModuleNotFoundError:
        print("Error: required package 'ply' is not installed for this Python.")
        print("Fix options:")
        print("  1) Activate the project's venv and run the script:")
        print("       cd /Users/sanjuvalavala/Desktop/lexer && source .venv/bin/activate && python lexer.py")
        print("  2) Or run using the venv python without activating:")
        print("       /Users/sanjuvalavala/Desktop/lexer/.venv/bin/python lexer.py")
        print("  3) Or install ply into your active Python:\n       pip install ply")
        sys.exit(1)

# -------------------------
# Reserved keywords
# -------------------------
reserved = {
    'PROGRAM': 'PROGRAM',
    'VAR': 'VAR',
    'ARRAY': 'ARRAY',
    'OF': 'OF',
    'INTEGER': 'INTEGER',
    'FLOAT': 'FLOAT',
    'IF': 'IF',
    'THEN': 'THEN',
    'ELSE': 'ELSE',
    'WHILE': 'WHILE',
    'DO': 'DO',
    'BEGIN': 'BEGIN',
    'END': 'END',
    'READ': 'READ',
    'WRITE': 'WRITE',
    'AND': 'AND',
    'OR': 'OR',
    'NOT': 'NOT',
}

# -------------------------
# Token list
# -------------------------
tokens = [
    # identifiers and constants
    'ID',
    'INTNUM',
    'FLOATNUM',
    'STRINGCONST',

    # arithmetic operators
    'PLUS', 'MINUS', 'TIMES', 'DIVIDE',

    # relational operators
    'RELOP',

    # assignment
    'ASSIGN',        # :=

    # separators / punctuation
    'LPAREN', 'RPAREN',
    'LBRACKET', 'RBRACKET',
    'DOT', 'COMMA', 'SEMI', 'COLON', 'DOTDOT',
] + list(reserved.values())

# -------------------------
# Simple token regexes
# -------------------------
t_PLUS      = r'\+'
t_MINUS     = r'-'
t_TIMES     = r'\*'
t_DIVIDE    = r'/'

# <=, >=, <>, <, >, =
t_RELOP     = r'<=|>=|<>|<|>|='

t_ASSIGN    = r':='

t_LPAREN    = r'\('
t_RPAREN    = r'\)'

t_LBRACKET  = r'\['
t_RBRACKET  = r'\]'

t_DOTDOT    = r'\.\.'
t_DOT       = r'\.'
t_COMMA     = r','
t_SEMI      = r';'
t_COLON     = r':'

# Ignore spaces, tabs, and carriage returns
t_ignore = ' \t\r'

# -------------------------
# Comments { ... }
# -------------------------
def t_COMMENT(t):
    r'\{[^}]*\}'
    # Count newlines inside comments
    t.lexer.lineno += t.value.count('\n')
    # Comments are ignored by the parser
    pass

# -------------------------
# Numbers
# -------------------------
# Float with optional exponent, must contain a dot
def t_FLOATNUM(t):
    r'(\d+\.\d*|\d*\.\d+)([eE][+-]?\d+)?'
    t.value = float(t.value)
    return t

# Integer
def t_INTNUM(t):
    r'\d+'
    t.value = int(t.value)
    return t

# -------------------------
# String constants  'LETTER*'
# -------------------------
def t_STRINGCONST(t):
    r"'[A-Za-z]*'"
    t.value = t.value[1:-1]      # strip quotes
    return t

# -------------------------
# Identifiers / Keywords
# -------------------------
def t_ID(t):
    r'[A-Za-z][A-Za-z0-9]*'
    t.type = reserved.get(t.value, 'ID')  # reserved or ID
    return t

# -------------------------
# Newlines
# -------------------------
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# -------------------------
# Error handling
# -------------------------
def t_error(t):
    print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
    t.lexer.skip(1)

# -------------------------
# Build lexer
# -------------------------
lexer = lex.lex()

if __name__ == '__main__':
    import sys, json

    data = sys.stdin.read()
    lexer.input(data)

    token_strings = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        token_strings.append(f"{tok.type}:{tok.value}")

    print(json.dumps({"type": "token_list", "tokens": token_strings}))
