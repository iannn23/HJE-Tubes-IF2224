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
        # Fallback: Jika node punya children, kunjungi children-nya
        if hasattr(node, 'children'):
            for child in node.children:
                self.visit(child)

    # --- Program & Blok ---
    def visit_Program(self, node):
        self.symtab.add_program_name(node.name)
        self.visit(node.block)

    def visit_Block(self, node):
        for decl in node.declarations:
            self.visit(decl)
        self.visit(node.compound_statement)

    def visit_VarDecl(self, node):
        type_name = node.type_node.value.lower()
        var_name = node.var_node.value
        
        # Mapping tipe ke kode (Sesuai SymbolTable: 1=int, 2=real, 3=bool, 4=char)
        type_code = 0
        if type_name == 'integer': type_code = 1
        elif type_name == 'real': type_code = 2
        elif type_name == 'boolean': type_code = 3
        elif type_name == 'char': type_code = 4
        
        # Cek duplikasi
        existing = self.symtab.lookup(var_name)
        if existing and existing['lev'] == self.symtab.level:
             print(f"Warning: Variabel '{var_name}' dideklarasikan ulang di scope yang sama.")

        idx = self.symtab.add_variable(var_name, type_code)
        
        # Simpan info ke node untuk keperluan printing Decorated AST
        if idx is not None:
            node.var_node.tab_entry = self.symtab.tab[idx]
            node.var_node.tab_entry['idx'] = idx

    def visit_ProcedureDecl(self, node):
        self.symtab.add_procedure(node.proc_name)
        self.symtab.enter_scope()
        for param in node.params:
            self.visit(param)
        self.visit(node.block_node)
        self.symtab.exit_scope()

    def visit_FunctionDecl(self, node):
        self.symtab.add_procedure(node.func_name) 
        self.symtab.enter_scope()
        for param in node.params:
            self.visit(param)
        self.visit(node.block_node)
        self.symtab.exit_scope()
    
    def visit_Compound(self, node):
        for child in node.children:
            self.visit(child)

    def visit_Assign(self, node):
        self.visit(node.left)  # Cek variabel kiri
        self.visit(node.right) # Cek ekspresi kanan
        
        left_type = node.left.sem_type
        right_type = node.right.sem_type
        
        # Validasi Tipe
        # Boleh: Int := Int (1=1), Real := Real (2=2), Bool := Bool (3=3)
        # Boleh: Real := Int (2=1) -> Implicit casting
        if left_type == right_type:
            pass
        elif left_type == 2 and right_type == 1:
            pass
        else:
            raise Exception(f"Semantic Error: Tidak bisa assign tipe {right_type} ke variabel bertipe {left_type} ('{node.left.value}')")
        
        node.sem_type = left_type

    def visit_If(self, node):
        # 1. Cek Kondisi
        self.visit(node.condition)
        if node.condition.sem_type != 3: # 3 = Boolean
            raise Exception(f"Semantic Error: Kondisi 'jika' harus boolean, ditemukan tipe {node.condition.sem_type}")
        
        # 2. Cek Body
        self.visit(node.then_branch)
        if node.else_branch:
            self.visit(node.else_branch)

    def visit_While(self, node):
        self.visit(node.condition)
        if node.condition.sem_type != 3: # 3 = Boolean
            raise Exception(f"Semantic Error: Kondisi 'selama' (while) harus boolean.")
        self.visit(node.body)

    def visit_For(self, node):
        self.visit(node.variable)
        self.visit(node.start_expr)
        self.visit(node.end_expr)
        
        # Pastikan variabel iterator integer
        if node.variable.sem_type != 1:
            raise Exception("Semantic Error: Variabel loop 'untuk' harus integer.")
            
        self.visit(node.body)

    def visit_ProcedureCall(self, node):
        # Cek apakah prosedur ada di tabel simbol
        proc_name = node.proc_name
        entry = self.symtab.lookup(proc_name)
        
        if not entry:
            # Cek apakah ini writeln (built-in)
            if proc_name.lower() == 'writeln':
                for param in node.actual_params:
                    self.visit(param)
                return
            else:
                raise Exception(f"Semantic Error: Prosedur '{proc_name}' tidak ditemukan.")
        
        if entry['obj'] != 'procedure':
             raise Exception(f"Semantic Error: '{proc_name}' bukan prosedur.")

        # Visit parameter aktual
        for param in node.actual_params:
            self.visit(param)

    def visit_BinOp(self, node):
        self.visit(node.left)
        self.visit(node.right)
        
        left_t = node.left.sem_type
        right_t = node.right.sem_type
        op = node.op.value.lower() # Ambil string operator dari node token

        # Aritmatika: +, -, *
        if op in ['+', '-', '*']:
            if left_t == 1 and right_t == 1:
                node.sem_type = 1 # Int op Int = Int
            elif left_t in [1, 2] and right_t in [1, 2]:
                node.sem_type = 2 # Salah satu Real = Real
            else:
                raise Exception(f"Semantic Error: Operator '{op}' butuh tipe numerik.")

        # Pembagian Real: /
        elif op == '/':
            if left_t in [1, 2] and right_t in [1, 2]:
                node.sem_type = 2 # Selalu Real
            else:
                raise Exception("Semantic Error: Pembagian '/' butuh tipe numerik.")

        # Pembagian Integer: div, mod
        elif op in ['div', 'mod', 'bagi']:
            if left_t == 1 and right_t == 1:
                node.sem_type = 1 # Integer only
            else:
                raise Exception(f"Semantic Error: Operator '{op}' hanya untuk integer.")

        # Relasional: <, >, =, <=, >=, <>
        elif op in ['=', '<>', '<', '<=', '>', '>=']:
            # Pastikan tipe sebanding (keduanya numerik atau keduanya sama)
            is_numeric = (left_t in [1, 2] and right_t in [1, 2])
            if is_numeric or (left_t == right_t):
                node.sem_type = 3 # Hasil selalu Boolean
            else:
                raise Exception(f"Semantic Error: Tidak bisa membandingkan tipe {left_t} dengan {right_t}")

        # Logika: and, or
        elif op in ['and', 'or', 'dan', 'atau']:
            if left_t == 3 and right_t == 3:
                node.sem_type = 3 # Boolean
            else:
                raise Exception(f"Semantic Error: Operator logika '{op}' butuh tipe boolean.")

    def visit_Var(self, node):
        var_name = node.value
        entry = self.symtab.lookup(var_name)
        
        if entry:
            node.sem_type = entry['type']
            node.tab_entry = entry # Tempel info tabel ke node (buat printer.py)
            node.tab_entry['idx'] = entry.get('idx', 0) # Pastikan ada idx
        else:
            raise Exception(f"Semantic Error: Variabel '{var_name}' belum dideklarasikan.")

    def visit_Num(self, node):
        # Cek apakah ada titik (.) di string value-nya
        if '.' in str(node.value):
            node.sem_type = 2 # Real
        else:
            node.sem_type = 1 # Integer

    def visit_StringLiteral(self, node):
        node.sem_type = 5 # Anggap 5 kode string (belum ada di spec, tapi buat aman)
    
    def visit_FunctionCall(self, node):
        # Mirip visit_Var tapi untuk fungsi
        func_name = node.func_name
        entry = self.symtab.lookup(func_name)
        
        if not entry:
             raise Exception(f"Semantic Error: Fungsi '{func_name}' tidak ditemukan.")
        
        # Fungsi harus punya tipe return (misal disimpan di 'type')
        node.sem_type = entry['type']
        
        for param in node.actual_params:
            self.visit(param)