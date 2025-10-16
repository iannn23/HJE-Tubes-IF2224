class Token:
    """
    Merepresentasikan satu unit makna tunggal (Token).
    """
    def __init__(self, type, value, line=None, column=None):
        # inisiasi objek token
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __str__(self):
        """
        print representasi string Token sesuai format output yang diminta
        """
        return f"{self.type}({self.value})"