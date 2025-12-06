
PROGRAM Sample;
VAR x, y : INTEGER;
    a : ARRAY [1 .. 10] OF FLOAT;
BEGIN
    x := 1;
    y := x + 2;
    IF x < y THEN
        WRITE('ok')
    ELSE
        WRITE(0);
    WHILE x < y DO
        x := x + 1
END.
