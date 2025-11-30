from .symbol_table import SymbolTable
from .ast_builder import ASTBuilder
from .ast_nodes import *

class SemanticAnalyzer:
    def __init__(self):
        self.symtab = SymbolTable()
        self.builder = ASTBuilder()

    def analyze(self, parse_tree_root):
        ast_root = self.builder.build(parse_tree_root)
        if ast_root:
            self.visit(ast_root)
        return ast_root, self.symtab

    def visit(self, node):
        if node is None: return None
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        # Fallback untuk node yang belum ada handler khusus
        pass

    # --- Program & Blok ---
    def visit_Program(self, node):
        self.symtab.add_program_name(node.name)
        self.visit(node.block)

    def visit_Block(self, node):
        for decl in node.declarations:
            self.visit(decl)
        self.visit(node.compound_statement)

    # --- Deklarasi ---
    def visit_VarDecl(self, node):
        var_name = node.var_node.value
        
        # Panggil helper rekursif
        type_code, ref_idx, size = self._resolve_type_info(node.type_node)

        # Cek Duplikasi
        existing = self.symtab.lookup(var_name)
        if existing and existing['lev'] == self.symtab.level:
             print(f"[SEMANTIC ERROR] Variable '{var_name}' redeclared.")

        # Masukkan ke Tabel
        idx = self.symtab.add_variable(var_name, type_code, ref=ref_idx, size=size)
        node.var_node.tab_entry = self.symtab.tab[idx]
        node.var_node.tab_entry['idx'] = idx 

    def visit_TypeDecl(self, node):
        type_name = node.name
        type_code, ref_idx, size = self._resolve_type_info(node.type_obj)

        existing = self.symtab.lookup(type_name)
        if existing and existing['lev'] == self.symtab.level:
            print(f"[SEMANTIC ERROR] Type '{type_name}' redeclared.")

        idx = self.symtab.add_type(type_name, type_code, ref=ref_idx)
        node.tab_entry = self.symtab.tab[idx]
        node.tab_entry['idx'] = idx

    def visit_ConstDecl(self, node):
        idx = self.symtab.add_constant(node.name, getattr(node, 'const_type', 0), node.value)
        if hasattr(node, 'tab_entry'):
             node.tab_entry = self.symtab.tab[idx]
             node.tab_entry['idx'] = idx

    def visit_FunctionDecl(self, node):
        # Resolve return type
        ret_code, _, _ = self._resolve_type_info(node.return_type)
        
        self.symtab.add_function(node.func_name, ret_code)
        self.symtab.enter_scope()
        for param in node.params:
            self.visit(param)
        self.visit(node.block_node)
        self.symtab.exit_scope()

    def visit_ProcedureDecl(self, node):
        self.symtab.add_procedure(node.proc_name)
        self.symtab.enter_scope()
        for param in node.params:
            self.visit(param)
        self.visit(node.block_node)
        self.symtab.exit_scope()

    # --- Statement ---
    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        # Visit Left (Target)
        self.visit(node.left)
        # Visit Right (Expression)
        self.visit(node.right)
        
        # Type Checking
        if node.left.sem_type != node.right.sem_type:
            # Sederhana: Anggap error/warning, tapi lanjut
            pass
        
        node.sem_type = node.left.sem_type

    def visit_ProcedureCall(self, node):
        # Cek prosedur
        pass

    # --- Ekspresi ---
    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        # Result type logic
        node.sem_type = node.left.sem_type

    def visit_Var(self, node):
        var_name = node.value
        entry = self.symtab.lookup(var_name)
        
        if entry:
            node.sem_type = entry['type']
            node.tab_entry = entry 
        else:
            raise Exception(f"Semantic Error: Variable '{var_name}' not declared.")

    def visit_Num(self, node):
        if '.' in str(node.value):
            node.sem_type = 2 # Real
        else:
            node.sem_type = 1 # Integer

    def visit_StringLiteral(self, node):
        node.sem_type = 5 # String

    # -- Helper ---
    def _evaluate_const_expr(self, node):
        """Mengevaluasi node AST menjadi nilai Python (int/float/bool/str)."""
        if isinstance(node, Num):
            # Cek apakah integer atau real
            if isinstance(node.value, float) or '.' in str(node.value):
                return float(node.value)
            return int(node.value)
            
        elif isinstance(node, Var):
            # Lookup konstanta di symbol table
            name = node.value
            entry = self.symtab.lookup(name)
            if entry and entry['obj'] == 'constant':
                return entry['adr'] # Nilai konstanta disimpan di adr
            else:
                print(f"[SEMANTIC ERROR] '{name}' is not a valid constant for array bounds.")
                return 0
                
        elif isinstance(node, UnaryOp):
            val = self._evaluate_const_expr(node.expr)
            if node.op.value == '-': return -val
            if node.op.value == '+': return val
            if node.op.value.lower() == 'not': return not val
            
        elif isinstance(node, BinOp):
            left = self._evaluate_const_expr(node.left)
            right = self._evaluate_const_expr(node.right)
            op = node.op.value
            
            if op == '+': return left + right
            elif op == '-': return left - right
            elif op == '*': return left * right
            elif op == 'div': return int(left / right)
            
        return 0 # Fallback

    def _resolve_type_info(self, type_obj):
        type_name = type_obj.value.lower()
        
        if type_name in ['integer', 'real', 'boolean', 'char']:
            return {"integer":1, "real":2, "boolean":3, "char":4}[type_name], 0, 1
        
        elif type_name in ['larik', 'array']:
            ele_type_obj = type_obj.ele_type
            etyp, eref, elsz = self._resolve_type_info(ele_type_obj)
            
            low_val = self._evaluate_const_expr(type_obj.low_node)
            high_val = self._evaluate_const_expr(type_obj.high_node)
            
            type_obj.low = low_val
            type_obj.high = high_val
            
            ref_idx = self.symtab.add_array_entry(
                xtyp=1, etyp=etyp, eref=eref,
                low=low_val, high=high_val, elsz=elsz
            )
            
            size = (high_val - low_val + 1) * elsz
            return 5, ref_idx, size
            
        else:
            entry = self.symtab.lookup(type_name)
            if entry and entry['obj'] == 'type':
                return entry['type'], entry['ref'], 1 
            return 0, 0, 1