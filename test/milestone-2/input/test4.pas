program SubProgramTest;

variabel
  angka: integer;

fungsi kuadrat(n: integer): integer;
mulai
  kuadrat := n * n;
selesai;

prosedur tampilkan(x: integer);
mulai
  writeln('Nilai adalah: ', x);
selesai;

mulai
  angka := 5;
  tampilkan(kuadrat(angka));
selesai.