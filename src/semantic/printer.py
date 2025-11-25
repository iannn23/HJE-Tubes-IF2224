from .ast_nodes import AST

def print_ast(node, prefix="", is_last=True, file=None, is_root=True):
    if node is None:
        return

    node_type = type(node).__name__
    
    # --- 1. MEMBUAT LABEL (Teks Node) ---
    
    # Format: ProgramNode
    if node_type == "Program":
        label = f"ProgramNode(name: '{node.name}')"
    
    # Format: VarDecl('x') -> tab_index:..., type:..., lev:...
    elif node_type == "VarDecl":
        var_name = node.var_node.value
        sem_info = []
        if hasattr(node.var_node, 'tab_entry') and node.var_node.tab_entry:
            sem_info.append(f"tab_index:{node.var_node.tab_entry.get('idx')}")
            sem_info.append(f"type:{node.type_node.value}")
            sem_info.append(f"lev:{node.var_node.tab_entry.get('lev')}")
        
        label = f"VarDecl('{var_name}')"
        if sem_info:
            label += " -> " + ", ".join(sem_info)
            
    # Format: Assign('x' := ...) -> type:integer
    elif node_type == "Assign":
        label = f"Assign('{node.left.value}' := ...)"
        if hasattr(node, 'sem_type'):
             label += f" -> type:integer" # Asumsi integer utk display
    
    # Format: BinOp '+' -> type:integer
    elif node_type == "BinOp":
        val = node.op.value if hasattr(node.op, 'value') else node.op
        label = f"BinOp '{val}'"
        if hasattr(node, 'sem_type'):
             label += f" -> type:integer"

    # Format: target 'x' -> ...
    elif node_type == "Var":
        label = f"target '{node.value}'"
        if hasattr(node, 'tab_entry') and node.tab_entry:
             label += f" -> tab_index:{node.tab_entry.get('idx')}, type:integer"

    # Format: 10 -> type:integer
    elif node_type == "Num":
        label = f"{node.value}"
        label += " -> type:integer"
        
    # Format: ProcedureCall(name: 'writeln')
    elif node_type == "ProcedureCall":
        label = f"ProcedureCall(name: '{node.proc_name}')"

    # Default
    else:
        info = ""
        if hasattr(node, 'value') and node.value is not None:
            info += f" '{node.value}'"
        label = f"{node_type}{info}"

    # --- 2. MENCETAK NODE ---
    if is_root:
        line = f"{label}\n"
        new_prefix = ""
    else:
        connector = "└── " if is_last else "├── "
        line = f"{prefix}{connector}{label}\n"
        new_prefix = prefix + ("    " if is_last else "│   ")
    
    if file:
        file.write(line)
    else:
        print(line, end="")

    # --- 3. MENGUMPULKAN ANAK (CHILDREN) SECARA SPESIFIK ---
    # Bagian ini mengontrol struktur pohon agar sesuai spesifikasi
    
    children_to_print = []

    if node_type == "Program":
        children_to_print = [node.block]

    elif node_type == "Block":
        # Khusus Block: Kita cetak pseudo-node 'Declarations' manual
        if node.declarations:
            # Kita handle pencetakan Declarations di sini agar rapi
            connector = "├── " if node.compound_statement.children else "└── "
            decl_header = f"{new_prefix}{connector}Declarations\n"
            if file: file.write(decl_header)
            else: print(decl_header, end="")
            
            decl_prefix = new_prefix + ("│   " if node.compound_statement.children else "    ")
            for i, decl in enumerate(node.declarations):
                print_ast(decl, decl_prefix, i == len(node.declarations)-1, file, is_root=False)
        
        # Ambil statement langsung dari compound_statement (Flattening)
        # Agar 'Compound' hilang dan isinya langsung nempel di Block
        if node.compound_statement:
            children_to_print = node.compound_statement.children

    elif node_type == "VarDecl":
        # Stop! Jangan cetak anak apapun (var_node/type_node sudah di label)
        pass 

    elif node_type == "Assign":
        # Anak Assign: Target (Left) dan Value (Right)
        children_to_print = [node.left, node.right]

    elif node_type == "BinOp":
        children_to_print = [node.left, node.right]
    
    elif node_type == "ProcedureCall":
        children_to_print = node.actual_params

    elif node_type == "Var" or node_type == "Num" or node_type == "Type" or node_type == "StringLiteral":
        # Leaf node, tidak punya anak visual
        pass

    else:
        # Default fallback: kumpulkan semua AST object
        for key, val in vars(node).items():
            if key in ['sem_type', 'sem_scope', 'token', 'tab_entry', 'op', 'name', 'value']: continue
            if isinstance(val, list):
                for item in val:
                    if isinstance(item, AST): children_to_print.append(item)
            elif isinstance(val, AST):
                children_to_print.append(val)

    # --- 4. REKURSIF KE ANAK ---
    count = len(children_to_print)
    for i, child in enumerate(children_to_print):
        is_last_child = (i == count - 1)
        print_ast(child, new_prefix, is_last_child, file, is_root=False)


def write_symbol_tables(symtab, f):
    """
    Mencetak tabel simbol sesuai urutan kolom di Lampiran B Spesifikasi.
    """
    # A. TAB (Identifier Table)
    f.write("=== SYMBOL TABLE (TAB) ===\n")
    header = f"{'Idx':<4} | {'ID':<15} | {'Link':<4} | {'Obj':<10} | {'Type':<4} | {'Ref':<4} | {'Nrm':<4} | {'Lev':<4} | {'Adr':<4}\n"
    f.write(header)
    f.write("-" * len(header) + "\n")
    
    for i, entry in enumerate(symtab.tab):
        obj_str = str(entry['obj'])
        if obj_str == "RES": continue 
        
        f.write(f"{i:<4} | {entry['id']:<15} | {entry['link']:<4} | {obj_str:<10} | {entry['type']:<4} | {entry['ref']:<4} | {entry['nrm']:<4} | {entry['lev']:<4} | {entry['adr']:<4}\n")
    
    # B. BTAB (Block Table)
    f.write("\n=== BLOCK TABLE (BTAB) ===\n")
    header_btab = f"{'Idx':<4} | {'Last':<4} | {'Lpar':<4} | {'Psze':<4} | {'Vsze':<4}\n"
    f.write(header_btab)
    f.write("-" * len(header_btab) + "\n")
    for i, blk in enumerate(symtab.btab):
        f.write(f"{i:<4} | {blk['last']:<4} | {blk['lpar']:<4} | {blk['psze']:<4} | {blk['vsze']:<4}\n")

    # C. ATAB (Array Table)
    f.write("\n=== ARRAY TABLE (ATAB) ===\n")
    if not symtab.atab:
        f.write("(Kosong)\n")
    else:
        pass