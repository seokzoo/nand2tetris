@ARG
D=M
@1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M
D=M
@THAT
M=D
@0
D=A
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@0
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
M=D
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@1
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
M=D
@ARG
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@2
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
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
M=M-D
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@0
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
M=D
(label_loop)
@ARG
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
A=M
D=M
@label_compute_element
D;JNE
@label_end
0;JMP
(label_compute_element)
@THAT
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@1
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
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
M=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
@THAT
D=M
@2
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
M=D
@THAT
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
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
M=M+D
D=M
@SP
A=M
M=D
@SP
M=M+1
@SP
M=M-1
@SP
A=M
D=M
@THAT
M=D
@ARG
D=M
@0
A=D+A
D=M
@SP
A=M
M=D
@SP
M=M+1
@1
D=A
@SP
A=M
M=D
@SP
M=M+1
@SP
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
M=M-D
D=M
@SP
A=M
M=D
@SP
M=M+1
@ARG
D=M
@0
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
M=D
@label_loop
0;JMP
(label_end)