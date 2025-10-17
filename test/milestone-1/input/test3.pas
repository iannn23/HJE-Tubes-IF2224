program ArrayLogic;

const 
    SIZE = 1..10;

var
    A: array [SIZE] of char;
    flag: boolean;
    
begin
    flag := TRUE and NOT FALSE; (* Logika dan assignment *)
    
    if (A[1] <> 'Z') or flag then 
    begin
        A[1] := 'a'; (* Char Literal *)
    end;

    writeln('Done'); (* String Literal *)
end.