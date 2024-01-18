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
        self.programControlOps = ['label', 'goto', 'if-goto']

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
            elif ref in ['static', 'temp']:
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
        if nToken == 2: # Branching
            opcode = splited[0].lower()
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
D;JGT'''

    def translate(self, code):
        splited = code.strip().split(' ')
        opcode = splited[0].lower()

        if opcode in self.stackArithmeticOps:
            return self.translateStackArithmeticOp(splited)
        elif opcode in self.programControlOps:
            return self.translateProgramControlOp(splited)

        raise Exception

def main(filename):
    with open(filename) as f:
        removed = stripLine(removeInlineComment(f.readlines()))
        data = '\n'.join(line for line in removed)
        code = re.sub('\/\*([\s\S]*?)\*\/', '', data)
        translator = Translator()
        for line in code.split('\n'):
            print(translator.translate(line))

if __name__ == "__main__":
    main(sys.argv[1])
