PROGRAM CoercionTest;
VAR x : INTEGER;
    y : FLOAT;
BEGIN
    x := 4;
    y := x + 3.5;   { INTEGER coerced to FLOAT }
    WRITE(y)
END.
