program TestAllTokens; {1, 2, 10}

//testing untuk semua token
const
    PiValue = 3.14; {1, 2, 7, 10}

type
    MyArrayType = array [1..10] of integer; {1, 2, 18, 16, 17, 1}

var
    sum, count: integer; {2, 11, 12, 1}
    flag: boolean; {2, 12, 1}
    ch: char; {2, 12, 1}
    
begin
    sum := 0; {1, 2, 6, 7, 10}
    count := 5; {2, 6, 7, 10}
    
    ch := 'A'; {2, 6, 8, 10} 

    if (sum <> 0) and (count > 0) then {1, 14, 2, 4, 7, 15, 5, 14, 2, 4, 7, 15, 1}
        flag := TRUE  // TRUE bukan keyword di Pascal-S, tapi kita asumsikan untuk boolean
    else 
        flag := FALSE;
        
    while flag do {1}
    begin
        count := count div 2; {2, 6, 2, 3, 7, 10}
    end;
    
    for count := 1 to 10 do {1, 2, 6, 7, 1, 7, 1}
        sum := sum + count; {2, 6, 2, 3, 2, 10}
        
    writeln('Final Sum: ', sum); {2, 14, 9, 11, 2, 15, 10}
    
    end. {1, 13}