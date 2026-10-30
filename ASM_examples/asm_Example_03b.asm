; Program Example_03b:
;Lable		Mnemonic	Arguments
        	MOV 		0x0000,A
        	MOV 		A,[0x0000]
        	MOV 		0xFFF6,B
        	MOV 		B,[0x000B]
RESTO:    	MOV 		0x0001,A
        	MOV 		[0x000B],B
        	UADD 		;A,B=>R
        	JZ16 		END       
        	MOV 		RL,[0x000B]
        	MOV 		[[0x0000]++],A	;[0x0000++]->,A
        	MOV 		0x0000,B
        	UADD 		;A,B=>R
        	JMP  		RESTO
END:   	STOP
