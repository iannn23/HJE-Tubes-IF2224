program CekNilai;

variabel
  nilai: integer;
  lulus: boolean;

mulai
  nilai := 75;
  
  jika nilai > 70 maka
    lulus := true
  selain-itu
    lulus := false;

  writeln('Status Lulus: ', lulus);
selesai.