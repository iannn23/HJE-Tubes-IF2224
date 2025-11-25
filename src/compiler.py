import sys
import os
import io
from lexer import Lexer
from pascal_token import Token 
from parser import Parser
from semantic.analyzer import SemanticAnalyzer
# Import fungsi cetak dari printer.py
from semantic.printer import print_ast, write_symbol_tables

# KEYWORD Pascal-S
PASCAL_S_KEYWORDS = [
    # Keyword
    "program", "var", "begin", "end", "if", "then", "else", "while", "do", 
    "for", "to", "downto", "integer", "real", "boolean", "char", "array", 
    "of", "procedure", "function", "const", "type", "true", "false",
    # Padanan Bahasa Indonesia
    "program", "variabel", "mulai", "selesai", "jika", "maka", "selain_itu", "selama", "lakukan",
    "untuk", "ke", "turun_ke", "integer", "real", "boolean", "char", "larik",
    "dari", "prosedur", "fungsi", "konstanta", "tipe", "true", "false"
]

def main():
    # Penerimaan Input File
    if len(sys.argv) != 2:
        print("Penggunaan: python src/compiler.py [File Pascal]")
        return
        
    pascal_file = sys.argv[1]
    
    if not os.path.exists(pascal_file) or not os.path.isfile(pascal_file):
            print(f"File input '{pascal_file}' tidak ditemukan.")
            raise SystemExit(1)

    # Membaca kode Pascal-S
    try:
        with open(pascal_file, 'r') as f:
            source_code = f.read()
    except Exception as e:
        print(f"Gagal membaca file input: {e}")
        return

    # Inisialisasi Lexer
    dfa_path = os.path.join(os.path.dirname(__file__), "dfa_rules.json")
    try:
        lexer = Lexer(dfa_path, PASCAL_S_KEYWORDS)
    except SystemExit:
        return

    # 4. Melakukan Scanning
    tokens = lexer.run_scanner(source_code)

    if tokens:
        # Persiapan Folder Output
        input_path = pascal_file 
        input_filename = os.path.basename(input_path)
        milestone_dir = os.path.dirname(os.path.dirname(input_path)) 
        
        test_number = "".join(filter(str.isdigit, input_filename))
        if not test_number: test_number = "result"
            
        output_dir = os.path.join(milestone_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        # 5. Output Token (Milestone 1 Requirement)
        token_output_path = os.path.join(output_dir, f"output-{test_number}.txt")
        try:
            with open(token_output_path, 'w') as f:
                for token in tokens:
                    f.write(str(token) + '\n')
            print(f"[INFO] Token ditulis ke: {token_output_path}")
        except Exception as e:
            print(f"[ERROR] Gagal tulis token: {e}")

        # 6. Parser (Milestone 2)
        print("\nLexer selesai. Memulai parser...")
        parser = Parser(tokens)
        try:
            parse_tree = parser.parse()
            
            if parse_tree:
                print("Parse Tree berhasil dibuat.")
                
                # Output Parse Tree (Milestone 2 Requirement)
                try:
                    parsetree_output_path = os.path.join(output_dir, f"parsetree-{test_number}.txt")
                    
                    f_buffer = io.StringIO()
                    original_stdout = sys.stdout  
                    sys.stdout = f_buffer         
                    parse_tree.print_tree()
                    sys.stdout = original_stdout
                    tree_string = f_buffer.getvalue()
                    
                    with open(parsetree_output_path, 'w', encoding='utf-8') as f:
                        f.write(tree_string)
                    print(f"[INFO] Parse tree ditulis ke: {parsetree_output_path}")
                
                except Exception as e:
                    print(f"[ERROR] Gagal tulis parse tree: {e}")

                # 7. Semantic Analysis (Milestone 3)
                print("\n---------------------------------------------------")
                print("Memulai Analisis Semantik (Milestone 3)...")
                print("---------------------------------------------------")
                
                try:
                    analyzer = SemanticAnalyzer()
                    ast, symtab = analyzer.analyze(parse_tree)
                    
                    print("[SUKSES] Semantic Analysis Selesai!")
                    
                    semantic_output_path = os.path.join(output_dir, f"semantic-output-{test_number}.txt")
                    
                    with open(semantic_output_path, 'w', encoding='utf-8') as f:
                        write_symbol_tables(symtab, f)

                        # Tulis Header AST (Tanpa garis dekoratif)
                        f.write("\n=== DECORATED AST ===\n")

                        # Tulis Pohon AST (dari printer.py)
                        print_ast(ast, file=f)

                    print(f"[INFO] Hasil Semantic Analysis (Tabel + AST) ditulis ke: {semantic_output_path}")

                except Exception as e:
                    print(f"\n[SEMANTIC ERROR] {e}")

            else:
                print("Tidak ada output dari parser.")

        except SyntaxError as e:
            print(f"\n[PARSING GAGAL] {e}")

    else:
        print("Tidak ada token yang dihasilkan oleh lexer.")
        
if __name__ == "__main__":
    main()