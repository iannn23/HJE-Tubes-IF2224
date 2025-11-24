class SymbolTable:
    """
    Kelas SymbolTable untuk mengelola informasi identifier (variabel, fungsi, prosedur, dll)
    selama proses Semantic Analysis.
    
    Struktur data mengacu pada spesifikasi Pascal-S:
    1. tab  : Tabel Identifier (menyimpan nama, tipe, level, alamat, dll).
    2. btab : Tabel Blok (menyimpan informasi scope prosedur/fungsi).
    3. atab : Tabel Array (menyimpan informasi detail tipe array).
    """
    
    def __init__(self):
        self.tab = []      # Tabel Identifier: id, link, obj, type, ref, nrm, lev, adr
        self.btab = []     # Tabel Blok: last, lpar, psze, vsze
        self.atab = []     # Tabel Array: xtyp, etyp, eref, low, high, elsz, size
        self.display = []  # Register display untuk melacak blok aktif per level
        self.level = 0     # Level scope saat ini (0 = Global)
        self._init_global_block()

    def _init_global_block(self):
        """
        Membuat blok pertama (Global Block) untuk Program Utama.
        """
        self.btab.append({"last": 0, "lpar": 0, "psze": 0, "vsze": 0}) # Buat blok global (indeks 0)
        self.display.append(0)
        
        # Daftarkan tipe dasar: integer=1, real=2, boolean=3, char=4
        for name, code in [("integer", 1), ("real", 2), ("boolean", 3), ("char", 4)]:
            self._add_basic_type(name, code)

    def _add_basic_type(self, name, type_code):
        """
        Menambahkan tipe dasar (integer, real, boolean, char) ke tabel simbol.
        """
        self.tab.append({"id": name, "obj": 2, "type": type_code, "ref": 0, "nrm": 0, "lev": 0, "adr": 0, "link": 0})

    def add_variable(self, name, type_code):
        """
        Menambahkan variabel baru ke scope saat ini.
        Mengembalikan indeks variabel baru di tabel 'tab'.
        """
        curr_block = self.display[self.level]
        last_id = self.btab[curr_block]["last"]
        
        # Masukkan variabel ke tab dan hubungkan link ke identifier sebelumnya
        self.tab.append({"id": name, "obj": 1, "type": type_code, "ref": 0, "nrm": 1, "lev": self.level, "adr": self.btab[curr_block]["vsze"], "link": last_id})
        
        # Update pointer last dan ukuran variabel di blok saat ini
        self.btab[curr_block]["last"] = len(self.tab) - 1
        self.btab[curr_block]["vsze"] += 1
        return len(self.tab) - 1

    def enter_scope(self):
        """
        Membuat blok baru (misal masuk fungsi/prosedur) dan menaikkan level scope.
        """
        self.level += 1
        self.btab.append({"last": 0, "lpar": 0, "psze": 0, "vsze": 0}) # Buat entri blok baru
        self.display.append(len(self.btab) - 1)

    def exit_scope(self):
        """
        Keluar dari blok saat ini (selesai fungsi/prosedur) dan menurunkan level scope.
        """
        self.level -= 1
        self.display.pop() # Hapus display level ini, tapi biarkan data di btab

    def lookup(self, name):
        """
        Mencari identifier berdasarkan nama.
        Mencari dari scope terdalam (level saat ini) mundur ke global.
        """
        # Cari identifier mundur dari scope level saat ini ke global (0)
        for lev in range(self.level, -1, -1):
            curr = self.btab[self.display[lev]]["last"]
            while curr > 0: # Telusuri linked list dalam blok
                if self.tab[curr]["id"] == name: return self.tab[curr]
                curr = self.tab[curr]["link"]
        return None