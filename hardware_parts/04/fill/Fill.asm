// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen
// by writing 'black' in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen by writing
// 'white' in every pixel;
// the screen should remain fully clear as long as no key is pressed.

//// Replace this comment with your code.
(INIT)
    @KBD
    D=M
    @INIT
    D;JEQ

    @SCREEN
    D=A
    @1
    M=D
(FILL)
    @1
    A=M
    M=-1
    A=A+1
    D=A
    @1
    M=D

    @KBD
    D=A-D
    @FILL
    D;JGE

(LOOP)
    @KBD
    D=M
    @LOOP
    D;JNE

    @SCREEN
    D=A
    @1
    M=D
(CLEAR)
    @1
    A=M
    M=0
    A=A+1
    D=A
    @1
    M=D

    @KBD
    D=A-D
    @CLEAR
    D;JGE
    @INIT
    0;JMP
