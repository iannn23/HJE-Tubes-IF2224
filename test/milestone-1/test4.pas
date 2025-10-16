program ErrorTest;

var
    z: real;
    
begin
    { Ini adalah komentar gaya curly brace
      yang bisa multi-baris }
    
    z := 5.25; (* Bilangan Real *)
    
    if z >= 0 then
        z := z / 2;
    
    // Simbol di bawah ini harus menghasilkan ERROR LEKSIKAL
    writeln(z); $
    
    (* Ini juga komentar, menggunakan kurung dan bintang *)
end.