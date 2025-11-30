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
        # Token: KEYWORD(program) -> visit_KEYWORD(program) -> tapi dihandle khusus di bawah
        clean_name = node.name.replace('<', '').replace('>', '').replace('-', '_')
        
        # Hapus bagian value dalam kurung jika ada, misal IDENTIFIER(x) -> IDENTIFIER
        if '(' in clean_name:
            clean_name = clean_name.split('(')[0]

        method_name = 'visit_' + clean_name
        
        # Jika node adalah token leaf
        if method_name.startswith('visit_KEYWORD') or \
           method_name.startswith('visit_IDENTIFIER') or \
           method_name.startswith('visit_NUMBER') or \
           method_name.startswith('visit_STRING_LITERAL') or \
           method_name.startswith('visit_CHAR_LITERAL') or \
           method_name.startswith('visit_ASSIGN_OPERATOR') or \
           method_name.startswith('visit_ARITHMETIC_OPERATOR') or \
           method_name.startswith('visit_RELATIONAL_OPERATOR') or \
           method_name.startswith('visit_LOGICAL_OPERATOR'):
            return node # Kembalikan node token aslinya

        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        # Skip untuk token/node yang tidak perlu di-visit (misal SEMICOLON, COLON)
        return None

    # --- Program Structure ---

    def visit_program(self, node):
        # <program> -> <program-header> <declaration-part> <compound-statement> DOT
        header_node = node.children[0]
        # program-header -> KEYWORD IDENTIFIER SEMICOLON
        prog_name = header_node.children[1].value 
        
        declarations = self.visit(node.children[1]) # visit_declaration_part
        compound_stmt = self.visit(node.children[2]) # visit_compound_statement
        
        block = Block(declarations, compound_stmt)
        return Program(prog_name, block)

    def visit_declaration_part(self, node):
        declarations = []
        for child in node.children:
            result = self.visit(child)
            if result:
                if isinstance(result, list):
                    declarations.extend(result)
                else:
                    declarations.append(result)
        return declarations

    def _extract_type_info(self, type_node):
        """Helper untuk mengekstrak informasi tipe (termasuk array)."""
        first_child = type_node.children[0]
        
        # Tipe Dasar
        if first_child.name.startswith("KEYWORD") and first_child.value in ['integer', 'real', 'boolean', 'char']:
            return Type(first_child)
            
        # Tipe Array (Larik)
        elif first_child.name.startswith("KEYWORD") and first_child.value in ['larik', 'array']:
            range_node = type_node.children[2] # Node <range>
            
            # Ambil Node Expression dari Parse Tree
            # Struktur: <range> -> <expression> .. <expression>
            raw_low = range_node.children[0]
            raw_high = range_node.children[2]
            
            # Visit untuk mendapatkan Node AST (bisa Num, Var, BinOp, dll)
            low_ast = self.visit(raw_low)
            high_ast = self.visit(raw_high)
            
            # Rekursif untuk tipe elemen
            ele_type_node = type_node.children[5]
            ele_type_obj = self._extract_type_info(ele_type_node)
            
            type_obj = Type(first_child)
            
            # SIMPAN AST NODE, BUKAN NILAI INT
            type_obj.low_node = low_ast
            type_obj.high_node = high_ast
            
            type_obj.ele_type = ele_type_obj
            return type_obj
            
        # 3. Tipe Alias (Identifier)
        elif first_child.name.startswith("IDENTIFIER"):
            return Type(first_child)

        return Type(first_child)

    def visit_var_declaration(self, node):
        vars_list = []
        i = 1 
        while i < len(node.children):
            id_list_node = node.children[i]
            type_node = node.children[i+2] # Node <type>
            
            identifiers = [child for child in id_list_node.children if child.name.startswith("IDENTIFIER")]
            
            type_obj = self._extract_type_info(type_node)
            
            for var_token in identifiers:
                # copy type_obj agar setiap variabel punya instance sendiri
                import copy
                new_type = copy.copy(type_obj)
                vars_list.append(VarDecl(Var(var_token), new_type))
            
            i += 4 
        return vars_list
    
    def visit_const_declaration(self, node):
        # <const-declaration> -> KONSTANTA ( ID = VALUE ; )+
        consts_list = []
        i = 1 # Mulai dari index 1 (setelah token KONSTANTA)
        
        while i < len(node.children):
            id_node = node.children[i]      # Token IDENTIFIER
            val_node = node.children[i+2]   # Token VALUE (Number/String/Char)
            
            name = id_node.value
            raw_val = val_node.value
            
            # --- Logika Penentuan Tipe Konstanta ---
            type_code = 0
            val = raw_val
            
            if val_node.name.startswith("NUMBER"):
                if '.' in str(raw_val):
                    type_code = 2 # Real
                    val = float(raw_val)
                else:
                    type_code = 1 # Integer
                    val = int(raw_val)
            
            elif val_node.name.startswith("STRING_LITERAL"):
                # Cek apakah String atau Char
                s_val = str(raw_val).strip("'")
                if len(s_val) == 1:
                    type_code = 4 # Char
                else:
                    type_code = 5 # String
                val = s_val
            
            elif val_node.name.startswith("CHAR_LITERAL"):
                type_code = 4 # Char
                val = str(raw_val).strip("'")
            
            elif val_node.name.startswith("KEYWORD"):
                # Handle boolean literals (true/false)
                if raw_val.lower() == 'true':
                    type_code = 3 # Boolean
                    val = True
                elif raw_val.lower() == 'false':
                    type_code = 3 # Boolean
                    val = False
                    
            const_decl = ConstDecl(name, val, type_code)
            consts_list.append(const_decl)
            
            # Loncat 4 langkah: ID -> = -> VAL -> ; -> (Next ID)
            i += 4
            
        return consts_list
    
    def visit_type_declaration(self, node):
        types = []
        i = 1
        
        while i < len(node.children):
            id_node = node.children[i]        
            type_spec_node = node.children[i+2]
            
            name = id_node.value
            type_obj = self._extract_type_info(type_spec_node) 
            types.append(TypeDecl(name, type_obj))
            
            i += 4
            
        return types

    def visit_subprogram_declaration(self, node):
        child = node.children[0]
        if child.name == "<procedure-declaration>":
            return self.visit_procedure_declaration(child)
        elif child.name == "<function-declaration>":
            return self.visit_function_declaration(child) 

    def visit_procedure_declaration(self, node):
        proc_name = node.children[1].value
        params = []
        idx = 2
        if node.children[idx].name == "<formal-parameter-list>":
            params = self.visit(node.children[idx])
            idx += 1
        
        idx += 1 # SEMICOLON
        local_decls = self.visit(node.children[idx])
        body = self.visit(node.children[idx+1])
        block_node = Block(local_decls, body)
        
        return ProcedureDecl(proc_name, params, block_node)

    def visit_function_declaration(self, node):
        # <function-decl> -> FUNGSI ID (params) : TIPE ; BLOCK ;
        func_name = node.children[1].value
        
        idx = 2
        params = []
        if node.children[idx].name == "<formal-parameter-list>":
            params = self.visit(node.children[idx])
            idx += 1
        
        idx += 1 
        
        return_type_node = node.children[idx]
        return_type = self._extract_type_info(return_type_node) 
        
        idx += 2 
        
        local_decls = self.visit(node.children[idx])
        body = self.visit(node.children[idx+1])
        block_node = Block(local_decls, body)
        
        return FunctionDecl(func_name, params, return_type, block_node)

    def visit_formal_parameter_list(self, node):
        params = []
        for child in node.children:
            if child.name == "<parameter-group>":
                group_params = self.visit(child)
                params.extend(group_params)
        return params

    def visit_parameter_group(self, node):
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
        compound = Compound()
        for child in node.children:
            # --- PERBAIKAN UTAMA DI SINI ---
            # Jangan cek child.name == "<statement>" karena Parser tidak membungkusnya
            # Cukup abaikan SEMICOLON, sisanya adalah statement valid
            if child.name.startswith("SEMICOLON"):
                continue
            
            stmt = self.visit(child)
            if stmt:
                compound.children.append(stmt)
        return compound

    def visit_statement(self, node):
        # Jika ada node wrapper <statement>, ambil anaknya
        return self.visit(node.children[0])

    def visit_assignment_statement(self, node):
        left_node = node.children[0]
        var_node = Var(left_node)
        
        # Handle array access sederhana: ID [ expr ] := ...
        # Cek anak kedua, jika LBRACKET berarti array access
        op_idx = 1
        if node.children[1].name.startswith("LBRACKET"):
             # Logika array access (bisa dikembangkan)
             op_idx = 4 # ID [ EXPR ] := (index ke-4 adalah ASSIGN)
        
        op = node.children[op_idx] 
        right_node = self.visit(node.children[op_idx+1])
        
        return Assign(var_node, op, right_node)

    def visit_if_statement(self, node):
        condition = self.visit(node.children[1])
        then_branch = self.visit(node.children[3])
        else_branch = None
        if len(node.children) > 4:
            else_branch = self.visit(node.children[5])
        return If(condition, then_branch, else_branch)

    def visit_while_statement(self, node):
        condition = self.visit(node.children[1])
        body = self.visit(node.children[3])
        return While(condition, body)
        
    def visit_procedure_call(self, node):
        proc_name = node.children[0].value
        params = []
        if len(node.children) > 3: 
             params = self.visit(node.children[2])
        token = node.children[0] 
        return ProcedureCall(proc_name, params, token)

    def visit_parameter_list(self, node):
        params = []
        for child in node.children:
            if child.name == "<expression>":
                params.append(self.visit(child))
        return params

    def visit_for_statement(self, node):
        # UNTUK id := expr KE/TURUN_KE expr LAKUKAN stmt
        var_node = Var(node.children[1]) # ID
        start_expr = self.visit(node.children[3])
        direction = node.children[4].value # KE / TURUN_KE
        end_expr = self.visit(node.children[5])
        body = self.visit(node.children[7])
        
        return For(var_node, start_expr, direction, end_expr, body)

    # --- Expressions ---

    def visit_expression(self, node):
        left = self.visit(node.children[0])
        if len(node.children) > 1:
            op = node.children[1]
            right = self.visit(node.children[2])
            return BinOp(left, op, right)
        return left

    def visit_simple_expression(self, node):
        first_term_idx = 0
        # Cek unary operator (misal -5)
        if node.children[0].name.startswith("ARITHMETIC_OPERATOR"):
             # TODO: Implement UnaryOp Node jika perlu
             # Untuk sekarang kita anggap term mulai dari index 1
             # tapi logika parser mungkin berbeda.
             # Kita ambil term pertama dulu:
             if len(node.children) > 1:
                 first_term_idx = 1
        
        left = self.visit(node.children[first_term_idx])
        
        i = first_term_idx + 1
        while i < len(node.children):
            op = node.children[i]
            right = self.visit(node.children[i+1])
            left = BinOp(left, op, right)
            i += 2
        return left

    def visit_term(self, node):
        left = self.visit(node.children[0])
        i = 1
        while i < len(node.children):
            op = node.children[i]
            right = self.visit(node.children[i+1])
            left = BinOp(left, op, right)
            i += 2
        return left

    def visit_factor(self, node):
        child = node.children[0]
        name = child.name
        
        if name.startswith("NUMBER"):
            return Num(child)
        elif name.startswith("STRING_LITERAL"):
            return StringLiteral(child)
        elif name.startswith("CHAR_LITERAL"):
            return StringLiteral(child) # Treat char as string for now
        elif name.startswith("IDENTIFIER"):
            return Var(child)
        elif name.startswith("KEYWORD") and (child.value == 'true' or child.value == 'false'):
             # Boolean literal, bisa buat node khusus atau pakai Num/Var
             return Num(child) # Simplified
        elif name.startswith("LPARENTHESIS"):
            return self.visit(node.children[1]) # ( expr )
        elif name == "<function-call>":
            # Handle function call
            func_name = child.children[0].value
            params = []
            if len(child.children) > 3:
                params = self.visit(child.children[2])
            return FunctionCall(func_name, params, child.children[0])
            
        return None