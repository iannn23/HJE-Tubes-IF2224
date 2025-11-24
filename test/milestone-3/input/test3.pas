program LoopTest;

variabel
  i, total: integer;

mulai
  total := 0;
  i := 1;

  selama i <= 5 lakukan
  mulai
    total := total + i;
    i := i + 1;
  selesai;

  untuk i := 10 turun_ke 1 lakukan
    writeln('Hitung mundur: ', i);
selesai.