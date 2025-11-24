class AST:
    """Base class untuk semua node AST."""
    def __init__(self):
        # Atribut untuk menyimpan hasil analisis semantik nanti
        self.sem_type = None   # Menyimpan tipe data (misal: 'integer')
        self.sem_scope = None  # Menyimpan level scope node ini

# --- Struktur Program ---
class Program(AST):
    def __init__(self, name, block):
        super().__init__()
        self.name = name
        self.block = block

class Block(AST):
    def __init__(self, declarations, compound_statement):
        super().__init__()
        self.declarations = declarations
        self.compound_statement = compound_statement

# --- Deklarasi ---
class VarDecl(AST):
    def __init__(self, var_node, type_node):
        super().__init__()
        self.var_node = var_node
        self.type_node = type_node

class Type(AST):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.value = token.value  # misal: 'integer', 'real'

class ProcedureDecl(AST):
    def __init__(self, proc_name, params, block_node):
        super().__init__()
        self.proc_name = proc_name
        self.params = params      # List of VarDecl (parameter)
        self.block_node = block_node

class FunctionDecl(AST):
    def __init__(self, func_name, params, return_type, block_node):
        super().__init__()
        self.func_name = func_name
        self.params = params
        self.return_type = return_type
        self.block_node = block_node

# --- Statement ---
class Compound(AST):
    """Representasi blok BEGIN ... END"""
    def __init__(self):
        super().__init__()
        self.children = []

class Assign(AST):
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left          # Variabel target (Var)
        self.token = self.op = op # Token :=
        self.right = right        # Ekspresi nilai

class If(AST):
    def __init__(self, condition, then_branch, else_branch):
        super().__init__()
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class While(AST):
    def __init__(self, condition, body):
        super().__init__()
        self.condition = condition
        self.body = body

class For(AST):
    def __init__(self, variable, start_expr, direction, end_expr, body):
        super().__init__()
        self.variable = variable
        self.start_expr = start_expr
        self.direction = direction # 'to' atau 'downto'
        self.end_expr = end_expr
        self.body = body

class ProcedureCall(AST):
    def __init__(self, proc_name, actual_params, token):
        super().__init__()
        self.proc_name = proc_name
        self.actual_params = actual_params # List ekspresi argumen
        self.token = token
        self.proc_symbol = None # Akan diisi referensi ke Symbol Table

class NoOp(AST):
    """Statement kosong"""
    pass

# --- Ekspresi ---
class BinOp(AST):
    def __init__(self, left, op, right):
        super().__init__()
        self.left = left
        self.token = self.op = op
        self.right = right

class UnaryOp(AST):
    def __init__(self, op, expr):
        super().__init__()
        self.token = self.op = op
        self.expr = expr

class Num(AST):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.value = token.value

class StringLiteral(AST):
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.value = token.value

class Var(AST):
    """Representasi penggunaan variabel dalam ekspresi"""
    def __init__(self, token):
        super().__init__()
        self.token = token
        self.value = token.value
        # Akan diisi saat semantic analysis (referensi ke entri di symbol table)
        self.tab_entry = None 

class FunctionCall(AST):
    def __init__(self, func_name, actual_params, token):
        super().__init__()
        self.func_name = func_name
        self.actual_params = actual_params
        self.token = token
        self.func_symbol = None