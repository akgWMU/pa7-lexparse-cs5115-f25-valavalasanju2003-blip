PROGRAM ArrayTest;
VAR nums : ARRAY [1 .. 5] OF INTEGER;
BEGIN
    nums[1] := 10;
    nums[2] := nums[1] + 5;
    WRITE(nums[2])
END.
