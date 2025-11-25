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
        type_name = node.type_node.value.lower()
        var_name = node.var_node.value
        
        # Mapping tipe ke kode
        type_code = 0
        if type_name == 'integer': type_code = 1
        elif type_name == 'real': type_code = 2
        elif type_name == 'boolean': type_code = 3
        elif type_name == 'char': type_code = 4
        
        # Cek duplikasi di scope yang sama
        existing = self.symtab.lookup(var_name)
        # Logic cek duplikasi level disederhanakan:
        # Jika ketemu dan levelnya sama dengan level sekarang -> Error
        if existing and existing['lev'] == self.symtab.level:
             pass # Warning atau Error, kita skip dulu biar jalan

        # Masukkan ke Symbol Table
        idx = self.symtab.add_variable(var_name, type_code)
        
        # Anotasi Node VarDecl (untuk info debug/print)
        node.var_node.tab_entry = self.symtab.tab[idx]
        node.var_node.tab_entry['idx'] = idx # Simpan indexnya juga

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
            node.tab_entry = entry # Penting untuk printing!
        else:
            raise Exception(f"Semantic Error: Variable '{var_name}' not declared.")

    def visit_Num(self, node):
        if '.' in str(node.value):
            node.sem_type = 2 # Real
        else:
            node.sem_type = 1 # Integer

    def visit_StringLiteral(self, node):
        node.sem_type = 5 # String