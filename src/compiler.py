import sys
import os
from lexer import Lexer
from pascal_token import Token 

# KEYWORD Pascal-S
PASCAL_S_KEYWORDS = [
    # Keyword
    "program", "var", "begin", "end", "if", "then", "else", "while", "do", 
    "for", "to", "downto", "integer", "real", "boolean", "char", "array", 
    "of", "procedure", "function", "const", "type", "true", "false"
]

def main():
    #Penerimaan Input File
    if len(sys.argv) != 2:
        print("Penggunaan: python compiler.py [Kode Pascal]")
        return
        
    pascal_file = sys.argv[1]
    
    if not os.path.exists(pascal_file) or not os.path.isfile(pascal_file):
            print(f"File input '{pascal_file}' tidak ditemukan atau bukan file yang valid.")
            raise SystemExit(1)

    #Membaca kode Pascal-S
    try:
        with open(pascal_file, 'r') as f:
            source_code = f.read()
    except Exception as e:
        print(f"Gagal membaca file input: {e}")
        return

    #Inisialisasi Lexer
    dfa_path = os.path.join(os.path.dirname(__file__), "dfa_rules.json")
    try:
        lexer = Lexer(dfa_path, PASCAL_S_KEYWORDS)
    except SystemExit:
        return

    # 4. Melakukan Scanning
    tokens = lexer.run_scanner(source_code)

    # 5. Penghasilan Output
    if tokens:
        input_path = pascal_file 
        input_filename = os.path.basename(input_path)
        
        milestone_dir = os.path.dirname(os.path.dirname(input_path)) 
        
        test_number = "".join(filter(str.isdigit, input_filename))
        output_filename = f"output-{test_number}.txt"

        output_dir = os.path.join(milestone_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, output_filename)

        try:
            with open(output_path, 'w') as f:
                for token in tokens:
                    f.write(str(token) + '\n')
            print(f"Output berhasil ditulis ke: {output_path}")
        except Exception as e:
            print(f"Gagal menulis file output: {e}")

    else:
        print("Tidak ada token yang dihasilkan atau terjadi error.")
        
if __name__ == "__main__":
    main()