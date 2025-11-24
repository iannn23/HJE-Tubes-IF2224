from .symbol_table import SymbolTable
from .ast_builder import ASTBuilder
from .ast_nodes import *

class SemanticAnalyzer:
    """
    Melakukan analisis semantik:
    1. Membangun AST dari Parse Tree.
    2. Mengisi Symbol Table (Scope Checking).
    3. Memeriksa kesesuaian tipe data (Type Checking).
    """
    def __init__(self):
        self.symtab = SymbolTable()
        self.builder = ASTBuilder()

    def analyze(self, parse_tree_root):
        """
        Fungsi utama yang dipanggil oleh compiler.
        Mengembalikan: (Decorated AST, Symbol Table)
        """
        # 1. Konversi Parse Tree -> AST
        ast_root = self.builder.build(parse_tree_root)
        
        # 2. Jalankan analisis semantik (Traversal AST)
        if ast_root:
            self.visit(ast_root)
            
        return ast_root, self.symtab

    def visit(self, node):
        """
        Pattern Visitor: Memanggil method visit_NamaKelasNode yang sesuai.
        """
        if node is None:
            return None
        
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{type(node).__name__} method")

    # --- Program & Blok ---

    def visit_Program(self, node):
        print(f"Analisis Semantik Program: {node.name}")
        self.visit(node.block)

    def visit_Block(self, node):
        # 1. Proses Deklarasi (masukkan ke Symbol Table)
        for decl in node.declarations:
            self.visit(decl)
        
        # 2. Proses Compound Statement (Body)
        self.visit(node.compound_statement)

    # --- Deklarasi ---

    def visit_VarDecl(self, node):
        type_name = node.type_node.value.lower()
        var_name = node.var_node.value
        
        # Mapping nama tipe ke kode tipe (sesuai spesifikasi/symbol table)
        type_code = 0
        if type_name == 'integer': type_code = 1
        elif type_name == 'real': type_code = 2
        elif type_name == 'boolean': type_code = 3
        elif type_name == 'char': type_code = 4
        else:
            # Tipe lain (array/record) bisa ditambahkan logikanya di sini
            type_code = 5 # Placeholder untuk tipe kompleks
        
        # Cek apakah variabel sudah ada di scope INI (duplikasi)
        existing = self.symtab.lookup(var_name)
        if existing and existing['lev'] == self.symtab.level:
            raise Exception(f"Semantic Error: Variabel '{var_name}' sudah dideklarasikan di scope ini.")

        # Masukkan ke Symbol Table
        self.symtab.add_variable(var_name, type_code)

    def visit_ProcedureDecl(self, node):
        proc_name = node.proc_name
        # Masukkan nama prosedur ke scope saat ini (agar bisa dipanggil)
        # (Untuk penyederhanaan, kita anggap prosedur tipe void/0)
        self.symtab.add_variable(proc_name, 0) 
        
        # Masuk Scope Baru
        self.symtab.enter_scope()
        
        # Proses Parameter (masukkan sebagai variabel lokal)
        for param in node.params:
            self.visit(param)
            
        # Proses Blok Prosedur
        self.visit(node.block_node)
        
        # Keluar Scope
        self.symtab.exit_scope()

    def visit_FunctionDecl(self, node):
        func_name = node.func_name
        # Masukkan nama fungsi ke scope saat ini
        # (Perlu mapping return type ke kode, disederhanakan dulu)
        self.symtab.add_variable(func_name, 0) 
        
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
        var_name = node.left.value
        
        # 1. Cek apakah variabel target sudah dideklarasikan?
        sym_entry = self.symtab.lookup(var_name)
        if not sym_entry:
            raise Exception(f"Semantic Error: Variabel '{var_name}' belum dideklarasikan.")
        
        # 2. Evaluasi nilai kanan (expression)
        self.visit(node.right)
        
        # 3. Cek Kesesuaian Tipe (Type Checking)
        # Integer (1) hanya bisa diisi Integer (1)
        if sym_entry['type'] != node.right.sem_type:
            raise Exception(f"Type Mismatch: Tidak bisa mengisi variabel '{var_name}' (Tipe {sym_entry['type']}) dengan nilai bertipe {node.right.sem_type}")
            
        node.sem_type = sym_entry['type']

    def visit_If(self, node):
        self.visit(node.condition)
        # Pastikan kondisi bertipe boolean (3)
        if node.condition.sem_type != 3: 
             pass # Warning: Harusnya raise error jika strict pascal, tapi kita skip dulu utk demo
             
        self.visit(node.then_branch)
        if node.else_branch:
            self.visit(node.else_branch)

    def visit_While(self, node):
        self.visit(node.condition)
        self.visit(node.body)

    def visit_For(self, node):
        # Cek variabel counter
        var_name = node.variable.value
        if not self.symtab.lookup(var_name):
            raise Exception(f"Semantic Error: Variabel loop '{var_name}' belum dideklarasikan.")
            
        self.visit(node.start_expr)
        self.visit(node.end_expr)
        self.visit(node.body)

    def visit_ProcedureCall(self, node):
        proc_name = node.proc_name
        entry = self.symtab.lookup(proc_name)
        if not entry:
             # Predefined procedure seperti 'writeln' mungkin tidak ada di tabel manual kita
             if proc_name.lower() not in ['writeln', 'write', 'readln', 'read']:
                 raise Exception(f"Semantic Error: Prosedur '{proc_name}' tidak dikenal.")
        
        for param in node.actual_params:
            self.visit(param)

    def visit_NoOp(self, node):
        pass

    # --- Ekspresi ---

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        
        # Type Checking Sederhana
        # Jika Int op Int -> Int
        if node.left.sem_type == node.right.sem_type:
            node.sem_type = node.left.sem_type
        else:
            # Fallback: Jika beda tipe (misal Int + Real), result Real (2)
            # Atau raise error jika strict
            node.sem_type = 2 # Asumsi promote ke Real/Error
            
        # Khusus operator relasional (>, <, =), hasilnya selalu Boolean (3)
        if node.op.value in ['>', '<', '=', '>=', '<=', '<>']:
            node.sem_type = 3 

    def visit_Var(self, node):
        var_name = node.value
        sym_entry = self.symtab.lookup(var_name)
        
        if not sym_entry:
            raise Exception(f"Semantic Error: Variabel '{var_name}' digunakan tapi belum dideklarasikan.")
            
        node.sem_type = sym_entry['type'] # Ambil tipe dari tabel simbol
        node.tab_entry = sym_entry        # Link node AST ke tabel simbol

    def visit_Num(self, node):
        # Cek apakah integer atau real
        if '.' in str(node.value):
            node.sem_type = 2 # Real
        else:
            node.sem_type = 1 # Integer

    def visit_StringLiteral(self, node):
        node.sem_type = 5 # Kode dummy untuk String (atau Char Array)