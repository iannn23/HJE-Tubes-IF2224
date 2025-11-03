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
            return Node(node_name)
        
        expected_val = f" dengan nilai '{value}'" if value else ""
        current_val = f"'{self.current_token.value}' ({self.current_token.type})" if self.current_token else "None"
        raise SyntaxError(
            f"Error Sintaks: Diharapkan token {token_type}{expected_val}, tetapi ditemukan {current_val}"
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
        if self.peek("KEYWORD", "variabel"):
            node.add_child(self.var_declaration())
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
            var_list_node = Node("<var-list>")
            var_list_node.add_child(self.identifier_list())
            var_list_node.add_child(self.expect("COLON", ":"))
            var_list_node.add_child(self.type_spec())
            var_list_node.add_child(self.expect("SEMICOLON", ";"))
            node.add_child(var_list_node)
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
        else:
            raise SyntaxError(f"Error Sintaks: Tipe data tidak valid '{self.current_token.value}'")
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
        if self.peek("IDENTIFIER"):
            # Cek apakah ini assignment atau procedure call
            # Untuk sekarang, kita asumsikan assignment
            return self.assignment_statement()
        else:
            raise SyntaxError(f"Error Sintaks: Diharapkan sebuah statement, tetapi ditemukan '{self.current_token.value}'")

    def assignment_statement(self):
        node = Node("<assignment-statement>")
        node.add_child(self.expect("IDENTIFIER"))
        node.add_child(self.expect("ASSIGN_OPERATOR", ":="))
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
        # TODO: Tambahkan logika untuk relational operator di sini
        return node

    def simple_expression(self):
        """
        Aturan produksi: <simple-expression> -> <term> ( <additive-operator> <term> )*
        """
        node = Node("<simple-expression>")
        node.add_child(self.term()) # Selalu dimulai dengan term

        # Loop jika ada operator tambah/kurang
        while self.current_token and self.current_token.value in ['+', '-', 'atau']:
            op_token = self.current_token
            if op_token.value == '+':
                node.add_child(self.expect("ARITHMETIC_OPERATOR", "+"))
            elif op_token.value == '-':
                 node.add_child(self.expect("ARITHMETIC_OPERATOR", "-"))
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
            op_token = self.current_token
            if op_token.value == '*':
                node.add_child(self.expect("ARITHMETIC_OPERATOR", "*"))
            elif op_token.value == '/':
                node.add_child(self.expect("ARITHMETIC_OPERATOR", "/"))
            elif op_token.value.lower() == 'bagi':
                node.add_child(self.expect("ARITHMETIC_OPERATOR", "bagi"))
            elif op_token.value.lower() == 'mod':
                node.add_child(self.expect("ARITHMETIC_OPERATOR", "mod"))
            elif op_token.value.lower() == 'dan':
                node.add_child(self.expect("LOGICAL_OPERATOR", "dan"))

            node.add_child(self.factor())
        
        return node

    def factor(self):
        """
        Aturan produksi: <factor> -> IDENTIFIER | NUMBER | ( <expression> )
        """
        node = Node("<factor>")
        
        if self.peek("IDENTIFIER"):
            node.add_child(self.expect("IDENTIFIER"))
        elif self.peek("NUMBER"):
            node.add_child(self.expect("NUMBER"))
        elif self.peek("LPARENTHESIS", "("):
            node.add_child(self.expect("LPARENTHESIS", "("))
            node.add_child(self.expression())
            node.add_child(self.expect("RPARENTHESIS", ")"))
        else:
            raise SyntaxError(f"Error Sintaks: Diharapkan factor (identifier, number, atau '(expr)'), tetapi ditemukan '{self.current_token.value}'")
        
        return node