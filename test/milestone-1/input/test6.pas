program NegativeNumberTest;

const
  MAX_SIZE = 100;

var
  x, y: integer;
  isActive: boolean;
  testString: char; 
  emptyString: char;

begin

  x := -10;

  y := x + (-5);
  
  isActive := true;
  
  testString := 'true';
  
  emptyString := ''; // Baris baru ditambahkan di sini

  if y < -12 then
  begin
    writeln('y is very small');
  end;

end.