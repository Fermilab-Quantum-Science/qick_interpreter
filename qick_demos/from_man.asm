	regwi 0, $1, 750; // freq .
	regwi 0, $2, 0; // phase .
	regwi 0, $3, 0; // addr .
	regwi 0, $4, 10000; // gain .
	regwi 0, $5, 1000; // nsamp .
	regwi 0, $6, 0x8; // 0 b1000 .
	bitwi 0, $6, $6 << 12; // left shift register 6 by 12 bits .
	bitw 0, $5, $5 | $6; // r5 = r5 or r6.
	regwi 0, $7, 20; // t = 20.
	regwi 1, $1, 0x1;
	seti 0, 1, $1, 200;
	synci 200;
	regwi 1, $2, 13; // loop counter .
	regwi 0, $10, 0; // memory address index .
LOOP0:	set 1, 0, $1, $2 , $3 , $4 , $5 , $7; // out @t = $7.
	mathi 0, $4, $4, +, 300; // gain = gain + 300.
	memw 0, $4, $10; // mem [ $10 ] = $4
	mathi 0, $10, $10, +, 1; // memory address +1
	loopnz 1, $2, @LOOP0;
	regwi 1, $1, 0x0;
	seti 0, 1, $1, 500;
	end;
