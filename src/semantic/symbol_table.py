class SymbolTable:
    """
    Symbol Table sesuai spesifikasi Pascal-S.
    Obj codes: 0=konstanta, 1=variabel, 2=tipe, 3=prosedur, 4=fungsi, 5=program
    Type codes: 0=none, 1=integer, 2=real, 3=boolean, 4=char
    """
    
    def __init__(self):
        self.tab = []      # Identifier Table
        self.btab = []     # Block Table
        self.atab = []     # Array Table
        self.display = []  # Scope display
        self.level = 0     # Current level
        
        # Inisialisasi Reserved Words (Padding agar index mulai dari angka tinggi seperti di contoh)
        # Di spesifikasi index mulai 29, jadi kita isi dummy 0-28
        for i in range(29):
            self.tab.append({"id": f"reserved_{i}", "obj": "RES", "type": 0, "ref": 0, "nrm": 0, "lev": 0, "adr": 0, "link": 0})

        self._init_global_block()

    def _init_global_block(self):
        # Blok 0 (Global)
        self.btab.append({"last": 0, "lpar": 0, "psze": 0, "vsze": 0})
        self.display.append(0)
        
        # Tipe Dasar (Integer=1, Real=2, Bool=3, Char=4)
        # obj=2 (Type)
        self._add_basic_type("integer", 1)
        self._add_basic_type("real", 2)
        self._add_basic_type("boolean", 3)
        self._add_basic_type("char", 4)

    def _add_basic_type(self, name, type_code):
        # ref=0, nrm=0 for types
        self.tab.append({
            "id": name, "obj": "type", "type": type_code, 
            "ref": 0, "nrm": 0, "lev": 0, "adr": 0, "link": 0
        })

    def add_program_name(self, name):
        # obj=program
        self.tab.append({
            "id": name, "obj": "program", "type": 0,
            "ref": 0, "nrm": 0, "lev": 0, "adr": 0, "link": 0
        })
        # Tidak update link/last karena program name biasanya spesial

    def add_variable(self, name, type_code):
        curr_block_idx = self.display[self.level]
        last_id = self.btab[curr_block_idx]["last"]
        
        # Hitung address (offset) berdasarkan vsze saat ini
        current_adr = self.btab[curr_block_idx]["vsze"]
        
        # obj=variable (1), nrm=1 (normal variable)
        entry = {
            "id": name, "obj": "variable", "type": type_code,
            "ref": 0, "nrm": 1, "lev": self.level, 
            "adr": current_adr, "link": last_id
        }
        self.tab.append(entry)
        
        new_idx = len(self.tab) - 1
        
        # Update Block Info
        self.btab[curr_block_idx]["last"] = new_idx
        self.btab[curr_block_idx]["vsze"] += 1 # Asumsi ukuran 1 word
        
        return new_idx

    def add_procedure(self, name):
        curr_block_idx = self.display[self.level]
        last_id = self.btab[curr_block_idx]["last"]
        
        # obj=procedure
        entry = {
            "id": name, "obj": "procedure", "type": 0, # Void
            "ref": 0, "nrm": 0, "lev": self.level,
            "adr": 0, "link": last_id 
        }
        self.tab.append(entry)
        new_idx = len(self.tab) - 1
        
        self.btab[curr_block_idx]["last"] = new_idx
        return new_idx

    def enter_scope(self):
        self.level += 1
        # Buat blok baru
        self.btab.append({"last": 0, "lpar": 0, "psze": 0, "vsze": 0})
        self.display.append(len(self.btab) - 1)

    def exit_scope(self):
        self.level -= 1
        self.display.pop()

    def lookup(self, name):
        # Cari dari level tertinggi ke 0
        for lev in range(self.level, -1, -1):
            # Mulai dari 'last' di blok level tersebut
            curr = self.btab[self.display[lev]]["last"]
            while curr > 0:
                if self.tab[curr]["id"] == name:
                    # Kembalikan entry + indexnya agar bisa dicatat di AST
                    entry = self.tab[curr].copy()
                    entry['idx'] = curr
                    return entry
                curr = self.tab[curr]["link"]
        
        # Cek tipe dasar (yang tidak masuk linked list blok)
        # Tipe dasar ada di index 29-32 (sesuai inisialisasi di atas)
        for i in range(29, len(self.tab)):
            if self.tab[i]["id"] == name and self.tab[i]["obj"] == "type":
                entry = self.tab[i].copy()
                entry['idx'] = i
                return entry
                
        return None