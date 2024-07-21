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

(RESET)
@SCREEN
D=A
@i
M=D
(LOOP)
//check if end of screen
@24576
D=A
@i
D=D-M
@RESET
D;JEQ
// read keyboard
@24576
D=M
// if key pressed jump to black
@BLACK
D;JNE
@i
A=M
M=0
//increment screen index
(INCREMENT)
@i
M=M+1
@LOOP
0;JMP
(BLACK)
@i
A=M
M=-1
@INCREMENT
0;JMP