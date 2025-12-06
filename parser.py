# parser.py
import sys
from collections import deque
import os

# Attempt to import PLY. If not available in the current interpreter, try
# to locate a local virtualenv at `.venv` and add its site-packages to
# `sys.path` so the module can be loaded when the user forgets to activate
# the venv. If that still fails, print actionable instructions and exit.
try:
    import ply.yacc as yacc
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
        import ply.yacc as yacc
    except ModuleNotFoundError:
        print("Error: required package 'ply' is not installed for this Python.")
        print("Fix options:")
        print("  1) Activate the project's venv and run the script:")
        print("       cd /Users/sanjuvalavala/Desktop/lexer && source .venv/bin/activate && python parser.py input.sml")
        print("  2) Or run using the venv python without activating:")
        print("       /Users/sanjuvalavala/Desktop/lexer/.venv/bin/python parser.py input.sml")
        print("  3) Or install ply into your active Python:\n       pip install ply")
        sys.exit(1)

from lexer import tokens, lexer


# =========================
# AST NODE CLASSES
# =========================

class Node:
    def __init__(self):
        self.type = None   # type for semantic analysis (later if needed)


class Program(Node):
    def __init__(self, name, decls, compound_stmt):
        super().__init__()
        self.name = name
        self.decls = decls or []
        self.compound_stmt = compound_stmt

    def __str__(self):
        return f"Program({self.name})"


class VarDecl(Node):
    """Represents: x, y : INTEGER;  or  a, b : ARRAY[...] OF FLOAT;"""

    def __init__(self, names, type_node):
        super().__init__()
        self.names = names          # list of strings
        self.type_node = type_node  # StandardType or ArrayType

    def __str__(self):
        return "VarDecl(" + ",".join(self.names) + ")"


class StandardType(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name  # 'INTEGER' or 'FLOAT'

    def __str__(self):
        return f"StandardType({self.name})"


class ArrayType(Node):
    def __init__(self, lower, upper, base_type):
        super().__init__()
        self.lower = lower          # int
        self.upper = upper          # int
        self.base_type = base_type  # StandardType

    def __str__(self):
        return f"ArrayType({self.lower}..{self.upper})"


class CompoundStatement(Node):
    def __init__(self, statements):
        super().__init__()
        self.statements = statements or []

    def __str__(self):
        return "Compound"


class Assign(Node):
    def __init__(self, var, expr):
        super().__init__()
        self.var = var        # Variable node
        self.expr = expr      # Expr node

    def __str__(self):
        return "Assign"


class IfStatement(Node):
    def __init__(self, cond, then_stmt, else_stmt=None):
        super().__init__()
        self.cond = cond
        self.then_stmt = then_stmt
        self.else_stmt = else_stmt

    def __str__(self):
        return "If"


class WhileStatement(Node):
    def __init__(self, cond, body):
        super().__init__()
        self.cond = cond
        self.body = body

    def __str__(self):
        return "While"


class Read(Node):
    def __init__(self, var):
        super().__init__()
        self.var = var

    def __str__(self):
        return "Read"


class Write(Node):
    def __init__(self, expr, is_string=False):
        super().__init__()
        self.expr = expr      # Expr or StringConst
        self.is_string = is_string

    def __str__(self):
        return "WriteStr" if self.is_string else "Write"


class BinOp(Node):
    def __init__(self, op, left, right):
        super().__init__()
        self.op = op          # '+', '-', '*', '/', 'AND', 'OR', '<', '>', etc.
        self.left = left
        self.right = right

    def __str__(self):
        return f"BinOp({self.op})"


class UnaryOp(Node):
    def __init__(self, op, operand):
        super().__init__()
        self.op = op          # 'NOT'
        self.operand = operand

    def __str__(self):
        return f"UnaryOp({self.op})"


class Var(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return f"Var({self.name})"


class ArrayRef(Node):
    def __init__(self, name, index_expr):
        super().__init__()
        self.name = name
        self.index_expr = index_expr

    def __str__(self):
        return f"ArrayRef({self.name})"


class IntConst(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return f"IntConst({self.value})"


class FloatConst(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return f"FloatConst({self.value})"


class StringConst(Node):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __str__(self):
        return f"StringConst('{self.value}')"


# =========================
# TYPE SYSTEM
# =========================

class Type:
    pass


class IntType(Type):
    def __str__(self):
        return "INTEGER"


class FloatType(Type):
    def __str__(self):
        return "FLOAT"


class ArrayTypeT(Type):
    def __init__(self, lower, upper, base_type):
        self.lower = lower
        self.upper = upper
        self.base_type = base_type  # IntType or FloatType

    def __str__(self):
        return f"ARRAY[{self.lower}..{self.upper}] OF {self.base_type}"


# =========================
# SYMBOL TABLE
# =========================

class Symbol:
    def __init__(self, name, type_obj):
        self.name = name
        self.type = type_obj

    def __str__(self):
        return f"{self.name} : {self.type}"


class SymbolTable:
    def __init__(self):
        self.table = {}

    def insert(self, name, type_obj):
        if name in self.table:
            raise Exception(f"Duplicate declaration of '{name}'")
        self.table[name] = Symbol(name, type_obj)

    def lookup(self, name):
        return self.table.get(name, None)

    def __str__(self):
        return "\n".join(str(sym) for sym in self.table.values())


# =========================
# SEMANTIC ANALYSIS
# =========================

class TypeError(Exception):
    pass


class TypeChecker:
    def __init__(self, symtab):
        self.symtab = symtab

    def error(self, msg):
        raise TypeError(msg)

    # -------------- main entry --------------
    def check_program(self, program: Program):
        # Declarations
        for decl in program.decls:
            self.check_vardecl(decl)
        # Body
        self.check_statement(program.compound_stmt)

    # -------------- declarations --------------
    def check_vardecl(self, decl: VarDecl):
        t = self.resolve_type(decl.type_node)
        for name in decl.names:
            self.symtab.insert(name, t)

    def resolve_type(self, tnode):
        if isinstance(tnode, StandardType):
            if tnode.name == 'INTEGER':
                return IntType()
            elif tnode.name == 'FLOAT':
                return FloatType()
            else:
                self.error(f"Unknown standard type {tnode.name}")
        elif isinstance(tnode, ArrayType):
            base = self.resolve_type(tnode.base_type)
            return ArrayTypeT(tnode.lower, tnode.upper, base)
        else:
            self.error(f"Unknown type node {tnode}")

    # -------------- statements --------------
    def check_statement(self, stmt):
        if isinstance(stmt, CompoundStatement):
            for s in stmt.statements:
                self.check_statement(s)

        elif isinstance(stmt, Assign):
            self.check_assign(stmt)

        elif isinstance(stmt, IfStatement):
            self.check_if(stmt)

        elif isinstance(stmt, WhileStatement):
            self.check_while(stmt)

        elif isinstance(stmt, Read):
            self.check_variable(stmt.var)

        elif isinstance(stmt, Write):
            if stmt.is_string:
                # ok, type not needed
                pass
            else:
                self.check_expr(stmt.expr)

    def check_assign(self, node: Assign):
        var_type = self.check_variable(node.var)
        expr_type = self.check_expr(node.expr)

        if isinstance(var_type, IntType) and isinstance(expr_type, FloatType):
            node.type = var_type
        elif isinstance(var_type, FloatType) and isinstance(expr_type, IntType):
            node.type = var_type
        elif type(var_type) is type(expr_type):
            node.type = var_type
        else:
            self.error(f"Incompatible assignment: {var_type} := {expr_type}")

    def check_if(self, node: IfStatement):
        cond_type = self.check_expr(node.cond)
        if not isinstance(cond_type, (IntType, FloatType)):
            self.error("IF condition must be numeric")
        self.check_statement(node.then_stmt)
        if node.else_stmt:
            self.check_statement(node.else_stmt)

    def check_while(self, node: WhileStatement):
        cond_type = self.check_expr(node.cond)
        if not isinstance(cond_type, (IntType, FloatType)):
            self.error("WHILE condition must be numeric")
        self.check_statement(node.body)

    # -------------- variables --------------
    def check_variable(self, v):
        if isinstance(v, Var):
            sym = self.symtab.lookup(v.name)
            if sym is None:
                self.error(f"Undeclared identifier '{v.name}'")
            v.type = sym.type
            return v.type

        elif isinstance(v, ArrayRef):
            sym = self.symtab.lookup(v.name)
            if sym is None:
                self.error(f"Undeclared array '{v.name}'")
            if not isinstance(sym.type, ArrayTypeT):
                self.error(f"'{v.name}' is not an array")
            index_type = self.check_expr(v.index_expr)
            if not isinstance(index_type, IntType):
                self.error("Array index must be INTEGER")
            v.type = sym.type.base_type
            return v.type

    # -------------- expressions --------------
    def check_expr(self, e):
        if isinstance(e, IntConst):
            e.type = IntType()
            return e.type
        elif isinstance(e, FloatConst):
            e.type = FloatType()
            return e.type
        elif isinstance(e, (Var, ArrayRef)):
            return self.check_variable(e)
        elif isinstance(e, BinOp):
            return self.check_binop(e)
        elif isinstance(e, UnaryOp):
            return self.check_unaryop(e)
        else:
            return None

    def check_binop(self, node: BinOp):
        left_t = self.check_expr(node.left)
        right_t = self.check_expr(node.right)
        op = node.op

        # logical ops
        if op in ('AND', 'OR'):
            node.type = IntType()
            return node.type

        # relational ops
        if op in ('<', '<=', '>=', '>', '=', '<>'):
            node.type = IntType()
            return node.type

        # arithmetic ops
        if op in ('+', '-', '*', '/'):
            if isinstance(left_t, FloatType) or isinstance(right_t, FloatType):
                node.type = FloatType()
            else:
                node.type = IntType()
            return node.type

        self.error(f"Unknown binary operator {op}")

    def check_unaryop(self, node: UnaryOp):
        if node.op == 'NOT':
            t = self.check_expr(node.operand)
            if not isinstance(t, IntType):
                self.error("NOT operand must be INTEGER")
            node.type = IntType()
        else:
            # could handle unary minus here if you extend grammar
            t = self.check_expr(node.operand)
            node.type = t
        return node.type


# =========================
# GRAMMAR RULES (PLY)
# =========================

start = 'program'


def p_program(p):
    """program : PROGRAM ID SEMI decls compound_statement DOT"""
    p[0] = Program(p[2], p[4], p[5])


def p_decls(p):
    """decls : VAR decl_list
             | empty"""
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = []


def p_decl_list(p):
    """decl_list : decl_list identifier_list COLON type SEMI
                 | identifier_list COLON type SEMI"""
    if len(p) == 6:
        p[0] = p[1] + [VarDecl(p[2], p[4])]
    else:
        p[0] = [VarDecl(p[1], p[3])]


def p_identifier_list(p):
    """identifier_list : ID
                       | identifier_list COMMA ID"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_type(p):
    """type : standard_type
            | array_type"""
    p[0] = p[1]


def p_standard_type(p):
    """standard_type : INTEGER
                     | FLOAT"""
    p[0] = StandardType(p[1])


def p_array_type(p):
    """array_type : ARRAY LBRACKET dim RBRACKET OF standard_type"""
    lower, upper = p[3]
    p[0] = ArrayType(lower, upper, p[6])


def p_dim(p):
    """dim : INTNUM DOTDOT INTNUM"""
    p[0] = (p[1], p[3])


def p_statement(p):
    """statement : assignment
                 | if_statement
                 | while_statement
                 | io_statement
                 | compound_statement"""
    p[0] = p[1]


def p_assignment(p):
    """assignment : variable ASSIGN expr"""
    p[0] = Assign(p[1], p[3])


def p_if_statement(p):
    """if_statement : IF expr THEN statement ELSE statement
                    | IF expr THEN statement"""
    if len(p) == 7:
        p[0] = IfStatement(p[2], p[4], p[6])
    else:
        p[0] = IfStatement(p[2], p[4])


def p_while_statement(p):
    """while_statement : WHILE expr DO statement"""
    p[0] = WhileStatement(p[2], p[4])


def p_io_statement(p):
    """io_statement : READ LPAREN variable RPAREN
                    | WRITE LPAREN expr RPAREN
                    | WRITE LPAREN STRINGCONST RPAREN"""
    if p[1] == 'READ':
        p[0] = Read(p[3])
    else:  # WRITE
        if isinstance(p[3], str):
            p[0] = Write(StringConst(p[3]), is_string=True)
        else:
            p[0] = Write(p[3])


def p_compound_statement(p):
    """compound_statement : BEGIN statement_list END"""
    p[0] = CompoundStatement(p[2])


def p_statement_list(p):
    """statement_list : statement
                      | statement_list SEMI statement"""
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[3]]


def p_expr(p):
    """expr : expr logop relexpr
            | relexpr"""
    if len(p) == 4:
        p[0] = BinOp(p[2], p[1], p[3])
    else:
        p[0] = p[1]


def p_logop(p):
    """logop : OR
             | AND"""
    p[0] = p[1]


def p_relexpr(p):
    """relexpr : relexpr relop addexpr
               | addexpr"""
    if len(p) == 4:
        p[0] = BinOp(p[2], p[1], p[3])
    else:
        p[0] = p[1]


def p_relop(p):
    """relop : RELOP"""
    p[0] = p[1]


def p_addexpr(p):
    """addexpr : addexpr addop mulexpr
               | mulexpr"""
    if len(p) == 4:
        p[0] = BinOp(p[2], p[1], p[3])
    else:
        p[0] = p[1]


def p_addop(p):
    """addop : PLUS
             | MINUS"""
    p[0] = p[1]


def p_mulexpr(p):
    """mulexpr : mulexpr mulop factor
               | factor"""
    if len(p) == 4:
        p[0] = BinOp(p[2], p[1], p[3])
    else:
        p[0] = p[1]


def p_mulop(p):
    """mulop : TIMES
             | DIVIDE"""
    p[0] = p[1]


def p_factor(p):
    """factor : variable
              | constant
              | NOT factor
              | LPAREN expr RPAREN"""
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = UnaryOp('NOT', p[2])
    else:
        p[0] = p[2]


def p_variable(p):
    """variable : ID
                | ID LBRACKET expr RBRACKET"""
    if len(p) == 2:
        p[0] = Var(p[1])
    else:
        p[0] = ArrayRef(p[1], p[3])


def p_constant(p):
    """constant : INTNUM
                | FLOATNUM"""
    if isinstance(p[1], int):
        p[0] = IntConst(p[1])
    else:
        p[0] = FloatConst(p[1])


def p_empty(p):
    """empty :"""
    p[0] = None


def p_error(tok):
    if tok:
        print(f"Syntax error at '{tok.value}' (type {tok.type})")
    else:
        print("Syntax error at EOF")


parser = yacc.yacc()


# =========================
# LEVEL-ORDER (BFS) PRINT
# =========================

def level_order_print(root: Node):
    """Print tree level by level:
       - nodes in a level separated by ' # '
       - levels separated by TWO blank lines
    """
    if root is None:
        return

    q = deque()
    q.append((root, 0))
    current_level = 0
    level_nodes = []

    while q:
        node, lvl = q.popleft()

        if lvl != current_level:
            print(" # ".join(str(n) for n in level_nodes))
            print()
            print()
            level_nodes = []
            current_level = lvl

        level_nodes.append(node)

        # Enqueue children
        if isinstance(node, Program):
            for d in node.decls:
                q.append((d, lvl + 1))
            q.append((node.compound_stmt, lvl + 1))

        elif isinstance(node, VarDecl):
            q.append((node.type_node, lvl + 1))
            for name in node.names:
                q.append((Var(name), lvl + 1))

        elif isinstance(node, ArrayType):
            q.append((IntConst(node.lower), lvl + 1))
            q.append((IntConst(node.upper), lvl + 1))
            q.append((node.base_type, lvl + 1))

        elif isinstance(node, CompoundStatement):
            for s in node.statements:
                q.append((s, lvl + 1))

        elif isinstance(node, Assign):
            q.append((node.var, lvl + 1))
            q.append((node.expr, lvl + 1))

        elif isinstance(node, IfStatement):
            q.append((node.cond, lvl + 1))
            q.append((node.then_stmt, lvl + 1))
            if node.else_stmt is not None:
                q.append((node.else_stmt, lvl + 1))

        elif isinstance(node, WhileStatement):
            q.append((node.cond, lvl + 1))
            q.append((node.body, lvl + 1))

        elif isinstance(node, Read):
            q.append((node.var, lvl + 1))

        elif isinstance(node, Write):
            q.append((node.expr, lvl + 1))

        elif isinstance(node, BinOp):
            q.append((node.left, lvl + 1))
            q.append((node.right, lvl + 1))

        elif isinstance(node, UnaryOp):
            q.append((node.operand, lvl + 1))

        elif isinstance(node, (Var, ArrayRef, IntConst, FloatConst, StringConst, StandardType)):
            pass

    if level_nodes:
        print(" # ".join(str(n) for n in level_nodes))
        print()
        print()


# =========================
# MAIN / DRIVER
# =========================

def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            source = f.read()
    else:
        # Sample program
        source = """PROGRAM Sample;
VAR x, y : INTEGER;
    a : ARRAY [1 .. 10] OF FLOAT;
BEGIN
    x := 1;
    y := x + 2.5;
    IF x < y THEN
        WRITE('ok')
    ELSE
        WRITE(0);
    WHILE x < y DO
        x := x + 1
END.
"""

    ast = parser.parse(source, lexer=lexer)

    if ast is None:
        print("Parsing failed.")
        return

    symtab = SymbolTable()
    checker = TypeChecker(symtab)

    try:
        checker.check_program(ast)
        print("=== Symbol Table ===")
        print(symtab)
    except TypeError as e:
        print("Type error:", e)

    print("\n=== Level-order traversal of AST ===")
    level_order_print(ast)



if __name__ == '__main__':
    main()
