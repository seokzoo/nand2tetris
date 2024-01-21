import os
import re
import sys
import secrets

def stripLine(lines):
    for line in lines:
        striped = line.strip()
        if striped:
            yield striped

def removeInlineComment(lines):
    for line in lines:
        if line[0:2] != '//':
            idx = line.find('//')
            if idx != -1:
                yield line[:idx]
            else:
                yield line

class Translator:
    def __init__(self):
        self.pointer_table = {
            'static' : 16,
            'temp' : 5
        }
        self.symbol_table = {
            'local' : 'LCL',
            'argument' : 'ARG',
            'this' : 'THIS',
            'that' : 'THAT'
        }
        self.dest_table = {
            0 : 'THIS',
            1 : 'THAT'
        }
        self.twoOperandsOpTable = {
            'add' : '+',
            'sub' : '-',
            'or' : '|',
            'and' : '&',
        }
        self.oneOperandOpTable = {
            'neg' : '-',
            'not' : '!' 
        }
        self.stackArithmeticOps = ['add', 'sub', 'or', 'and', 'neg', 'not', 'eq', 'gt', 'lt', 'push', 'pop']
        self.programControlOps = ['label', 'goto', 'if-goto', 'call', 'function', 'return']
        self.nStaticVariables = 0
        self.staticTable = {}

    def translateStackArithmeticOp(self, splited):
        nToken = len(splited)
        opcode = splited[0].lower()
        random_hash = secrets.token_hex(nbytes=16)
        if nToken == 1: # Arithmetic & Logical
            if opcode in ['add', 'sub', 'or', 'and']:
                return f'''@SP
M=M-1
A=M
D=M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R14
M=D
@R13
D=M
@R14
M=M{self.twoOperandsOpTable[opcode]}D
D=M
@SP
A=M
M=D
@SP
M=M+1'''
            elif opcode in ['neg', 'not']:
                return f'''@SP
M=M-1
A=M
D=M
M={self.oneOperandOpTable[opcode]}D
@SP
M=M+1'''
            elif opcode == 'eq':
                return f'''@SP
M=M-1
A=M
D=M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R14
M=D
@R13
D=M
@R14
D=M-D
@{random_hash}_eq
D;JEQ
D=0
@{random_hash}_end
0;JMP
({random_hash}_eq)
D=0
D=!D
({random_hash}_end)
@SP
A=M
M=D
@SP
M=M+1'''
            elif opcode == 'gt':
                return f'''@SP
M=M-1
A=M
D=M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R14
M=D
@R13
D=M
@R14
D=M-D
@{random_hash}_gt
D;JGT
D=0
@{random_hash}_end
0;JMP
({random_hash}_gt)
D=0
D=!D
({random_hash}_end)
@SP
A=M
M=D
@SP
M=M+1'''
            elif opcode == 'lt':
                return f'''@SP
M=M-1
A=M
D=M
@R13
M=D
@SP
M=M-1
A=M
D=M
@R14
M=D
@R13
D=M
@R14
D=D-M
@{random_hash}_gt
D;JGT
D=0
@{random_hash}_end
0;JMP
({random_hash}_gt)
D=0
D=!D
({random_hash}_end)
@SP
A=M
M=D
@SP
M=M+1'''
        elif nToken == 3: # Stack
            opcode = splited[0].lower()
            ref = splited[1].lower()
            n = int(splited[2])

            if ref in ['local', 'argument', 'this', 'that']:
                if opcode == 'push':
                    return f'''@{self.symbol_table[ref]}
D=M
@{n}
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1'''
                elif opcode == 'pop':
                    return f'''@{self.symbol_table[ref]}
D=M
@{n}
D=A+D
@R13
M=D
@SP
M=M-1
@SP
A=M
D=M
@R13
A=M
M=D'''
            elif ref == 'constant':
                return f'''@{n}
D=A
@SP
A=M
M=D
@SP
M=M+1'''
            elif ref == 'static':
                if n not in self.staticTable:
                    self.staticTable[n] = self.nStaticVariables
                    self.nStaticVariables += 1
                if opcode == 'push':
                    return f'''@{self.pointer_table[ref] + self.staticTable[n]}
D=M
@SP
A=M
M=D
@SP
M=M+1'''

                elif opcode == 'pop':
                    return f'''@SP
M=M-1
@SP
A=M
D=M
@{self.pointer_table[ref] + self.staticTable[n]}
M=D'''
            elif ref == 'temp':
                if opcode == 'push':
                    return f'''@{self.pointer_table[ref] + n}
D=M
@SP
A=M
M=D
@SP
M=M+1'''

                elif opcode == 'pop':
                    return f'''@SP
M=M-1
@SP
A=M
D=M
@{self.pointer_table[ref] + n}
M=D'''
            elif ref == 'pointer':
                if opcode == 'push':
                    return f'''@{self.dest_table[n]}
D=M
@SP
A=M
M=D
@SP
M=M+1'''
                elif opcode == 'pop':
                    return f'''@SP
M=M-1
@SP
A=M
D=M
@{self.dest_table[n]}
M=D'''

    def translateProgramControlOp(self, splited):
        nToken = len(splited)
        random_hash = secrets.token_hex(nbytes=16)
        opcode = splited[0].lower()
        if nToken == 2: # Branching
            label_name = splited[1].lower()
            
            if opcode == 'label':
                return f'''(label_{label_name})'''
            elif opcode == 'goto':
                return f'''@label_{label_name}
0;JMP'''
            elif opcode == 'if-goto':
                return f'''@SP
M=M-1
A=M
D=M
@label_{label_name}
D;JNE'''
        elif nToken == 3:
            function_name = splited[1]
            nArgs = int(splited[2])
            if opcode == 'function':
                snippets = []
                push_fmt = '''@0
D=A
@SP
A=M
M=D
@SP
M=M+1'''
                snippets.append(f'(function_{function_name})')
                for i in range(nArgs):
                    snippets.append(push_fmt)
                generated_code = '\n'.join(snippets)
                return generated_code
            elif opcode == 'call':
                snippets = []
                ret_label = f'ret_{random_hash}'
                push_fmt = '''@{0}
D=M
@SP
A=M
M=D
@SP
M=M+1'''
                snippets.append(f'''@{ret_label}
D=A
@SP
A=M
M=D
@SP
M=M+1''')
                for operand in ['LCL', 'ARG', 'THIS', 'THAT']:
                    snippets.append(push_fmt.format(operand))
                snippets.append(f'''@SP
D=M
@5
D=D-A
@{nArgs}
D=D-A
@ARG
M=D''')
                snippets.append(f'''@SP
D=M
@LCL
M=D''')
                snippets.append(f'''@function_{function_name}
0;JMP''')
                snippets.append(f'({ret_label})')
                generated_code = '\n'.join(snippets)
                return generated_code
        elif nToken == 1:
            if opcode == 'return':
                return f'''@LCL
D=M
@R14
M=D
D=M
@5
A=D-A
D=M
@R15
M=D
@SP
M=M-1
A=M
D=M
@ARG
A=M
M=D
@ARG
D=M
@SP
M=D+1
@R14
D=M
@1
A=D-A
D=M
@THAT
M=D
@R14
D=M
@2
A=D-A
D=M
@THIS
M=D
@R14
D=M
@3
A=D-A
D=M
@ARG
M=D
@R14
D=M
@4
A=D-A
D=M
@LCL
M=D
@R15
A=M
0;JMP'''
    def translate(self, code):
        splited = code.strip().split(' ')
        opcode = splited[0].lower()

        if opcode in self.stackArithmeticOps:
            return self.translateStackArithmeticOp(splited)
        elif opcode in self.programControlOps:
            return self.translateProgramControlOp(splited)

        raise Exception

def main(path):
    if os.path.isfile(path):
        with open(path) as f:
            removed = stripLine(removeInlineComment(f.readlines()))
            data = '\n'.join(line for line in removed)
            code = re.sub('\/\*([\s\S]*?)\*\/', '', data)
            translator = Translator()
            for line in code.split('\n'):
                print(translator.translate(line))
    else:
        translator = Translator()
        print('''@256
D=A
@SP
M=D''')
        print(translator.translateProgramControlOp(['call', 'Sys.init', '0']))
        for file in os.scandir(path):
            translator.staticTable = {}
            if file.path.endswith(('.vm')):
                with open(file) as f:
                    removed = stripLine(removeInlineComment(f.readlines()))
                    data = '\n'.join(line for line in removed)
                    code = re.sub('\/\*([\s\S]*?)\*\/', '', data)
                    for line in code.split('\n'):
                        print(translator.translate(line))

if __name__ == "__main__":
    main(sys.argv[1])
