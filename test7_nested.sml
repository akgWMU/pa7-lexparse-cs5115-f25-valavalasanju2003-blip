PROGRAM NestedTest;
VAR x : INTEGER;
BEGIN
    x := 0;
    WHILE x < 3 DO
        BEGIN
            IF x = 1 THEN
                WRITE('one')
            ELSE
                WRITE('not one');
            x := x + 1
        END
END.
