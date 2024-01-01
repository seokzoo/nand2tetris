import re
import sys

variable_count = 16

def removeSpaces(lines):
    for line in lines:
        replaced = line.replace(' ', '').strip()
        if replaced != '':
            yield replaced

def removeInlineComment(lines):
    for line in lines:
        if line[0:2] != '//':
            idx = line.find('//')
            if idx != -1:
                yield line[:idx]
            else:
                yield line

def translate(line, symbol_table):
    global variable_count
    splited = line.split(';')
    inst = splited[0].strip()
    ch = inst[0]
    jump_field = '000' 
    if len(splited) > 1:
        jump_inst = splited[1].strip()
        if jump_inst == 'JGT':
            jump_field = '001'
        elif jump_inst == 'JEQ':
            jump_field = '010'
        elif jump_inst == 'JGE':
            jump_field = '011'
        elif jump_inst == 'JLT':
            jump_field = '100'
        elif jump_inst == 'JNE':
            jump_field = '101'
        elif jump_inst == 'JLE':
            jump_field = '110'
        elif jump_inst == 'JMP':
            jump_field = '111'
    if ch == '@': # A-inst
        symbol = inst[1:]
        itob = lambda x: bin(x)[2:].zfill(16)
        if symbol in symbol_table:
            return itob(symbol_table[symbol])
        else:
            if symbol.isdecimal():
                return itob(int(symbol))
            else:
                symbol_table[symbol] = variable_count
                variable_count += 1
                return itob(symbol_table[symbol])
    else:         # C-inst
        instruction = '111'
        splited = inst.split('=')
        if len(splited) > 1:
            dest, comp = splited
        else:
            dest, comp = 'null', splited[0]
        a_field = '0'
        if 'M' in comp:
            a_field = '1'
        if comp == '0':
            comp_field = '101010'
        elif comp == '1':
            comp_field = '111111'
        elif comp == '-1':
            comp_field = '111010'
        elif comp == 'D':
            comp_field = '001100'
        elif comp == 'A' or comp == 'M':
            comp_field = '110000'
        elif comp == '!D':
            comp_field = '001101'
        elif comp == '!A' or comp == '!M':
            comp_field = '110001'
        elif comp == '-D':
            comp_field = '001111'
        elif comp == '-A' or comp == '-M':
            comp_field = '110011'
        elif comp == 'D+1':
            comp_field = '011111'
        elif comp == 'A+1' or comp == 'M+1':
            comp_field = '110111'
        elif comp == 'D-1':
            comp_field = '001110'
        elif comp == 'A-1' or comp == 'M-1':
            comp_field = '110010'
        elif comp == 'D+A' or comp == 'D+M':
            comp_field = '000010'
        elif comp == 'D-A' or comp == 'D-M':
            comp_field = '010011'
        elif comp == 'A-D' or comp == 'M-D':
            comp_field = '000111'
        elif comp == 'D&A' or comp == 'D&M':
            comp_field = '000000'
        elif comp == 'D|A' or comp == 'D|M':
            comp_field = '010101'
        dest_field = ''
        if 'A' in dest:
            dest_field += '1'
        else:
            dest_field += '0'
        if 'D' in dest:
            dest_field += '1'
        else:
            dest_field += '0'
        if 'M' in dest:
            dest_field += '1'
        else:
            dest_field += '0'
        instruction += a_field
        instruction += comp_field
        instruction += dest_field
        instruction += jump_field
        return instruction

def main(filename):
    symbol_table = {
        'SCREEN': 16384,
        'KBD': 24576,
        'SP': 0,
        'LCL': 1,
        'ARG': 2,
        'THIS': 3,
        'THAT': 4,
    }
    for i in range(0, 16):
        symbol_table[f'R{i}'] = i

    with open(filename) as f:
        removed = removeInlineComment(removeSpaces(f))
        data = '\n'.join(line for line in removed)
        code = re.sub('\/\*([\s\S]*?)\*\/', '', data)
        count = 0
        label_table = {}
        for i, line in enumerate(code.split('\n')):
            if line[0] == '(':
                label_name = line[1:-1]
                if label_name in symbol_table.keys():
                    raise Exception
                label_table[label_name] = i - count
                count += 1
        symbol_table |= label_table
        for line in code.split('\n'):
            if line[0] != '(':
                binary_code = translate(line, symbol_table) 
                print(binary_code)

if __name__ == "__main__":
    main(sys.argv[1])
