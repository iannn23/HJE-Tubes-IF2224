program ArrayKompleks;

konstanta
  MAX = 100;

tipe
  Vektor = larik [1..10] dari integer;

variabel
  data: Vektor;
  idx: integer;

mulai
  idx := 1;
  data[idx] := MAX div 2;
  
  jika data[1] <> 0 maka
    writeln('Data valid');
selesai.