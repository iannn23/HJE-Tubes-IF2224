from .ast_nodes import *

class ASTBuilder:
    """
    Mengubah Parse Tree (dari Parser) menjadi Abstract Syntax Tree (AST).
    """
    
    def build(self, parse_tree_root):
        if parse_tree_root is None:
            return None
        return self.visit(parse_tree_root)

    def visit(self, node):
        """Dispatch method: memanggil fungsi visit yang sesuai berdasarkan nama node."""
        if node is None:
            return None
        
        # Bersihkan nama node dari < > untuk jadi nama method
        # Contoh: <program> -> visit_program
        # Contoh: <if-statement> -> visit_if_statement
        method_name = 'visit_' + node.name.replace('<', '').replace('>', '').replace('-', '_')
        
        # Jika node adalah token leaf (seperti KEYWORD, IDENTIFIER, dll)
        if method_name.startswith('visit_KEYWORD') or \
           method_name.startswith('visit_IDENTIFIER') or \
           method_name.startswith('visit_NUMBER') or \
           method_name.startswith('visit_STRING_LITERAL') or \
           method_name.startswith('visit_CHAR_LITERAL'):
            return node # Kembalikan node token aslinya (objek Node dari parser)

        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"No visit_{node.name} method")

    # --- Program Structure ---

    def visit_program(self, node):
        # <program> -> <program-header> <declaration-part> <compound-statement> DOT
        header_node = node.children[0]
        prog_name = header_node.children[1].value # Ambil value dari IDENTIFIER
        
        declarations = self.visit(node.children[1]) # visit_declaration_part
        compound_stmt = self.visit(node.children[2]) # visit_compound_statement
        
        block = Block(declarations, compound_stmt)
        return Program(prog_name, block)

    def visit_declaration_part(self, node):
        # <declaration-part> -> kumpulan deklarasi
        declarations = []
        for child in node.children:
            # Child bisa berupa <var-declaration>, <subprogram-declaration>, dll.
            # Hasil visit bisa berupa single object atau list of objects
            result = self.visit(child)
            if result:
                if isinstance(result, list):
                    declarations.extend(result)
                else:
                    declarations.append(result)
        return declarations

    def visit_var_declaration(self, node):
        # <var-declaration> -> KEYWORD(variabel) <identifier-list> COLON <type> SEMICOLON ...
        # Note: Satu baris "a, b: integer;" akan menghasilkan 2 objek VarDecl
        vars_list = []
        
        # Karena struktur di parser bisa berulang (identifier list, colon, type, semicolon)
        # Kita perlu iterasi children
        i = 1 # Skip KEYWORD(variabel)
        while i < len(node.children):
            id_list_node = node.children[i] # <identifier-list>
            type_node = node.children[i+2]  # <type> (skip COLON)
            
            # Ambil semua nama identifier
            identifiers = []
            for child in id_list_node.children:
                if child.name.startswith("IDENTIFIER"):
                    identifiers.append(child)
            
            # Ambil tipe data
            # <type> -> KEYWORD(integer) atau lainnya
            # Kita ambil token KEYWORD-nya
            type_token = type_node.children[0] 
            
            for var_token in identifiers:
                # Bungkus token tipe ke dalam objek Type AST
                type_obj = Type(type_token)
                # Bungkus variabel ke VarDecl
                vars_list.append(VarDecl(Var(var_token), type_obj))
            
            i += 4 # Lompat ke grup deklarasi berikutnya (jika ada)
            
        return vars_list

    def visit_subprogram_declaration(self, node):
        # <subprogram-declaration> -> <procedure-declaration> | <function-declaration>
        return self.visit(node.children[0])

    def visit_procedure_declaration(self, node):
        # KEYWORD(prosedur) ID [params] SEMI block SEMI
        proc_name = node.children[1].value
        
        params = []
        idx = 2
        # Cek jika ada parameter
        if node.children[idx].name == "<formal-parameter-list>":
            params = self.visit(node.children[idx])
            idx += 1
            
        idx += 1 # Skip SEMICOLON
        
        # Deklarasi lokal dan body ada di children berikutnya
        # Namun struktur parser.py memisahkan declaration_part dan compound_statement
        # Kita gabungkan jadi Block
        local_decls = self.visit(node.children[idx])
        body = self.visit(node.children[idx+1])
        block_node = Block(local_decls, body)
        
        return ProcedureDecl(proc_name, params, block_node)

    def visit_formal_parameter_list(self, node):
        # Mengembalikan list of VarDecl
        params = []
        for child in node.children:
            if child.name == "<parameter-group>":
                group_params = self.visit(child)
                params.extend(group_params)
        return params

    def visit_parameter_group(self, node):
        # Mirip var_declaration tapi untuk parameter
        id_list = node.children[0]
        type_node = node.children[2]
        type_token = type_node.children[0]
        
        identifiers = [child for child in id_list.children if child.name.startswith("IDENTIFIER")]
        
        group = []
        for token in identifiers:
            type_obj = Type(type_token)
            group.append(VarDecl(Var(token), type_obj))
        return group

    # --- Statements ---

    def visit_compound_statement(self, node):
        # <compound-statement> -> MULAI <statement-list> SELESAI
        stmt_list_node = node.children[1]
        return self.visit(stmt_list_node)

    def visit_statement_list(self, node):
        # Mengembalikan objek Compound (list of statements)
        compound = Compound()
        for child in node.children:
            if child.name == "<statement>":
                stmt = self.visit(child)
                if stmt:
                    compound.children.append(stmt)
        return compound

    def visit_statement(self, node):
        # <statement> hanya membungkus statement spesifik
        return self.visit(node.children[0])

    def visit_assignment_statement(self, node):
        # ID := Expression
        left_node = node.children[0] # IDENTIFIER
        var_node = Var(left_node)
        
        # Cek array access (belum diimplementasi di sini untuk penyederhanaan, bisa ditambahkan)
        
        op = node.children[1] # ASSIGN_OPERATOR
        right_node = self.visit(node.children[2]) # <expression>
        
        return Assign(var_node, op, right_node)

    def visit_if_statement(self, node):
        # JIKA expr MAKA stmt [SELAIN_ITU stmt]
        condition = self.visit(node.children[1])
        then_branch = self.visit(node.children[3])
        else_branch = None
        
        if len(node.children) > 4:
            # Ada ELSE
            else_branch = self.visit(node.children[5])
            
        return If(condition, then_branch, else_branch)

    def visit_while_statement(self, node):
        # SELAMA expr LAKUKAN stmt
        condition = self.visit(node.children[1])
        body = self.visit(node.children[3])
        return While(condition, body)
        
    def visit_procedure_call(self, node):
        # ID ( [params] )
        proc_name = node.children[0].value
        params = []
        if len(node.children) > 3: # Ada parameter list
             params = self.visit(node.children[2]) # visit parameter_list
        
        # Token digunakan untuk tracking baris error nanti
        token = node.children[0] 
        return ProcedureCall(proc_name, params, token)

    def visit_parameter_list(self, node):
        # Mengembalikan list of expressions
        params = []
        for child in node.children:
            if child.name == "<expression>":
                params.append(self.visit(child))
        return params

    # --- Expressions ---

    def visit_expression(self, node):
        # <expression> -> simple_expr [REL_OP simple_expr]
        left = self.visit(node.children[0])
        
        if len(node.children) > 1:
            op = node.children[1] # RELATIONAL_OPERATOR
            right = self.visit(node.children[2])
            return BinOp(left, op, right)
        
        return left

    def visit_simple_expression(self, node):
        # <simple-expression> -> term (ADD_OP term)*
        # Perlu menangani urutan operasi (flattening) atau chaining
        # Untuk sederhananya kita asumsi struktur pohon biner kiri ke kanan
        
        # Cek unary operator di depan (opsional)
        first_term_idx = 0
        # Logika unary bisa ditambahkan di sini jika ada di Parse Tree
        
        left = self.visit(node.children[first_term_idx])
        
        # Loop untuk sisa operation: op term op term...
        i = first_term_idx + 1
        while i < len(node.children):
            op = node.children[i]
            right = self.visit(node.children[i+1])
            left = BinOp(left, op, right) # Build tree up
            i += 2
            
        return left

    def visit_term(self, node):
        # <term> -> factor (MUL_OP factor)*
        left = self.visit(node.children[0])
        
        i = 1
        while i < len(node.children):
            op = node.children[i]
            right = self.visit(node.children[i+1])
            left = BinOp(left, op, right)
            i += 2
            
        return left

    def visit_factor(self, node):
        # <factor> -> ID | NUMBER | ( expr ) | ...
        child = node.children[0]
        
        if child.name.startswith("NUMBER"):
            return Num(child)
        elif child.name.startswith("STRING_LITERAL"):
            return StringLiteral(child)
        elif child.name.startswith("IDENTIFIER"):
            return Var(child)
        elif child.name.startswith("LPARENTHESIS"):
            # ( expression ) -> index 1 adalah expression
            return self.visit(node.children[1])
        elif child.name == "<function-call>":
            # Belum dihandle penuh, anggap Var dulu atau implementasi FunctionCall
            return Var(child.children[0]) # Simplified
            
        return None