"""
program Lexer berbasis DFA
"""

#1 Inisiasi dan Pembacaan Input

#Baca argumen : menerima path ke file kode pascal-S dan command line

#Baca aturan DFA: memuat dan memparsing aturan DFA dari file json buat membangun struktur DFA di memori
#Proses ini dari start state, final state(tipe token) dan tabel transisi

#Baca kode sumber pascalnya jadi satu string besar


#2 Proses Scanning (Lexer)

# Buat function run_scanner, ini adalah proses loop dan akan membaca sepanjang source code karakter demi karkter
"""
tokens = list kosong
index_karakter = 0

SELAMA index_karakter < panjang_kode_sumber:
    karakter_saat_ini = kode_sumber[index_karakter]

    # --- A. Abaikan Spasi/Komentar ---
    JIKA karakter_saat_ini adalah spasi, tab, atau newline:
        Lewati karakter tersebut
        Lanjut ke iterasi berikutnya
    JIKA karakter_saat_ini adalah awal_komentar:
        Lewati seluruh blok komentar sampai ditemukan akhir_komentar
        Lanjut ke iterasi berikutnya

    # --- B. Proses Pencarian Token Menggunakan DFA ---
    state_saat_ini = START_STATE
    lexeme_terpanjang = ""
    state_final_terpanjang = None
    indeks_terakhir_diterima = index_karakter

    # Loop Greedy (Mencari urutan karakter terpanjang yang valid)
    SELAMA karakter_berikutnya_ada:
        input_karakter = karakter_berikutnya
        state_berikutnya = Transisi(state_saat_ini, input_karakter)

        JIKA state_berikutnya valid (ada dalam aturan DFA):
            state_saat_ini = state_berikutnya
            lexeme_saat_ini += input_karakter

            JIKA state_saat_ini adalah FINAL_STATE:
                # Simpan sebagai kandidat token terpanjang (Greedy Match)
                lexeme_terpanjang = lexeme_saat_ini
                state_final_terpanjang = state_saat_ini
                indeks_terakhir_diterima = indeks_saat_ini

        SELAIN ITU (Transisi Mati):
            Hentikan pencarian token ini
            Jeda loop greedy
            
    # --- C. Klasifikasi dan Output Token ---
    JIKA ditemukan lexeme_terpanjang:
        # Pindah pointer kembali ke posisi terakhir yang diterima DFA
        index_karakter = indeks_terakhir_diterima + 1
        
        # Cek apakah lexeme ini adalah KEYWORD atau IDENTIFIER?
        token_type = Dapatkan_Tipe_Token(lexeme_terpanjang, state_final_terpanjang, Daftar_Keyword)
        
        Buat Objek Token(token_type, lexeme_terpanjang)
        Tambahkan Objek Token ke list 'tokens'
    
    SELAIN ITU (Error Leksikal):
        # Program dapat menangani error dengan baik [cite: 179]
        Laporkan Error Leksikal (Simbol tidak dikenal)
        index_karakter += 1 # Lanjut ke karakter berikutnya

KEMBALI tokens
"""

#3 Klasifikasi Keyword dan Identifier

#Lexer harus dapat membedakan antara identifier dan keyword
#Identifier adalah nama variable yang dibuat oleh user
#Keyword adalah kata kunci yang udah didefinisikan sebelumnya

#pola DFA mungkin memiliki pola yang sama
#Solusinya adalah setelah DFA selesai mengenali lexeme, dia akan mengecek apakah nilai lexeme (program, var) ada dalam daftar keyword yang udah ditentuin
#Kalo ada akan dianggap sebagai tipe keyword kalo ga ada jadi identifier



#4 Output
# Proses setelah looping selesai
#Main program akan menerima list token hasil pemrosesan
#Mencetak daftar token ke terminal dengan format yang jelas seperty (TYPE(value))