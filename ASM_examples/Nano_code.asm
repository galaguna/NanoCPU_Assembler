 ; commentary
 ORG 0x00
 LAB1:  mov a b
        call SUM
        jmp LAB1    ;other commentary

 ORG 0x20
 SUM:   sadd
        ret