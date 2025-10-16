import json
import os
from pascal_token import Token

class Lexer:
    """
    Melakukan analisis leksikal menggunakan DFA yang dimuat dari file.
    """
    
    def __init__(self, dfa_file_path, keyword_list):
        self.keywords = keyword_list
        self.dfa = self.load_dfa(dfa_file_path)
    
        self.current_index = 0
        self.current_line = 1
        self.current_coloumn = 1

    def load_dfa(self, file_path):
        """
        Membaca dan memparsing file aturan DFA (JSON atau TXT).
        """
        #print(f"Menginisialisasi DFA dari: {file_path}")
        try:
            with open(file_path, 'r') as f:
                dfa_data = json.load(f)

                if 'start_state' not in dfa_data or 'final_states' not in dfa_data or 'transitions' not in dfa_data:
                    print("File aturan DFA tidak lengkap")
                    return None
            return dfa_data
        
        except json.JSONDecodeError as e:
            print(f"Format File DFA tidak valid {e}")
            return None

        except FileNotFoundError:
            print(f"File tidak ditemukan di {file_path}")
            return None

        except ValueError as e:
            print(f"Error pada konfigurasi DFA {e}")
            return None

    def get_token_type(self, lexeme, final_state):
        """
        Menentukan tipe token, termasuk mengecek apakah lexeme adalah KEYWORD atau IDENTIFIER.
        """
        token_type = self.dfa['final_states'].get(final_state)
        lexeme_lower = lexeme.lower()

        if token_type == "IDENTIFIER_CANDIDATE":
            if lexeme_lower in [k.lower() for k in self.keywords]:
                return "KEYWORD"
            else:
                return "IDENTIFIER"
            
        return token_type if token_type else "UNKNOWN_TOKEN"

    def advance_past_comment(self, source_code, index):
        """
        Melakukan scanning untuk melewati seluruh blok komentar (misalnya: (*...*) atau {...}).
        Mengembalikan index setelah akhir komentar dan penyesuaian baris/kolom.
        """
        return index, 0, 0
    
    def classify_char_input(self, char):
        if char.isalpha():
            return "letter"
        if char.isdigit():
            return "digit"
        return char

    def run_scanner(self, source_code):
        """
        Melakukan scanning kode sumber huruf demi huruf menggunakan logika DFA.
        """
        tokens = []
        

        while self.current_index < len(source_code):
            token_start_line = self.current_line
            token_start_coloumn = self.current_coloumn

            char = source_code[self.current_index]

            #Buat handle whitespace
            if char.isspace():
                if char == '\n':
                    self.current_line += 1
                    self.current_coloumn = 1
                else:
                    self.current_coloumn += 1
                self.current_index += 1
                continue

            # Handle comment
            if char == '{' or (char == '(' and self.current_index + 1 < len(source_code) and source_code[self.current_index + 1] == '*'):
                # Skip comment content
                if char == '{':
                    self.current_index += 1
                    self.current_coloumn += 1
                    while self.current_index < len(source_code) and source_code[self.current_index] != '}':
                        if source_code[self.current_index] == '\n':
                            self.current_line += 1
                            self.current_coloumn = 1
                        else:
                            self.current_coloumn += 1
                        self.current_index += 1
                    if self.current_index < len(source_code):
                        self.current_index += 1
                        self.current_coloumn += 1
                else:  # Handle (* ... *) comments
                    self.current_index += 2 
                    self.current_coloumn += 2
                    while self.current_index + 1 < len(source_code):
                        if (self.current_index + 1 < len(source_code) and 
                            source_code[self.current_index:self.current_index+2] == '*)'):
                            self.current_index += 2
                            self.current_coloumn += 2
                            break
                        if source_code[self.current_index] == '\n':
                            self.current_line += 1
                            self.current_coloumn = 1
                        else:
                            self.current_coloumn += 1
                        self.current_index += 1
                continue


            #Scanning Token 
            current_state = self.dfa['start_state']
            lexeme =""
            longest_finalstate = None
            longest_lexeme = ""
            last_valid_index = self.current_index

            temp_index = self.current_index

            while temp_index < len(source_code):
                temp_char = source_code[temp_index]
                input_symbol = self.classify_char_input(temp_char)
                
                # Cek ada transisi ga
                if current_state in self.dfa['transitions'] and input_symbol in self.dfa['transitions'][current_state]:
                    current_state = self.dfa['transitions'][current_state][input_symbol]
                    lexeme += temp_char
                    temp_index += 1
                    
                    # Cek current state nya final atau ga
                    if current_state in self.dfa['final_states']:
                        longest_lexeme = lexeme
                        longest_finalstate = current_state
                        last_valid_index = temp_index
                else:
                    # No valid transition, stop
                    break

            #Buat tokennya
            if longest_lexeme:
                token_type = self.get_token_type(longest_lexeme, longest_finalstate)
                tokens.append(Token(token_type, longest_lexeme, token_start_line, token_start_coloumn))

                #terus majuin poinnya ke posisi setelah token found
                self.current_coloumn += len(longest_lexeme)
                self.current_index = last_valid_index
            else:
                # Lexical error unknown symbol
                tokens.append(Token("LEXICAL_ERROR", char, token_start_line, token_start_coloumn))
                print(f"Simbol unknown '{char}' pada baris {token_start_line}")
                self.current_index += 1
                self.current_coloumn += 1
        
        return tokens


        
            



