program BasicTest;

var
    x, y, total: integer;
    
begin
    x := 5; 
    y := x + 10 mod 3; 
    
    if y > x then 
        total := y 
    else
        total := x;

    writeln('Total:', total);
end.