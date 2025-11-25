# src/parser.py

class Node:
    """
    Kelas untuk merepresentasikan sebuah node dalam Parse Tree.
    """
    def __init__(self, name, value=None):
        self.name = name
        self.value = value
        self.children = []

    def add_child(self, node):
        self.children.append(node)

    def __repr__(self, level=0):
        ret = "\t" * level + f"{self.name}"
        if self.value:
            ret += f"({self.value})"
        ret += "\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret
    
    def print_tree(self, prefix="", is_last=True, is_root=True):
        if is_root:
            print(self.name)
            new_prefix = ""
        else:
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{self.name}")
            
            new_prefix = prefix + ("    " if is_last else "│   ")

        child_count = len(self.children)
        for i, child in enumerate(self.children):
            is_last_child = (i == child_count - 1)
            child.print_tree(new_prefix, is_last_child, is_root=False)

class Parser:
    """
    Melakukan syntax analysis menggunakan metode Recursive Descent.
    """
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_index = 0
        self.current_token = self.tokens[self.token_index] if self.tokens else None

    def advance(self):
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = None

    def expect(self, token_type, value=None):
        token = self.current_token
        if token and token.type == token_type and (value is None or token.value.lower() == value.lower()):
            self.advance()
            node_name = f"{token.type}({token.value})"
            return Node(node_name,value=token.value)
        
        expected_val = f" dengan nilai '{value}'" if value else ""
        current_val = f"'{self.current_token.value}' ({self.current_token.type})" if self.current_token else "None"
        raise SyntaxError(
            f"Error Sintaks: Diharapkan token {token_type}{expected_val}, tetapi ditemukan {current_val} pada posisi {self.token_index}."
        )

    def peek(self, token_type, value=None):
        return self.current_token and self.current_token.type == token_type and \
               (value is None or self.current_token.value.lower() == value.lower())

    def parse(self):
        if not self.current_token:
            return None
        return self.program()

    # --- ATURAN PRODUKSI UTAMA ---

    def program(self):
        node = Node("<program>")
        node.add_child(self.program_header())
        node.add_child(self.declaration_part())
        node.add_child(self.compound_statement())
        node.add_child(self.expect("DOT", "."))
        print("Parsing Selesai!")
        return node

    def program_header(self):
        node = Node("<program-header>")
        node.add_child(self.expect("KEYWORD", "program")) 
        node.add_child(self.expect("IDENTIFIER"))
        node.add_child(self.expect("SEMICOLON", ";"))
        return node

    def declaration_part(self):
        node = Node("<declaration-part>")
        while self.peek("KEYWORD", "variabel") or \
              self.peek("KEYWORD", "konstanta") or \
              self.peek("KEYWORD", "tipe") or \
              self.peek("KEYWORD", "prosedur") or \
              self.peek("KEYWORD", "fungsi"):
            
            if self.peek("KEYWORD", "variabel"):
                node.add_child(self.var_declaration())
            if self.peek("KEYWORD", "konstanta"):
                node.add_child(self.const_declaration())
            if self.peek("KEYWORD", "tipe"):
                node.add_child(self.type_declaration())
            if self.peek("KEYWORD", "prosedur") or self.peek("KEYWORD", "fungsi"):
                node.add_child(self.subprogram_declaration())
        return node

    def compound_statement(self):
        node = Node("<compound-statement>")
        node.add_child(self.expect("KEYWORD", "mulai"))
        node.add_child(self.statement_list())
        node.add_child(self.expect("KEYWORD", "selesai"))
        return node

    # --- ATURAN PRODUKSI DEKLARASI ---

    def var_declaration(self):
        node = Node("<var-declaration>")
        node.add_child(self.expect("KEYWORD", "variabel"))
        while self.peek("IDENTIFIER"):
            node.add_child(self.identifier_list())
            node.add_child(self.expect("COLON", ":"))
            node.add_child(self.type_spec())
            node.add_child(self.expect("SEMICOLON", ";"))
        return node
    
    def const_declaration(self):
        node = Node("<const-declaration>")
        node.add_child(self.expect("KEYWORD", "konstanta"))
        while self.peek("IDENTIFIER"):
            node.add_child(self.expect("IDENTIFIER"))
            node.add_child(self.expect("RELATIONAL_OPERATOR", "="))
            node.add_child(self.expect("NUMBER"))
            node.add_child(self.expect("SEMICOLON", ";"))
        return node
    
    def type_declaration(self):
        node = Node("<type-declaration>")
        node.add_child(self.expect("KEYWORD", "tipe"))
        while self.peek("IDENTIFIER"):
            node.add_child(self.expect("IDENTIFIER"))
            node.add_child(self.expect("RELATIONAL_OPERATOR", "="))
            node.add_child(self.type_spec())
            node.add_child(self.expect("SEMICOLON", ";"))
        return node
    
    def subprogram_declaration(self):
        node = Node("<subprogram-declaration>")
        while self.peek("KEYWORD", "prosedur") or self.peek("KEYWORD", "fungsi"):
            if self.peek("KEYWORD", "prosedur"):
                node.add_child(self.procedure_declaration())
            elif self.peek("KEYWORD", "fungsi"):
                node.add_child(self.function_declaration())
        return node
    
    def procedure_declaration(self):
        node = Node("<procedure-declaration>")
        node.add_child(self.expect("KEYWORD", "prosedur"))
        node.add_child(self.expect("IDENTIFIER"))
        
        if self.peek("LPARENTHESIS", "("):
            node.add_child(self.formal_parameter_list())
        
        node.add_child(self.expect("SEMICOLON", ";"))
        node.add_child(self.declaration_part())
        node.add_child(self.compound_statement())
        node.add_child(self.expect("SEMICOLON", ";"))
        return node
    
    def function_declaration(self):
        node = Node("<function-declaration>")
        node.add_child(self.expect("KEYWORD", "fungsi"))
        node.add_child(self.expect("IDENTIFIER"))
        
        if self.peek("LPARENTHESIS", "("):
            node.add_child(self.formal_parameter_list())
        
        node.add_child(self.expect("COLON", ":"))
        node.add_child(self.type_spec())
        node.add_child(self.expect("SEMICOLON", ";"))
        node.add_child(self.declaration_part())
        node.add_child(self.compound_statement())
        node.add_child(self.expect("SEMICOLON", ";"))
        return node

    def formal_parameter_list(self):
        node = Node("<formal-parameter-list>")
        node.add_child(self.expect("LPARENTHESIS", "("))
        node.add_child(self.parameter_group())
        while self.peek("SEMICOLON", ";"):
            node.add_child(self.expect("SEMICOLON", ";"))
            node.add_child(self.parameter_group())
        node.add_child(self.expect("RPARENTHESIS", ")"))
        return node
    
    def parameter_group(self):
        node = Node("<parameter-group>")
        node.add_child(self.identifier_list())
        node.add_child(self.expect("COLON", ":"))
        node.add_child(self.type_spec())
        return node

    def identifier_list(self):
        node = Node("<identifier-list>")
        node.add_child(self.expect("IDENTIFIER"))
        while self.peek("COMMA"):
            node.add_child(self.expect("COMMA", ","))
            node.add_child(self.expect("IDENTIFIER"))
        return node

    def type_spec(self):
        node = Node("<type>")
        if self.peek("KEYWORD", "integer"):
            node.add_child(self.expect("KEYWORD", "integer"))
        elif self.peek("KEYWORD", "real"):
            node.add_child(self.expect("KEYWORD", "real"))
        elif self.peek("KEYWORD", "boolean"):
            node.add_child(self.expect("KEYWORD", "boolean"))
        elif self.peek("KEYWORD", "char"):
            node.add_child(self.expect("KEYWORD", "char"))
        elif self.peek("KEYWORD", "larik"):
            node.add_child(self.expect("KEYWORD", "larik"))
            node.add_child(self.expect("LBRACKET", "["))
            node.add_child(self.range_spec())
            node.add_child(self.expect("RBRACKET", "]"))
            node.add_child(self.expect("KEYWORD", "dari"))
            node.add_child(self.type_spec())
        else:
            expr_node = self.expression() 
            
            if self.peek("RANGE_OPERATOR", ".."):
                subrange_node = Node("<subrange-type>")
                subrange_node.add_child(expr_node)
                subrange_node.add_child(self.expect("RANGE_OPERATOR", "..")) 
                subrange_node.add_child(self.expression()) # Ambil expression kedua
                node.add_child(subrange_node)
            else:
                node.add_child(expr_node) 
        return node
    
    def range_spec(self):
        node = Node("<range>")
        node.add_child(self.expression())
        node.add_child(self.expect("RANGE_OPERATOR", ".."))
        node.add_child(self.expression())
        return node

    # --- ATURAN PRODUKSI STATEMENT ---

    def statement_list(self):
        node = Node("<statement-list>")
        node.add_child(self.statement())
        while self.peek("SEMICOLON"):
            node.add_child(self.expect("SEMICOLON", ";"))
            if not self.peek("KEYWORD", "selesai"):
                 node.add_child(self.statement())
            else:
                break
        return node

    def statement(self):
            # 1. Cek Compound Statement (Blok mulai ... selesai)
            if self.peek("KEYWORD", "mulai"):
                return self.compound_statement()
                
            # 2. Cek If Statement (Percabangan)
            elif self.peek("KEYWORD", "jika"):
                return self.if_statement()
                
            # 3. Cek While Statement (Perulangan)
            elif self.peek("KEYWORD", "selama"):
                return self.while_statement()
                
            # 4. Cek For Statement (Perulangan Counter)
            elif self.peek("KEYWORD", "untuk"):
                return self.for_statement()
                
            # 5. Cek Identifier (Bisa Assignment ATAU Procedure Call)
            elif self.peek("IDENTIFIER"):
                next_token_idx = self.token_index + 1
                
                is_assignment = False
                if next_token_idx < len(self.tokens):
                    next_type = self.tokens[next_token_idx].type
                    # Assignment ditandai dengan ':=' ATAU '[' (untuk array)
                    if next_type == "ASSIGN_OPERATOR" or next_type == "LBRACKET":
                        is_assignment = True
                
                if is_assignment:
                    return self.assignment_statement()
                else:
                    return self.procedure_call()
                    
            # 6. Handle Empty Statement (titik koma berlebih)
            elif self.peek("SEMICOLON"):
                return Node("<empty-statement>")
                
            else:
                raise SyntaxError(f"Error Sintaks: Diharapkan statement, ditemukan '{self.current_token.value}'")

    def assignment_statement(self):
        # Grammar: ID [ '[' expression ']' ] := expression
        node = Node("<assignment-statement>")
        
        # 1. Nama Variabel
        node.add_child(self.expect("IDENTIFIER"))
        
        # 2. Cek apakah ini akses Array? (Opsional)
        if self.peek("LBRACKET", "["):
             node.add_child(self.expect("LBRACKET", "["))
             node.add_child(self.expression()) # Indeks
             node.add_child(self.expect("RBRACKET", "]"))
        
        # 3. Operator Assignment
        node.add_child(self.expect("ASSIGN_OPERATOR", ":="))
        
        # 4. Nilai Baru
        node.add_child(self.expression())
        
        return node

    # ATURAN PRODUKSI EKSPRESI

    def expression(self):
        """
        Aturan produksi: <expression> -> <simple-expression> [ <relational-operator> <simple-expression> ]
        Saat ini hanya mengimplementasikan bagian pertama.
        """
        node = Node("<expression>")
        node.add_child(self.simple_expression())
        # Cek Operator Relasional
        if self.current_token and self.current_token.type == "RELATIONAL_OPERATOR":
            node.add_child(self.expect("RELATIONAL_OPERATOR"))
            node.add_child(self.simple_expression())

        return node

    def simple_expression(self):
        """
        Aturan produksi: <simple-expression> -> <term> ( <additive-operator> <term> )*
        """
        node = Node("<simple-expression>")

        # Handle unary operator (+/-) di depan angka (misal: -5)
        if self.peek("ARITHMETIC_OPERATOR", "+") or self.peek("ARITHMETIC_OPERATOR", "-"):
             node.add_child(self.expect("ARITHMETIC_OPERATOR"))

        node.add_child(self.term()) # Selalu dimulai dengan term

        # Loop jika ada operator tambah/kurang
        while self.current_token and self.current_token.value in ['+', '-', 'atau']:
            op_token = self.current_token
            if op_token.value == '+':
                node.add_child(self.expect("ARITHMETIC_OPERATOR", "+"))
                node.add_child(self.term())
            elif op_token.value == '-':
                 node.add_child(self.expect("ARITHMETIC_OPERATOR", "-"))
                 node.add_child(self.term())
            elif op_token.value.lower() == 'atau':
                 node.add_child(self.expect("LOGICAL_OPERATOR", "atau"))
                 node.add_child(self.term())
        
        return node

    def term(self):
        """
        Aturan produksi: <term> -> <factor> ( <multiplicative-operator> <factor> )*
        """
        node = Node("<term>")
        node.add_child(self.factor()) # Selalu dimulai dengan factor

        # Loop jika ada operator kali/bagi
        while self.current_token and self.current_token.value in ['*', '/', 'bagi', 'mod', 'dan']:
            if self.peek("ARITHMETIC_OPERATOR", "*"):
                node.add_child(self.expect("ARITHMETIC_OPERATOR", "*"))
                node.add_child(self.factor())
            elif self.peek("ARITHMETIC_OPERATOR", "/"):
                node.add_child(self.expect("ARITHMETIC_OPERATOR", "/"))
                node.add_child(self.factor())
            elif self.peek("ARITHMETIC_OPERATOR", "bagi"): # div
                node.add_child(self.expect("ARITHMETIC_OPERATOR", "bagi"))
                node.add_child(self.factor())
            elif self.peek("ARITHMETIC_OPERATOR", "mod"): # mod
                node.add_child(self.expect("ARITHMETIC_OPERATOR", "mod"))
                node.add_child(self.factor())
            elif self.peek("LOGICAL_OPERATOR", "dan"): # and
                node.add_child(self.expect("LOGICAL_OPERATOR", "dan"))
                node.add_child(self.factor())
            else:
                break
        
        return node

    def factor(self):
        """
        Aturan produksi: <factor> -> IDENTIFIER | NUMBER | STRING | CHAR | ( <expression> ) | true | false
        """
        node = Node("<factor>")
        
        if self.peek("IDENTIFIER"):
            # Cek apakah ini Function Call (ID diikuti kurung buka)
            next_token_idx = self.token_index + 1
            
            # Kasus 1: Function Call -> nama_fungsi(...)
            if next_token_idx < len(self.tokens) and self.tokens[next_token_idx].type == "LPARENTHESIS":
                 node.add_child(self.function_call())

            # Kasus 2: Array Access -> nama_array[indeks] 
            elif next_token_idx < len(self.tokens) and self.tokens[next_token_idx].type == "LBRACKET":
                 node.add_child(self.expect("IDENTIFIER"))
                 node.add_child(self.expect("LBRACKET", "["))
                 node.add_child(self.expression()) # Indeks array
                 node.add_child(self.expect("RBRACKET", "]"))

            # Kasus 3: Variabel Biasa
            else:
                 node.add_child(self.expect("IDENTIFIER"))
                 
        elif self.peek("NUMBER"):
            node.add_child(self.expect("NUMBER"))
            
        elif self.peek("STRING_LITERAL"):
            node.add_child(self.expect("STRING_LITERAL"))
            
        elif self.peek("CHAR_LITERAL"):
            node.add_child(self.expect("CHAR_LITERAL"))

        elif self.peek("KEYWORD", "true"):
            node.add_child(self.expect("KEYWORD", "true"))
            
        elif self.peek("KEYWORD", "false"):
            node.add_child(self.expect("KEYWORD", "false"))
            
        elif self.peek("LOGICAL_OPERATOR", "tidak"): # Operator NOT
            node.add_child(self.expect("LOGICAL_OPERATOR", "tidak"))
            node.add_child(self.factor())
            
        elif self.peek("LPARENTHESIS", "("):
            node.add_child(self.expect("LPARENTHESIS", "("))
            node.add_child(self.expression())
            node.add_child(self.expect("RPARENTHESIS", ")"))
            
        else:
            val = self.current_token.value if self.current_token else "EOF"
            raise SyntaxError(f"Error Sintaks: Diharapkan factor, ditemukan '{val}'")
        
        return node
    
    # Control Flow Statements
    def if_statement(self):
        # Grammar: jika <expression> maka <statement> [selain_itu <statement>]
        node = Node("<if-statement>")
        node.add_child(self.expect("KEYWORD", "jika"))
        node.add_child(self.expression())
        node.add_child(self.expect("KEYWORD", "maka"))
        node.add_child(self.statement())
        
        # Cek apakah ada 'selain_itu' (else)
        if self.peek("KEYWORD", "selain_itu"):
            node.add_child(self.expect("KEYWORD", "selain_itu"))
            node.add_child(self.statement())
            
        return node

    def while_statement(self):
        # Grammar: selama <expression> lakukan <statement>
        node = Node("<while-statement>")
        node.add_child(self.expect("KEYWORD", "selama"))
        node.add_child(self.expression())
        node.add_child(self.expect("KEYWORD", "lakukan"))
        node.add_child(self.statement())
        return node

    def for_statement(self):
        # Grammar: untuk <id> := <expr> ke/turun_ke <expr> lakukan <statement>
        node = Node("<for-statement>")
        node.add_child(self.expect("KEYWORD", "untuk"))
        node.add_child(self.expect("IDENTIFIER"))
        node.add_child(self.expect("ASSIGN_OPERATOR", ":="))
        node.add_child(self.expression())
        
        # Cek arah loop
        if self.peek("KEYWORD", "ke"):
            node.add_child(self.expect("KEYWORD", "ke"))
        elif self.peek("KEYWORD", "turun_ke"):
            node.add_child(self.expect("KEYWORD", "turun_ke"))
        else:
            raise SyntaxError("Error Sintaks: Diharapkan 'ke' atau 'turun_ke' dalam loop 'untuk'.")
            
        node.add_child(self.expression())
        node.add_child(self.expect("KEYWORD", "lakukan"))
        node.add_child(self.statement())
        return node
    
    # Procedure Call
    def procedure_call(self):
        # Grammar: IDENTIFIER ( [ <parameter-list> ] )
        node = Node("<procedure-call>")
        node.add_child(self.expect("IDENTIFIER"))
        node.add_child(self.expect("LPARENTHESIS", "("))
        
        if not self.peek("RPARENTHESIS", ")"):
             node.add_child(self.parameter_list())

        node.add_child(self.expect("RPARENTHESIS", ")"))
            
        return node

    def parameter_list(self):
        # Grammar: <expression> (, <expression>)*
        node = Node("<parameter-list>")
        node.add_child(self.expression())
        
        while self.peek("COMMA", ","):
            node.add_child(self.expect("COMMA", ","))
            node.add_child(self.expression())
            
        return node
    
    # Function Call
    def function_call(self):
        # Mirip procedure call tapi mengembalikan nilai (bagian dari factor)
        node = Node("<function-call>")
        node.add_child(self.expect("IDENTIFIER"))
        node.add_child(self.expect("LPARENTHESIS", "("))
        
        # Parameter opsional untuk fungsi
        if not self.peek("RPARENTHESIS", ")"):
             node.add_child(self.parameter_list())
             
        node.add_child(self.expect("RPARENTHESIS", ")"))
        return node
    
    
