PROGRAM LogicTest;
VAR a, b : INTEGER;
BEGIN
    a := 2;
    b := 5;
    IF (a < b) AND (b > 3) THEN
        WRITE('ok')
    ELSE
        WRITE('no')
END.
