
// Program

        regwi 0, $1, 100;
        synci 200;
        regwi 0, $15, 0;
        regwi 0, $14, 0;
LOOP_J: mathi 0, $1, $1, +, -50;
        memwi 0, $1, 123;
        mathi 0, $15, $15, +, 1;
        memwi 0, $15, 1;
        loopnz 0, $14, @LOOP_J;
        end ;