; Program Example_01:
;Lable		Mnemonic	Arguments
        	ORG 		0x0000
        	MOV 		0x0000,I
        	MOV 		0x000A,N
        	MOV 		0x0001,A
        	MOV 		0x0000,B
TRY:    	CALL 		SUM
			MOV 		RL,B
        	INC 		I
			CMP 		I;N
			JN16 		TRY
        	STOP

        	ORG 		0x0020
SUM:		NOP
 			UADD 		;A,B=>R
 			RET