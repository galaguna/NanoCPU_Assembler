; Program Example_02:
;Label		Mnemonic	Arguments
        	MOV 		0xFFF6,B
        	MOV 		0x0001,A
        	MOV 		0x80,USP
STO:    	MOV 		B,[USP]
        	UADD 		;A,B=>R
        	JZ16 		NEXT       
        	MOV 		RL,B
        	INC 		USP
        	JMP 		STO
NEXT:   	MOV 		0x000A,A
RESTO:    	MOV 		[USP],B
        	UADD 		;A,B=>R
        	JZ16 		END       
        	DEC 		USP
        	JMP 		RESTO
END:   	        STOP
