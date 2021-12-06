
// Program

        regwi 3, $16, 69905067;                 //freq = 100.00000047683716 MHz
        regwi 3, $17, 0;                        //phase = 0
        regwi 3, $19, 3000;                     //gain = 3000
        regwi 3, $21, 0;                        //t = 0
        regwi 3, $20, 589844;                   //stdysel | mode | outsel = 0b01001 | length = 20 
        synci 200;
        regwi 0, $15, 0;
        regwi 0, $14, 0;
LOOP_J: regwi 0, $31, 49152;                    //out = 0b1100000000000000
        seti 0, 0, $31, 100;                    //ch =0 out = $31 @t = 0
        regwi 0, $31, 0;                        //out = 0b0000000000000000
        seti 0, 0, $31, 110;                    //ch =0 out = $31 @t = 0
        regwi 3, $20, 589844;                   //stdysel | mode | outsel = 0b01001 | length = 20 
        regwi 3, $21, 0;                        //t = 0
        set 7, 3, $16, $17, $18, $19, $20, $21; //ch = 7, out = $16,$18,$19,$20 @t = $21
        synci 20;
        mathi 0, $15, $15, +, 1;
        memwi 0, $15, 1;
        loopnz 0, $14, @LOOP_J;
        end ;

// Program

        regwi 3, $16, 69905067;                 //freq = 100.00000047683716 MHz
        regwi 3, $17, 0;                        //phase = 0
        regwi 3, $19, 5000;                     //gain = 5000
        regwi 3, $21, 0;                        //t = 0
        regwi 3, $18, 0;                        //addr = 0
        regwi 3, $20, 524363;                   //stdysel | mode | outsel = 0b01000 | length = 75 
        regwi 3, $22, 50;
        synci 200;
        regwi 0, $15, 0;
        regwi 0, $14, 0;
LOOP_J: regwi 0, $31, 49152;                    //out = 0b1100000000000000
        seti 0, 0, $31, 200;                    //ch =0 out = $31 @t = 0
        regwi 0, $31, 0;                        //out = 0b0000000000000000
        seti 0, 0, $31, 210;                    //ch =0 out = $31 @t = 0
        regwi 3, $18, 0;                        //addr = 0
        regwi 3, $20, 524363;                   //stdysel | mode | outsel = 0b01000 | length = 75 
        regwi 3, $22, 50;
        regwi 3, $19, 5000;                     //gain = 5000
        regwi 3, $21, 0;                        //t = 0
        regwi 3, $18, 0;                        //addr = 0
        regwi 3, $20, 524363;                   //stdysel | mode | outsel = 0b01000 | length = 75 
        set 7, 3, $16, $17, $18, $19, $20, $21; //ch = 7, out = $16,$18,$19,$20 @t = $21
        regwi 3, $19, 2500;                     //gain = 2500
        regwi 3, $21, 0;                        //t = 0
        regwi 3, $18, 0;                        //addr = 0
        regwi 3, $20, 589824;                   //stdysel | mode | outsel = 0b01001 | length = 0 
        math 3, $20, $20, +, $22;               //+
        set 7, 3, $16, $17, $18, $19, $20, $21; //ch = 7, out = $16,$18,$19,$20 @t = $21
        regwi 3, $19, 5000;                     //gain = 5000
        regwi 3, $21, 125;                      //t = 125
        regwi 3, $18, 75;                       //addr = 75
        regwi 3, $20, 524363;                   //stdysel | mode | outsel = 0b01000 | length = 75 
        set 7, 3, $16, $17, $18, $19, $20, $21; //ch = 7, out = $16,$18,$19,$20 @t = $21
        synci 200;
        mathi 0, $15, $15, +, 1;
        memwi 0, $15, 1;
        loopnz 0, $14, @LOOP_J;
        end ;

// Program

        regwi 3, $16, 69905067;                 //freq = 100.00000047683716 MHz
        regwi 3, $17, 0;                        //phase = 0
        regwi 3, $19, 5000;                     //gain = 5000
        regwi 3, $18, 0;                        //addr = 0
        regwi 3, $20, 524438;                   //stdysel | mode | outsel = 0b01000 | length = 150 
        synci 200;
        regwi 0, $15, 0;
        regwi 0, $14, 0;
LOOP_J: regwi 0, $31, 49152;                    //out = 0b1100000000000000
        seti 0, 0, $31, 200;                    //ch =0 out = $31 @t = 0
        regwi 0, $31, 0;                        //out = 0b0000000000000000
        seti 0, 0, $31, 210;                    //ch =0 out = $31 @t = 0
        regwi 3, $18, 0;                        //addr = 0
        regwi 3, $20, 524438;                   //stdysel | mode | outsel = 0b01000 | length = 150 
        regwi 3, $21, 0;                        //t = 0
        set 7, 3, $16, $17, $18, $19, $20, $21; //ch = 7, out = $16,$18,$19,$20 @t = $21
        synci 150;
        mathi 0, $15, $15, +, 1;
        memwi 0, $15, 1;
        loopnz 0, $14, @LOOP_J;
        end ;

// Program

        regwi 3, $16, 69905067;                 //freq = 100.00000047683716 MHz
        regwi 3, $17, 0;                        //phase = 0
        regwi 3, $19, 1000;                     //gain = 1000
        regwi 3, $21, 0;                        //t = 0
        regwi 3, $20, 589844;                   //stdysel | mode | outsel = 0b01001 | length = 20 
        synci 200;
        regwi 0, $15, 0;
        regwi 0, $14, 0;
LOOP_J: regwi 0, $31, 49152;                    //out = 0b1100000000000000
        seti 0, 0, $31, 100;                    //ch =0 out = $31 @t = 0
        regwi 0, $31, 0;                        //out = 0b0000000000000000
        seti 0, 0, $31, 110;                    //ch =0 out = $31 @t = 0
        regwi 3, $20, 589844;                   //stdysel | mode | outsel = 0b01001 | length = 20 
        regwi 3, $21, 0;                        //t = 0
        set 7, 3, $16, $17, $18, $19, $20, $21; //ch = 7, out = $16,$18,$19,$20 @t = $21
        synci 20;
        mathi 0, $15, $15, +, 1;
        memwi 0, $15, 1;
        loopnz 0, $14, @LOOP_J;
        end ;

// Program

        regwi 3, $16, 69905067;                 //freq = 100.00000047683716 MHz
        regwi 3, $17, 0;                        //phase = 0
        regwi 3, $19, 1000;                     //gain = 1000
        regwi 3, $21, 0;                        //t = 0
        regwi 3, $20, 589844;                   //stdysel | mode | outsel = 0b01001 | length = 20 
        synci 200;
        regwi 0, $15, 0;
        regwi 0, $14, 99;
LOOP_J: regwi 0, $31, 49152;                    //out = 0b1100000000000000
        seti 0, 0, $31, 100;                    //ch =0 out = $31 @t = 0
        regwi 0, $31, 0;                        //out = 0b0000000000000000
        seti 0, 0, $31, 110;                    //ch =0 out = $31 @t = 0
        regwi 3, $20, 589844;                   //stdysel | mode | outsel = 0b01001 | length = 20 
        regwi 3, $21, 0;                        //t = 0
        set 7, 3, $16, $17, $18, $19, $20, $21; //ch = 7, out = $16,$18,$19,$20 @t = $21
        synci 20;
        mathi 0, $15, $15, +, 1;
        memwi 0, $15, 1;
        loopnz 0, $14, @LOOP_J;
        end ;

// Program

        regwi 3, $16, 69905067;                 //freq = 100.00000047683716 MHz
        regwi 3, $17, 0;                        //phase = 0
        regwi 3, $19, 1000;                     //gain = 1000
        regwi 3, $21, 0;                        //t = 0
        regwi 3, $20, 589844;                   //stdysel | mode | outsel = 0b01001 | length = 20 
        synci 200;
        regwi 0, $15, 0;
        regwi 0, $14, 99;
LOOP_J: regwi 0, $31, 49152;                    //out = 0b1100000000000000
        seti 0, 0, $31, 100;                    //ch =0 out = $31 @t = 0
        regwi 0, $31, 0;                        //out = 0b0000000000000000
        seti 0, 0, $31, 110;                    //ch =0 out = $31 @t = 0
        regwi 3, $20, 589844;                   //stdysel | mode | outsel = 0b01001 | length = 20 
        regwi 3, $21, 0;                        //t = 0
        set 7, 3, $16, $17, $18, $19, $20, $21; //ch = 7, out = $16,$18,$19,$20 @t = $21
        synci 20;
        mathi 0, $15, $15, +, 1;
        memwi 0, $15, 1;
        loopnz 0, $14, @LOOP_J;
        end ;
