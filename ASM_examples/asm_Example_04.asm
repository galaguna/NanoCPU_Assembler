; Program Example_04:
;Label		Mnemonic	Arguments
			ORG 		0x0000
        	OUT 		0x07,[0x00]
			STOP

			ORG 		0x0010
 ISS0:		NOP
			IN 			[0x01]		; IN=>AL
       		MOV 		0x00FE,B
			AND 		;A,B-> R
			MOV 		RL,A
			OUT 		[0x01]		; AL=> OUT
 			RETI

			ORG 		0x0020
 ISS1:		NOP
			IN 			[0x01]		; IN=>AL
        	MOV 		0x00FD,B
			AND 		;A,B=> R
			MOV 		RL,A
			OUT 		[0x01]		; AL=> OUT
 			RETI

			ORG 		0x0030
 ISS2:		NOP
			IN 			[0x01]		; IN=>AL
        	MOV 		0x00FB,B
			AND 		;A,B=> R
			MOV 		RL,A
			OUT 		[0x01]		; AL=> OUT
 			RETI

			ORG 		0x0FF7
INT2V:		JMP 		ISS2
INT1V:		JMP 		ISS1
INT0V:		JMP 		ISS0
