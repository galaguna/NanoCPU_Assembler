##########################################################################################
# Programa ensamblador para el microprocesador Nano-120,
# desarrollado en la Universidad Autónoma Metropolitana.
# Assembler program for the Nano-120 microprocessor,
# developed at the Universidad Autónoma Metropolitana.
##########################################################################################
# Universidad Autónoma Metropolitana, Unidad Lerma
# Programador: Gerardo Laguna
# 28 octubre de 2026
##########################################################################################
import os
import sys
import ply.lex as lex

#Diccionario de palabras reservadas
palabras_reservadas = {
    'org': 'ORIGEN',
    'a'  : 'REG_A',
    'al' : 'REG_AL',
    'b'  : 'REG_B',
    'bl' : 'REG_BL',
    'i'  : 'REG_I',
    'j'  : 'REG_J',
    'n'  : 'REG_N',
    'm'  : 'REG_M',
    'r' : 'REG_R',
    'rl' : 'REG_RL',
    'rh' : 'REG_RH',
    'acc': 'REG_ACC',
    'accl': 'REG_ACCL',
    'acch': 'REG_ACCH',
    'sp' : 'REG_SP',
    'usp': 'REG_USP',
    'nop': 'OP_NOP',
    'jmp'  : 'OP_JMP',
    'jz16' : 'OP_JZ16',
    'jn16' : 'OP_JN16',
    'jo16' : 'OP_JO16',
    'jco16': 'OP_JCO16',
    'jz32' : 'OP_JZ32',
    'jn32' : 'OP_JN32',
    'jo32' : 'OP_JO32',
    'jco32': 'OP_JCO32',
    'jnz16': 'OP_JNZ16',
    'jp16' : 'OP_JP16',
    'jno16': 'OP_JNO16',
    'jnco16': 'OP_NCO16',
    'jnz32' : 'OP_JNZ32',
    'jp32'  : 'OP_JP32',
    'jno32' : 'OP_JNO32',
    'jnco32': 'OP_JNCO32',
	'call' : 'OP_CALL',
    'ret' : 'OP_RET',
    'reti' : 'OP_RETI',
    'push' : 'OP_PUSH',
    'pop' : 'OP_POP',
    'mov' : 'OP_MOV',
    'uadd' : 'OP_UADD',
    'sadd' : 'OP_SADD',
    'cum' : 'OP_CUM',
    'umul' : 'OP_UMUL',
	'smul' : 'OP_SMUL',
    'umac' : 'OP_UMAC',
    'smac' : 'OP_SMAC',
    'sr' : 'OP_SR',
    'sra' : 'OP_SRA',
    'sl' : 'OP_SL',
    'not' : 'OP_NOT',
    'and' : 'OP_AND',
    'or' : 'OP_OR',
    'xor' : 'OP_XOR',
	'inc' : 'OP_INC',
    'dec' : 'OP_DEC',
    'cmp' : 'OP_CMP',
    'incmp' : 'OP_INCMP',
    'decmp' : 'OP_DECMP',
    'out' : 'OP_OUT',
    'in' : 'OP_IN',
    'stop' : 'OP_STOP'
}
#Lista de tokens:
tokens=('TERMINADOR',
        'ETIQUETA',
        'DECIMAL',
        'HEXADECIMAL',
        'ABRE_CORCH',
        'CIERRA_CORCH',
        'GUION',
        'MAYOR_QUE',
        'MAS')+ tuple(palabras_reservadas.values())

#Definición de tokens simples:
t_ABRE_CORCH = r'\['
t_CIERRA_CORCH = r'\]'
t_GUION = r'\-'
t_MAYOR_QUE = r'>'
t_MAS = r'\+'

##########################################################################################
#PLY (Python Lex-Yacc) evalua las reglas definidas como funciones en su orden de aparición
##########################################################################################

def t_TERMINADOR(t):
    r'[;\n\r]'  #El token 'TERMINADOR' puede ser ';', 'LF' o 'CR'

    if t.value in '\n\r': #Si el caracter es 'LF' o 'CR'
        t.lexer.lineno += 1 #Incrementa el contador de números del lexer.

    return t

def t_ETIQUETA(t):
    #Regla con expresión regular para token etiqueta
    #r'[a-zA-Z][a-zA-Z0-9_]*'
    #   - Inicia con letra (minúscula o mayúscula)
    #   - Termina una cadena compuesta por números y
    #     letras en el intervalo [A:F] (minúscula o mayúscula)
    #     incluyendo el guion bajo.
    r'[a-zA-Z][a-zA-Z0-9_]*'

    #Prevision para garantizar insensbilidad ante mayúsculas y inusculas:
    lower_key=t.value.lower() #Valor (i.e. cadena) a minúsculas
    #Verificamos si la cadena del token es una palabra reservada:
    if lower_key in palabras_reservadas:
        t.type = palabras_reservadas[lower_key]

    return t

#Primero se define el token hexadecimal para capturar antes que nadie el prefijo '0x'
def t_HEXADECIMAL(t):
    #Regla con expresión regular para token hexadecimal
    #r'0[xX][0-9a-fA-F]+'
    #   - Inicia con 0
    #   - Le sigue x (minúscula o mayúscula)
    #   - Finalmente una cadena compuesta por números y
    #     letras en el intervalo [A:F] (minúscula o mayúscula)
    r'0[xX][0-9a-fA-F]+'
    t.value= int(t.value,16)
    return t

#Luego se define el token decimal que tambien puede comenzar con '0'
def t_DECIMAL(t):
    #Regla con expresión regular para token decimal
    r'\d+'
    t.value= int(t.value)
    return t

#Caracteres que se ignoran:
#espacio, tabulador, coma, punto, dos puntos.
t_ignore = ' \t,.:'

def t_error(t):
    print(f'Caracter ilegal:{t.value[0]} en número {t.lineno}, columna {t.lexpos+1}')
    sys.exit()


#Construye el lexer
lexer = lex.lex()

##########################################################################################
#Variables globales:
##########################################################################################
Lista_codigo_maquina = []
block_org=0
block_org_ix=-1 #De entrada, un índice no válido, en espera de que se use almenos una primitiva ORG.
Tabla_etiquetas = {}
ProgramCounter = 0

# Diccionario de OP codes:
OP_code = {
    'OP_NOP': 0x00,
    'OP_JMP': 0x01,
    'OP_JZ16': 0x02,
    'OP_JN16': 0x03,
    'OP_JO16': 0x04,
    'OP_JCO16': 0x05,
    'OP_JZ32': 0x06,
    'OP_JN32': 0x07,
    'OP_JO32': 0x08,
    'OP_JCO32': 0x09,
    'OP_JNZ16': 0x0A,
    'OP_JP16': 0x0B,
    'OP_JNO16': 0x0C,
    'OP_NCO16': 0x0D,
    'OP_JNZ32': 0x0E,
    'OP_JP32': 0x0F,
    'OP_JNO32': 0x10,
    'OP_JNCO32': 0x11,
	'OP_CALL': 0x12,
    'OP_RET': 0x13,
    'OP_RETI': 0x14,
    'OP_PUSHA': 0x15,
    'OP_PUSHB': 0x16,
    'OP_PUSHI': 0x17,
    'OP_PUSHJ': 0x18,
    'OP_PUSHN': 0x19,
    'OP_PUSHM': 0x1A,
    'OP_POPA': 0x1B,
    'OP_POPB': 0x1C,
    'OP_POPI': 0x1D,
    'OP_POPJ': 0x1E,
    'OP_POPN': 0x1F,
    'OP_POPM': 0x20,
    'OP_MOVBA': 0x21,
    'OP_MOVIRA': 0x22,
    'OP_MOVJRA': 0x23,
    'OP_MOVRLA': 0x24,
    'OP_MOVRHA': 0x25,
    'OP_MOVAB': 0x26,
    'OP_MOVRLB': 0x27,
    'OP_MOVRHB': 0x28,
    'OP_MOVRACC': 0x29,
    'OP_MOVAACCL': 0x2A,
    'OP_MOVBACCL': 0x2B,
    'OP_MOVAACCH': 0x2C,
    'OP_MOVBACCH': 0x2D,
    'OP_MOVACCLA': 0x2E,
    'OP_MOVACCLB': 0x2F,
    'OP_MOVACCHA': 0x30,
    'OP_MOVACCHB': 0x31,
    'OP_STOSPA': 0x32,
    'OP_STOSPB': 0x33,
    'OP_STOUSPA': 0x34,
    'OP_STOUSPB': 0x35,
    'OP_LDUSP': 0x36,
    'OP_LDUSPA': 0x37,
    'OP_LDUSPB': 0x38,
    'OP_LDUSPR': 0x39,
    'OP_LDUSPK': 0x3A,
    'OP_MOVKA': 0x3B,
    'OP_MOVKB': 0x3C,
    'OP_MOVKI': 0x3D,
    'OP_MOVKJ': 0x3E,
    'OP_MOVKN': 0x3F,
    'OP_MOVKM': 0x40,
    'OP_MOVAM': 0x41,
    'OP_MOVBM': 0x42,
    'OP_MOVRLM': 0x43,
    'OP_MOVRHM': 0x44,
    'OP_MOVMA': 0x45,
    'OP_MOVMB': 0x46,
    'OP_MOVAI': 0x47,
    'OP_MOVBI': 0x48,
    'OP_MOVRLI': 0x49,
    'OP_MOVRHI': 0x4A,
    'OP_MOVIA': 0x4B,
    'OP_MOVIB': 0x4C,
    'OP_MOVAIPP': 0x4D,
    'OP_MOVBIPP': 0x4E,
    'OP_MOVRLIPP': 0x4F,
    'OP_MOVRHIPP': 0x50,
    'OP_MOVIPPA': 0x51,
    'OP_MOVIPPB': 0x52,
    'OP_MOVMMIA': 0x53,
    'OP_MOVMMIB': 0x54,
    'OP_MOVAS': 0x55,
    'OP_MOVBS': 0x56,
    'OP_MOVRLS': 0x57,
    'OP_MOVRHS': 0x58,
    'OP_MOVSA': 0x59,
    'OP_MOVSB': 0x5A,
    'OP_UADD': 0x5B,
    'OP_SADD': 0x5C,
    'OP_CUM': 0x5D,
    'OP_UMUL': 0x5E,
	'OP_SMUL': 0x5F,
    'OP_UMAC': 0x60,
    'OP_SMAC': 0x61,
    'OP_SR': 0x62,
    'OP_SRA': 0x63,
    'OP_SL': 0x64,
    'OP_NOTA': 0x65,
    'OP_NOTB': 0x66,
    'OP_AND': 0x67,
    'OP_OR': 0x68,
    'OP_XOR': 0x69,
	'OP_INCUSP': 0x6A,
    'OP_INCIR': 0x6B,
	'OP_INCJR': 0x6C,
    'OP_DECUSP': 0x6D,
    'OP_DECIR': 0x6E,
    'OP_DECJR': 0x6F,
    'OP_CMPIN': 0x70,
    'OP_CMPJM': 0x71,
    'OP_INCMP': 0x72,
    'OP_DECMP': 0x73,
    'OP_OUTA': 0x74,
    'OP_INA': 0x75,
    'OP_OUTK': 0x76,
    'OP_STOP': 0xFF
}

#Lista de instrucciones que no requieren argumento:
OP_X_NOARG=(
    'OP_NOP',
    'OP_RET',
    'OP_RETI',
    'OP_UADD',
    'OP_SADD',
    'OP_CUM',
    'OP_UMUL',
	'OP_SMUL',
    'OP_UMAC',
    'OP_SMAC',
    'OP_SR',
    'OP_SRA',
    'OP_SL',
    'OP_AND',
    'OP_OR',
    'OP_XOR',
    'OP_STOP'
)

#Lista de instrucciones que requieren un argumento con la dirección destino:
OP_X_ADD=(
    'OP_JMP',
    'OP_JZ16',
    'OP_JN16',
    'OP_JO16',
    'OP_JCO16',
    'OP_JZ32',
    'OP_JN32',
    'OP_JO32',
    'OP_JCO32',
    'OP_JNZ16',
    'OP_JP16',
    'OP_JNO16',
    'OP_NCO16',
    'OP_JNZ32',
    'OP_JP32',
    'OP_JNO32',
    'OP_JNCO32',
	'OP_CALL'
)

##########################################################################################
#Análisis léxico-sintáctico
##########################################################################################

def next_token():
    ntok = lexer.token()
    #Depuración:
    #print(ntok)  # Imprime tipo (type), valor (value) del token, línea y columna.
    return ntok

def syntax_ana_ETIQUETA(lab):
    if lab.value not in Tabla_etiquetas:
        Tabla_etiquetas[lab.value] = ProgramCounter
    else:
        print(f'¡¡¡Error en número {lab.lineno}, columna {lab.lexpos+1}: Etiqueta definida previamente!!!\n')
        sys.exit()

def syntax_ana_4ORIGEN():
    global ProgramCounter, block_org, block_org_ix
    tok = next_token()
    if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
        block_size= ProgramCounter - block_org
        if block_org_ix >= 0: #Si ya se empleó la primitica ORG
            Lista_codigo_maquina[block_org_ix] = Lista_codigo_maquina[block_org_ix] + ' (SIZE ' + str(block_size) + ')'
        ProgramCounter = tok.value
        block_org=ProgramCounter
        block_org_ix=len(Lista_codigo_maquina)
        Lista_codigo_maquina.append('ORG 0x' + '{:04X}'.format(tok.value))

    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Primitiva ORG sin argumento válido!!!\n')
        sys.exit()

def ensambla_OP_X_NOARG(op_key):
    global ProgramCounter
    Lista_codigo_maquina.append('0x'+'{:02X}'.format(OP_code[op_key]))
    ProgramCounter+=1

def ensambla_OP_X_ADD(op_key):
    global ProgramCounter
    tok = next_token()
    if tok.type == 'ETIQUETA' or tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
        ProgramCounter += 1
        if tok.type == 'ETIQUETA':
            Lista_codigo_maquina.append(tok.value)
            ProgramCounter += 1
            Lista_codigo_maquina.append(tok.value)
            ProgramCounter += 1
        else: #El argumento de dirección destino se specifica numéricamente:
            ADDH= (tok.value >> 8)& 0xFF
            Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
            ProgramCounter += 1
            ADDL=tok.value & 0xFF
            Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
            ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento destino válido (etiqueta o dirección)!!!\n')
        sys.exit()

def ensambla_OP_PUSH_X():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_A':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_PUSHA']))
        ProgramCounter += 1
    elif tok.type == 'REG_B':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_PUSHB']))
        ProgramCounter += 1
    elif tok.type == 'REG_I':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_PUSHI']))
        ProgramCounter += 1
    elif tok.type == 'REG_J':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_PUSHJ']))
        ProgramCounter += 1
    elif tok.type == 'REG_N':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_PUSHN']))
        ProgramCounter += 1
    elif tok.type == 'REG_M':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_PUSHM']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento válido para instrucción PUSH!!!\n')
        sys.exit()

def ensambla_OP_POP_X():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_A':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_POPA']))
        ProgramCounter += 1
    elif tok.type == 'REG_B':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_POPB']))
        ProgramCounter += 1
    elif tok.type == 'REG_I':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_POPI']))
        ProgramCounter += 1
    elif tok.type == 'REG_J':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_POPJ']))
        ProgramCounter += 1
    elif tok.type == 'REG_N':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_POPN']))
        ProgramCounter += 1
    elif tok.type == 'REG_M':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_POPM']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento válido para instrucción POP!!!\n')
        sys.exit()

def ensambla_OP_NOT_X():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_A':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_NOTA']))
        ProgramCounter += 1
    elif tok.type == 'REG_B':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_NOTB']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento válido para instrucción NOT!!!\n')
        sys.exit()

def ensambla_OP_INC_X():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_USP':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_INCUSP']))
        ProgramCounter += 1
    elif tok.type == 'REG_I':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_INCIR']))
        ProgramCounter += 1
    elif tok.type == 'REG_J':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_INCJR']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento válido para instrucción INC!!!\n')
        sys.exit()

def ensambla_OP_DEC_X():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_USP':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_DECUSP']))
        ProgramCounter += 1
    elif tok.type == 'REG_I':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_DECIR']))
        ProgramCounter += 1
    elif tok.type == 'REG_J':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_DECJR']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento válido para instrucción DEC!!!\n')
        sys.exit()

def ensambla_OP_CMP_X():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_I':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_CMPIN']))
        ProgramCounter += 1
    elif tok.type == 'REG_J':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_CMPJM']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento válido para instrucción CMP!!!\n')
        sys.exit()

def ensambla_OP_XCMP(op_key):
    global ProgramCounter
    tok = next_token()
    if tok.type == 'ABRE_CORCH':
        tok = next_token()
        if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
            ADDH= (tok.value >> 8)& 0xFF
            ADDL=tok.value & 0xFF
            tok = next_token()
            if tok.type == 'CIERRA_CORCH':
                Lista_codigo_maquina.append('0x'+'{:02X}'.format(OP_code[op_key]))
                ProgramCounter+=1
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
                ProgramCounter += 1
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
                ProgramCounter += 1
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta corchete de cierre!!!\n')
                sys.exit()
        else:
            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta índice numérico (ix) de localidad de memoria!!!\n')
            sys.exit()
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento con localidad de memoria válido ([ix])!!!\n')
        sys.exit()

def ensambla_OP_INA():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'ABRE_CORCH':
        tok = next_token()
        if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
            ADD=tok.value & 0xFF
            tok = next_token()
            if tok.type == 'CIERRA_CORCH':
                Lista_codigo_maquina.append('0x'+'{:02X}'.format(OP_code['OP_INA']))
                ProgramCounter+=1
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADD))
                ProgramCounter += 1
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta corchete de cierre!!!\n')
                sys.exit()
        else:
            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta índice numérico (ix) de localidad de entrada!!!\n')
            sys.exit()
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento con localidad de entrada válido ([ix])!!!\n')
        sys.exit()

def ensambla_OP_OUT_X():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'ABRE_CORCH' or tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
        if tok.type == 'ABRE_CORCH':
            tok = next_token()
            if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
                ADD=tok.value & 0xFF
                tok = next_token()
                if tok.type == 'CIERRA_CORCH':
                    Lista_codigo_maquina.append('0x'+'{:02X}'.format(OP_code['OP_OUTA']))
                    ProgramCounter+=1
                    Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADD))
                    ProgramCounter += 1
                else:
                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta corchete de cierre!!!\n')
                    sys.exit()
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta índice numérico (ix) de localidad de salida!!!\n')
                sys.exit()
        else:
            K = tok.value & 0xFF
            tok = next_token()
            if tok.type == 'ABRE_CORCH':
                tok = next_token()
                if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
                    ADD = tok.value & 0xFF
                    tok = next_token()
                    if tok.type == 'CIERRA_CORCH':
                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_OUTK']))
                        ProgramCounter += 1
                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(K))
                        ProgramCounter += 1
                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADD))
                        ProgramCounter += 1
                    else:
                        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta corchete de cierre!!!\n')
                        sys.exit()
                else:
                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta índice numérico (ix) de localidad de salida!!!\n')
                    sys.exit()
            else:
                print(
                    f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento destino válido para la salida ([ix])!!!\n')
                sys.exit()
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Faltan argumentos de salida válidos (k,[ix] o [ix])!!!\n')
        sys.exit()

def ensambla_OP_MOV_AX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_B':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVAB']))
        ProgramCounter += 1
    elif tok.type == 'REG_ACCL':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVAACCL']))
        ProgramCounter += 1
    elif tok.type == 'REG_ACCH':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVAACCH']))
        ProgramCounter += 1
    elif tok.type == 'ABRE_CORCH':
        tok = next_token()
        if tok.type == 'ABRE_CORCH':
            tok = next_token()
            if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
                ADDH = (tok.value >> 8) & 0xFF
                ADDL = tok.value & 0xFF
                tok = next_token()
                if tok.type == 'CIERRA_CORCH':
                    tok = next_token()
                    if tok.type in ('CIERRA_CORCH', 'MAS'):
                        if tok.type == 'CIERRA_CORCH':
                            op_key = 'OP_MOVAI'
                        else: #tok.type == 'MAS':
                            tok = next_token()
                            if tok.type == 'MAS':
                                tok = next_token()
                                if tok.type == 'CIERRA_CORCH':
                                    op_key = 'OP_MOVAIPP'
                                else:
                                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                                    sys.exit()
                            else:
                                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter +!!!\n')
                                sys.exit()

                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
                        ProgramCounter += 1
                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
                        ProgramCounter += 1
                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
                        ProgramCounter += 1
                    else:
                        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ] u operador +!!!\n')
                        sys.exit()
                else:
                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                    sys.exit()
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera un valor numérico como índice!!!\n')
                sys.exit()

        elif tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
            ADDH= (tok.value >> 8)& 0xFF
            ADDL=tok.value & 0xFF
            tok = next_token()
            if tok.type in ('CIERRA_CORCH', 'MAS'):
                if tok.type == 'CIERRA_CORCH':
                    tok = next_token()
                    if tok.type == 'GUION':
                        tok = next_token()
                        if tok.type == 'MAYOR_QUE':
                            op_key = 'OP_MOVAI'
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter >!!!\n')
                            sys.exit()
                    else:
                        op_key='OP_MOVAM'
                else: #tok.type == 'MAS':
                    tok = next_token()
                    if tok.type == 'MAS':
                        tok = next_token()
                        if tok.type == 'CIERRA_CORCH':
                            tok = next_token()
                            if tok.type == 'GUION':
                                tok = next_token()
                                if tok.type == 'MAYOR_QUE':
                                    op_key = 'OP_MOVAIPP'
                                else:
                                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter >!!!\n')
                                    sys.exit()
                            else:
                                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter -!!!\n')
                                sys.exit()
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                            sys.exit()
                    else:
                        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter +!!!\n')
                        sys.exit()

                Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
                ProgramCounter += 1
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
                ProgramCounter += 1
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
                ProgramCounter += 1
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta corchete de cierre!!!\n')
                sys.exit()
        elif tok.type == 'REG_USP':
            tok = next_token()
            if tok.type == 'CIERRA_CORCH':
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVAS']))
                ProgramCounter += 1
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta corchete de cierre!!!\n')
                sys.exit()
        else:
            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta índice numérico (ix) o apuntador USP para localidad destino en memoria!!!\n')
            sys.exit()
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento válido para instrucción MOV!!!\n')
        sys.exit()

def ensambla_OP_MOV_ALX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_USP':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_LDUSPA']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Sólo se acepta al registro USP como destino en la instrucción MOV AL (LDUSPA)!!!\n')
        sys.exit()

def ensambla_OP_MOV_BX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_A':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVBA']))
        ProgramCounter += 1
    elif tok.type == 'REG_ACCL':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVBACCL']))
        ProgramCounter += 1
    elif tok.type == 'REG_ACCH':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVBACCH']))
        ProgramCounter += 1
    elif tok.type == 'ABRE_CORCH':
        tok = next_token()
        if tok.type == 'ABRE_CORCH':
            tok = next_token()
            if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
                ADDH = (tok.value >> 8) & 0xFF
                ADDL = tok.value & 0xFF
                tok = next_token()
                if tok.type == 'CIERRA_CORCH':
                    tok = next_token()
                    if tok.type in ('CIERRA_CORCH', 'MAS'):
                        if tok.type == 'CIERRA_CORCH':
                            op_key = 'OP_MOVBI'
                        else: #tok.type == 'MAS':
                            tok = next_token()
                            if tok.type == 'MAS':
                                tok = next_token()
                                if tok.type == 'CIERRA_CORCH':
                                    op_key = 'OP_MOVBIPP'
                                else:
                                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                                    sys.exit()
                            else:
                                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter +!!!\n')
                                sys.exit()

                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
                        ProgramCounter += 1
                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
                        ProgramCounter += 1
                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
                        ProgramCounter += 1
                    else:
                        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ] u operador +!!!\n')
                        sys.exit()
                else:
                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                    sys.exit()
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera un valor numérico como índice!!!\n')
                sys.exit()

        elif tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
            ADDH= (tok.value >> 8)& 0xFF
            ADDL=tok.value & 0xFF
            tok = next_token()
            if tok.type in ('CIERRA_CORCH', 'MAS'):
                if tok.type == 'CIERRA_CORCH':
                    tok = next_token()
                    if tok.type == 'GUION':
                        tok = next_token()
                        if tok.type == 'MAYOR_QUE':
                            op_key = 'OP_MOVBI'
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter >!!!\n')
                            sys.exit()
                    else:
                        op_key='OP_MOVBM'
                else:  # tok.type == 'MAS':
                    tok = next_token()
                    if tok.type == 'MAS':
                        tok = next_token()
                        if tok.type == 'CIERRA_CORCH':
                            tok = next_token()
                            if tok.type == 'GUION':
                                tok = next_token()
                                if tok.type == 'MAYOR_QUE':
                                    op_key = 'OP_MOVBIPP'
                                else:
                                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter >!!!\n')
                                    sys.exit()
                            else:
                                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter -!!!\n')
                                sys.exit()
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                            sys.exit()
                    else:
                        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter +!!!\n')
                        sys.exit()

                Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
                ProgramCounter += 1
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
                ProgramCounter += 1
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
                ProgramCounter += 1
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta corchete de cierre!!!\n')
                sys.exit()
        elif tok.type == 'REG_USP':
            tok = next_token()
            if tok.type == 'CIERRA_CORCH':
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVBS']))
                ProgramCounter += 1
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta corchete de cierre!!!\n')
                sys.exit()
        else:
            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta índice numérico (ix) o apuntador USP para localidad destino en memoria!!!\n')
            sys.exit()
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento válido para instrucción MOV!!!\n')
        sys.exit()


def ensambla_OP_MOV_BLX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_USP':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_LDUSPB']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Sólo se acepta al registro USP como destino en la instrucción MOV BL (LDUSPB)!!!\n')
        sys.exit()

def ensambla_OP_MOV_RX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_ACC':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVRACC']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Sólo se acepta al registro ACC como destino en la instrucción MOV R!!!\n')
        sys.exit()

def ensambla_OP_MOV_RLX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_A':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVRLA']))
        ProgramCounter += 1
    elif tok.type == 'REG_B':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVRLB']))
        ProgramCounter += 1
    elif tok.type == 'REG_USP':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_LDUSPR']))
        ProgramCounter += 1
    elif tok.type == 'ABRE_CORCH':
        tok = next_token()
        if tok.type == 'ABRE_CORCH':
            tok = next_token()
            if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
                ADDH = (tok.value >> 8) & 0xFF
                ADDL = tok.value & 0xFF
                tok = next_token()
                if tok.type == 'CIERRA_CORCH':
                    tok = next_token()
                    if tok.type in ('CIERRA_CORCH', 'MAS'):
                        if tok.type == 'CIERRA_CORCH':
                            op_key = 'OP_MOVRLI'
                        else: #tok.type == 'MAS':
                            tok = next_token()
                            if tok.type == 'MAS':
                                tok = next_token()
                                if tok.type == 'CIERRA_CORCH':
                                    op_key = 'OP_MOVRLIPP'
                                else:
                                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                                    sys.exit()
                            else:
                                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter +!!!\n')
                                sys.exit()

                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
                        ProgramCounter += 1
                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
                        ProgramCounter += 1
                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
                        ProgramCounter += 1
                    else:
                        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ] u operador +!!!\n')
                        sys.exit()
                else:
                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                    sys.exit()
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera un valor numérico como índice!!!\n')
                sys.exit()

        elif tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
            ADDH= (tok.value >> 8)& 0xFF
            ADDL=tok.value & 0xFF
            tok = next_token()
            if tok.type in ('CIERRA_CORCH', 'MAS'):
                if tok.type == 'CIERRA_CORCH':
                    tok = next_token()
                    if tok.type == 'GUION':
                        tok = next_token()
                        if tok.type == 'MAYOR_QUE':
                            op_key = 'OP_MOVRLI'
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter >!!!\n')
                            sys.exit()
                    else:
                        op_key='OP_MOVRLM'
                else:  # tok.type == 'MAS':
                    tok = next_token()
                    if tok.type == 'MAS':
                        tok = next_token()
                        if tok.type == 'CIERRA_CORCH':
                            tok = next_token()
                            if tok.type == 'GUION':
                                tok = next_token()
                                if tok.type == 'MAYOR_QUE':
                                    op_key = 'OP_MOVRLIPP'
                                else:
                                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter >!!!\n')
                                    sys.exit()
                            else:
                                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter -!!!\n')
                                sys.exit()
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                            sys.exit()
                    else:
                        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter +!!!\n')
                        sys.exit()

                Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
                ProgramCounter += 1
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
                ProgramCounter += 1
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
                ProgramCounter += 1
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta corchete de cierre!!!\n')
                sys.exit()
        elif tok.type == 'REG_USP':
            tok = next_token()
            if tok.type == 'CIERRA_CORCH':
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVRLS']))
                ProgramCounter += 1
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta corchete de cierre!!!\n')
                sys.exit()
        else:
            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta índice numérico (ix) o apuntador USP para localidad destino en memoria!!!\n')
            sys.exit()
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento válido para instrucción MOV!!!\n')
        sys.exit()


def ensambla_OP_MOV_RHX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_A':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVRHA']))
        ProgramCounter += 1
    elif tok.type == 'REG_B':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVRHB']))
        ProgramCounter += 1
    elif tok.type == 'ABRE_CORCH':
        tok = next_token()
        if tok.type == 'ABRE_CORCH':
            tok = next_token()
            if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
                ADDH = (tok.value >> 8) & 0xFF
                ADDL = tok.value & 0xFF
                tok = next_token()
                if tok.type == 'CIERRA_CORCH':
                    tok = next_token()
                    if tok.type in ('CIERRA_CORCH', 'MAS'):
                        if tok.type == 'CIERRA_CORCH':
                            op_key = 'OP_MOVRHI'
                        else: #tok.type == 'MAS':
                            tok = next_token()
                            if tok.type == 'MAS':
                                tok = next_token()
                                if tok.type == 'CIERRA_CORCH':
                                    op_key = 'OP_MOVRHIPP'
                                else:
                                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                                    sys.exit()
                            else:
                                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter +!!!\n')
                                sys.exit()

                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
                        ProgramCounter += 1
                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
                        ProgramCounter += 1
                        Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
                        ProgramCounter += 1
                    else:
                        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ] u operador +!!!\n')
                        sys.exit()
                else:
                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                    sys.exit()
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera un valor numérico como índice!!!\n')
                sys.exit()


        elif tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
            ADDH= (tok.value >> 8)& 0xFF
            ADDL=tok.value & 0xFF
            tok = next_token()
            if tok.type in ('CIERRA_CORCH', 'MAS'):
                if tok.type == 'CIERRA_CORCH':
                    tok = next_token()
                    if tok.type == 'GUION':
                        tok = next_token()
                        if tok.type == 'MAYOR_QUE':
                            op_key = 'OP_MOVRHI'
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter >!!!\n')
                            sys.exit()
                    else:
                        op_key='OP_MOVRHM'
                else:  # tok.type == 'MAS':
                    tok = next_token()
                    if tok.type == 'MAS':
                        tok = next_token()
                        if tok.type == 'CIERRA_CORCH':
                            tok = next_token()
                            if tok.type == 'GUION':
                                tok = next_token()
                                if tok.type == 'MAYOR_QUE':
                                    op_key = 'OP_MOVRHIPP'
                                else:
                                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter >!!!\n')
                                    sys.exit()
                            else:
                                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter -!!!\n')
                                sys.exit()
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                            sys.exit()
                    else:
                        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter +!!!\n')
                        sys.exit()

                Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
                ProgramCounter += 1
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
                ProgramCounter += 1
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
                ProgramCounter += 1
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta corchete de cierre!!!\n')
                sys.exit()
        elif tok.type == 'REG_USP':
            tok = next_token()
            if tok.type == 'CIERRA_CORCH':
                Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVRHS']))
                ProgramCounter += 1
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta corchete de cierre!!!\n')
                sys.exit()
        else:
            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta índice numérico (ix) o apuntador USP para localidad destino en memoria!!!\n')
            sys.exit()
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta argumento válido para instrucción MOV!!!\n')
        sys.exit()


def ensambla_OP_MOV_ACCLX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_A':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVACCLA']))
        ProgramCounter += 1
    elif tok.type == 'REG_B':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVACCLB']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Sólo se acepta a los registros A y B como destino en la instrucción MOV ACCL!!!\n')
        sys.exit()

def ensambla_OP_MOV_ACCHX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_A':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVACCHA']))
        ProgramCounter += 1
    elif tok.type == 'REG_B':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVACCHB']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Sólo se acepta a los registros A y B como destinos en la instrucción MOV ACCH!!!\n')
        sys.exit()

def ensambla_OP_MOV_IX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_A':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVIRA']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Sólo se acepta al registro A como destino en la instrucción MOV I!!!\n')
        sys.exit()

def ensambla_OP_MOV_JX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_A':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVJRA']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Sólo se acepta al registro A como destino en la instrucción MOV J!!!\n')
        sys.exit()

def ensambla_OP_MOV_KX(value):
    global ProgramCounter
    KH = (value >> 8) & 0xFF
    KL = value & 0xFF

    tok = next_token()
    if tok.type == 'REG_USP':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_LDUSPK']))
        ProgramCounter += 1
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(KL))
        ProgramCounter += 1
    elif tok.type in ('REG_A', 'REG_B', 'REG_I', 'REG_J', 'REG_N', 'REG_M'):
        if tok.type == 'REG_A':
            op_key= 'OP_MOVKA'
        elif tok.type == 'REG_B':
            op_key= 'OP_MOVKB'
        elif tok.type == 'REG_I':
            op_key= 'OP_MOVKI'
        elif tok.type == 'REG_J':
            op_key= 'OP_MOVKJ'
        elif tok.type == 'REG_N':
            op_key= 'OP_MOVKN'
        else:# tok.type == 'REG_M':
            op_key= 'OP_MOVKM'

        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
        ProgramCounter += 1
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(KH))
        ProgramCounter += 1
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(KL))
        ProgramCounter += 1

    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Falta registro destino válido para instrucción MOV K!!!\n')
        sys.exit()

def ensambla_OP_MOV_SPX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_USP':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_LDUSP']))
        ProgramCounter += 1
    elif tok.type == 'REG_A':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_STOSPA']))
        ProgramCounter += 1
    elif tok.type == 'REG_B':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_STOSPB']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Sólo se acepta a los registros A, B y USP como destinos en la instrucción MOV SP (Respectivamente, STOSPA, STOSPB y LDUSP)!!!\n')
        sys.exit()

def ensambla_OP_MOV_USPX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'REG_A':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_STOUSPA']))
        ProgramCounter += 1
    elif tok.type == 'REG_B':
        Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_STOUSPB']))
        ProgramCounter += 1
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Sólo se acepta a los registros A y B como destinos en la instrucción MOV USP (Respectivamente, STOUSPA y STOUSPB !!!\n')
        sys.exit()

def ensambla_OP_MOV_CORCHX():
    global ProgramCounter
    tok = next_token()
    if tok.type == 'ABRE_CORCH':
        tok = next_token()
        if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
            ADDH = (tok.value >> 8) & 0xFF
            ADDL = tok.value & 0xFF
            tok = next_token()
            if tok.type == 'CIERRA_CORCH':
                tok = next_token()
                if tok.type in ('CIERRA_CORCH', 'MAS'):
                    if tok.type == 'CIERRA_CORCH':
                        tok = next_token()
                        if tok.type == 'REG_A':
                            op_key = 'OP_MOVIA'
                        elif tok.type == 'REG_B':
                            op_key = 'OP_MOVIB'
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Argumento de destino inválido para MOV!!!\n')
                            sys.exit()

                    else: #tok.type == 'MAS':
                        tok = next_token()
                        if tok.type == 'MAS':
                            tok = next_token()
                            if tok.type == 'CIERRA_CORCH':
                                tok = next_token()
                                if tok.type == 'REG_A':
                                    op_key = 'OP_MOVIPPA'
                                elif tok.type == 'REG_B':
                                    op_key = 'OP_MOVIPPB'
                                else:
                                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Argumento de destino inválido para MOV!!!\n')
                                    sys.exit()


                            else:
                                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                                sys.exit()
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter +!!!\n')
                            sys.exit()

                    Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
                    ProgramCounter += 1
                    Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
                    ProgramCounter += 1
                    Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
                    ProgramCounter += 1
                else:
                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ] u operador +!!!\n')
                    sys.exit()
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                sys.exit()
        else:
            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera un valor numérico como índice!!!\n')
            sys.exit()

    elif tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
        ADDH = (tok.value >> 8) & 0xFF
        ADDL = tok.value & 0xFF
        tok = next_token()
        if tok.type in ('CIERRA_CORCH', 'MAS'):
            if tok.type == 'CIERRA_CORCH':
                tok = next_token()
                if tok.type == 'GUION':
                    tok = next_token()
                    if tok.type == 'MAYOR_QUE':
                        tok = next_token()
                        if tok.type == 'REG_A':
                            op_key = 'OP_MOVIA'
                        elif tok.type == 'REG_B':
                            op_key = 'OP_MOVIB'
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Argumento de destino inválido para MOV!!!\n')
                            sys.exit()
                    else:
                        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter >!!!\n')
                        sys.exit()

                elif tok.type == 'REG_A':
                    op_key = 'OP_MOVMA'
                elif tok.type == 'REG_B':
                    op_key = 'OP_MOVMB'
                else:
                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Argumento de destino inválido para MOV!!!\n')
                    sys.exit()
            else:  # tok.type == 'MAS':
                tok = next_token()
                if tok.type == 'MAS':
                    tok = next_token()
                    if tok.type == 'CIERRA_CORCH':
                        tok = next_token()
                        if tok.type == 'GUION':
                            tok = next_token()
                            if tok.type == 'MAYOR_QUE':
                                tok = next_token()
                                if tok.type == 'REG_A':
                                    op_key = 'OP_MOVIPPA'
                                elif tok.type == 'REG_B':
                                    op_key = 'OP_MOVIPPB'
                                else:
                                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Argumento de destino inválido para MOV!!!\n')
                                    sys.exit()
                            else:
                                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter >!!!\n')
                                sys.exit()
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter -!!!\n')
                            sys.exit()
                    else:
                        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                        sys.exit()
                else:
                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter +!!!\n')
                    sys.exit()

            Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
            ProgramCounter += 1
            Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
            ProgramCounter += 1
            Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
            ProgramCounter += 1
        else:
            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Falta corchete de cierre!!!\n')
            sys.exit()
    elif tok.type == 'GUION':
        tok = next_token()
        if tok.type == 'GUION':
            tok = next_token()
            if tok.type == 'ABRE_CORCH':
                tok = next_token()
                if tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
                    ADDH = (tok.value >> 8) & 0xFF
                    ADDL = tok.value & 0xFF
                    tok = next_token()
                    if tok.type == 'CIERRA_CORCH':
                        tok = next_token()
                        if tok.type == 'CIERRA_CORCH':
                            tok = next_token()
                            if tok.type in ('REG_A', 'REG_B'):
                                if tok.type == 'REG_A':
                                    op_key = 'OP_MOVMMIA'
                                else: #tok.type == 'REG_B':
                                    op_key = 'OP_MOVMMIB'

                                Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
                                ProgramCounter += 1
                                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
                                ProgramCounter += 1
                                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
                                ProgramCounter += 1

                            else:
                                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Argumento de destino inválido para MOV!!!\n')
                                sys.exit()
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                            sys.exit()
                    else:
                        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter ]!!!\n')
                        sys.exit()
                else:
                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera un valor numérico como índice!!!\n')
                    sys.exit()

            elif tok.type == tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
                ADDH = (tok.value >> 8) & 0xFF
                ADDL = tok.value & 0xFF
                tok = next_token()
                if tok.type == 'CIERRA_CORCH':
                    tok = next_token()
                    if tok.type == 'GUION':
                        tok = next_token()
                        if tok.type == 'MAYOR_QUE':
                            tok = next_token()
                            if tok.type == 'REG_A':
                                Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVMMIA']))
                                ProgramCounter += 1
                                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
                                ProgramCounter += 1
                                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
                                ProgramCounter += 1
                            elif tok.type == 'REG_B':
                                Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code['OP_MOVMMIB']))
                                ProgramCounter += 1
                                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDH))
                                ProgramCounter += 1
                                Lista_codigo_maquina.append('0x' + '{:02X}'.format(ADDL))
                                ProgramCounter += 1
                            else:
                                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Argumento de destino inválido para MOV!!!\n')
                                sys.exit()
                        else:
                            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter >!!!\n')
                            sys.exit()
                    else:
                        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera cadena -> !!!\n')
                        sys.exit()
                else:
                    print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera cadena ]-> !!!\n')
                    sys.exit()
            else:
                print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Falta índice numérico (ix) para localidad fuente en memoria!!!\n')
                sys.exit()
        else:
            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Se espera caracter -!!!\n')
            sys.exit()
    elif tok.type == 'REG_USP':
        tok = next_token()
        if tok.type == 'CIERRA_CORCH':
            tok = next_token()
            if tok.type == 'REG_A':
                op_key = 'OP_MOVSA'
            elif tok.type == 'REG_B':
                op_key = 'OP_MOVSB'
            else:
                print(
                    f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Argumento de destino inválido para MOV!!!\n')
                sys.exit()

            Lista_codigo_maquina.append('0x' + '{:02X}'.format(OP_code[op_key]))
            ProgramCounter += 1
        else:
            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Falta corchete de cierre!!!\n')
            sys.exit()
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos + 1}: Falta índice numérico (ix) o apuntador USP para localidad fuente en memoria!!!\n')
        sys.exit()


def ensambla_OP_MOV_XX():
    tok = next_token()
    if tok.type == 'REG_A':
        ensambla_OP_MOV_AX()
    elif tok.type == 'REG_AL':
        ensambla_OP_MOV_ALX()
    elif tok.type == 'REG_B':
        ensambla_OP_MOV_BX()
    elif tok.type == 'REG_BL':
        ensambla_OP_MOV_BLX()
    elif tok.type == 'REG_R':
        ensambla_OP_MOV_RX()
    elif tok.type == 'REG_RL':
        ensambla_OP_MOV_RLX()
    elif tok.type == 'REG_RH':
        ensambla_OP_MOV_RHX()
    elif tok.type == 'REG_ACCL':
        ensambla_OP_MOV_ACCLX()
    elif tok.type == 'REG_ACCH':
        ensambla_OP_MOV_ACCHX()
    elif tok.type == 'REG_I':
        ensambla_OP_MOV_IX()
    elif tok.type == 'REG_J':
        ensambla_OP_MOV_JX()
    elif tok.type == 'DECIMAL' or tok.type == 'HEXADECIMAL':
        ensambla_OP_MOV_KX(tok.value)
    elif tok.type == 'REG_SP':
        ensambla_OP_MOV_SPX()
    elif tok.type == 'REG_USP':
        ensambla_OP_MOV_USPX()
    elif tok.type == tok.type == 'ABRE_CORCH':
        ensambla_OP_MOV_CORCHX()
    else:
        print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Argumento no válido para instrucción MOV!!!\n')
        sys.exit()

def syntax_ana_INSTRUCCION(tok):
    if not(not tok or tok.type == 'TERMINADOR'):
        if tok.type in OP_X_NOARG:
            ensambla_OP_X_NOARG(tok.type)
        elif tok.type in OP_X_ADD:
            ensambla_OP_X_ADD(tok.type)
        elif tok.type == 'OP_PUSH':
            ensambla_OP_PUSH_X()
        elif tok.type == 'OP_POP':
            ensambla_OP_POP_X()
        elif tok.type == 'OP_NOT':
            ensambla_OP_NOT_X()
        elif tok.type == 'OP_INC':
            ensambla_OP_INC_X()
        elif tok.type == 'OP_DEC':
            ensambla_OP_DEC_X()
        elif tok.type == 'OP_CMP':
            ensambla_OP_CMP_X()
        elif tok.type == 'OP_INCMP' or tok.type == 'OP_DECMP':
            ensambla_OP_XCMP(tok.type)
        elif tok.type == 'OP_IN':
            ensambla_OP_INA()
        elif tok.type == 'OP_OUT':
            ensambla_OP_OUT_X()
        elif tok.type == 'OP_MOV':
            ensambla_OP_MOV_XX()
        else:
            print(f'¡¡¡Error de sintaxis en número {tok.lineno}, columna {tok.lexpos+1}: Instrucción ASM desconocida!!!\n')
            sys.exit()

def default_ORIGEN():
    global ProgramCounter, block_org, block_org_ix
    block_org=ProgramCounter
    block_org_ix=len(Lista_codigo_maquina)
    Lista_codigo_maquina.append('ORG 0x' + '{:04X}'.format(block_org))

def analiza_linea_asm():
    tok = next_token()
    if not(not tok or tok.type == 'TERMINADOR'):
        if tok.type == 'ORIGEN':
            syntax_ana_4ORIGEN()
        else:
            if len(Lista_codigo_maquina) == 0:
                default_ORIGEN()

            if tok.type == 'ETIQUETA':
                syntax_ana_ETIQUETA(tok)
                tok = next_token()
                syntax_ana_INSTRUCCION(tok)
            else:
                syntax_ana_INSTRUCCION(tok)

def link_labels():
    N=len(Lista_codigo_maquina)

    for n in range(N):
        lexer.input(Lista_codigo_maquina[n])
        tok = next_token()
        if tok.type == 'ETIQUETA':
            if tok.value in Tabla_etiquetas:
                ADD=Tabla_etiquetas[tok.value]
                ADDH = (ADD >> 8) & 0xFF
                ADDL = ADD & 0xFF
                Lista_codigo_maquina[n]='0x' + '{:02X}'.format(ADDH)
                Lista_codigo_maquina[n+1]='0x' + '{:02X}'.format(ADDL)

            else:
                print(f'¡¡¡Error!!!: Etiqueta {tok.value} no definida!!!\n')
                sys.exit()

def close_code_block():
    block_size = ProgramCounter - block_org
    if block_org_ix >= 0:  # Si ya se empleó la primitiva ORG
        Lista_codigo_maquina[block_org_ix] = Lista_codigo_maquina[block_org_ix] + ' (SIZE ' + str(block_size) + ')'


#Uso de token() en forma manual, para ensamblar, línea por línea, un código fuente en texto:
def Nano120_asm2hex(asm_file):
# asm_file: nombre del archivo con el código fuente en ensamblador, preferentemente con extensión asm
# Salida:
# Archivo con el código máquina (en formato texto), con el mismo nombre base que el archivo fuente, pero con extensión hex.
    try:
        with open(asm_file, 'r') as codigo:
            lexer.lineno =1 #Iniializamos contador de líneas del lexer
            #Iteramos número por número:
            for n_linea, linea in enumerate(codigo, start=1):
                lexer.lineno = n_linea #Número de línea en turno
                lexer.input (linea)
                #Depuración:
                #print(f'Línea {n_linea}')
                #print(linea)
                analiza_linea_asm()

            close_code_block()
            #Depuración:
            #print(Tabla_etiquetas)
            #print(ProgramCounter)
            #print(Lista_codigo_maquina)
            link_labels()
            print(Lista_codigo_maquina)
            # Guardar los resultados en un nuevo archivo de texto
            nombre_base, _ = os.path.splitext(asm_file)
            output_file = nombre_base + ".hex"
            with open(output_file, "w") as salida:
                salida.write("\n".join(Lista_codigo_maquina))
                print(f'Código máquina ensamblado en el archivo de salida {output_file} \n')


    except FileNotFoundError:
        print(f'El archivo {asm_file} no existe \n')


if __name__ == "__main__":

    Nano120_asm2hex('Nano_code.asm')