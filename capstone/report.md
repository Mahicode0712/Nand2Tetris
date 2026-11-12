# Capstone Project Report

Student Name: Mahi Singh  
Roll No.: 2501350042  
K: 42  
Course: Nand to Tetris – I (ETCCNT301)  
School: School of Engineering & Technology, K.R. Mangalam University

## 1. Idea in one line
The Hack computer draws a black box on the screen while a key is pressed and clears it when the key is released.

## 2. K-dependent configuration
Given the roll number 2501350042, the last two digits are 42, so:

- K = 42
- Starting row = 42
- Box height = 20 rows
- Box width = 16 × ((42 mod 4) + 1) = 16 × 3 = 48 pixels

The box therefore occupies a 48-pixel wide, 20-row tall region beginning at row 42.

## 3. Part A – Build the computer
I created the required Hack computer HDL files in the capstone/HDL folder:

- CPU.hdl
- Memory.hdl
- Computer.hdl

The CPU and memory files are aligned with the Nand2Tetris lab design and the course simulation conventions. For compatibility, the memory module uses the built-in RAM16K chip where the official lab chip is unavailable or unstable, which is permitted by the assignment instructions.

## 4. Part B – Assembler in Python
The assembler implemented in assembler.py does the following:

- strips comments and blank lines
- keeps track of labels like (LOOP)
- assigns variables to RAM addresses starting at 16
- translates each Hack instruction to a 16-bit binary machine word
- writes a symbol table `symbols.txt` because K = 42, and 42 % 3 = 0

The assembler was tested on the standard sample programs `Add.asm`, `Max.asm`, `Rect.asm`, and `Pong.asm` and successfully produced their corresponding `.hack` files.

## 5. Part C – Box program
The file `Box.asm` implements the required behavior:

- while any key is pressed, a black box appears on the screen
- when the key is released, the box is cleared
- the box sits at row 42, is 20 rows tall, and is 48 pixels wide

The logic follows the standard `Fill.asm` approach adapted to a finite rectangular area. The program uses the screen stride of 32 words per row, and each word is 16 pixels wide.

## 6. One mistake that was fixed
A common issue in box drawing is incorrectly computing the screen base address. If the base pointer is not advanced row by row using the screen stride of 32 words, the box drifts or overlaps the wrong memory region. I corrected this by resetting the pointer to `SCREEN + 32 × K` and then stepping through each row with a fixed increment so the box stays aligned with the display memory.

## 7. Files in the submission
The project is organized as follows:

- `capstone/assembler.py`
- `capstone/Add.asm`, `Max.asm`, `Rect.asm`, `Pong.asm`
- `capstone/Box.asm`
- `capstone/Box.hack`
- `capstone/symbols.txt`
- `capstone/HDL/CPU.hdl`, `Memory.hdl`, `Computer.hdl`
- `capstone/report.md`
- `capstone/screenshots/`

## 8. Viva preparation
In the viva, I would explain:

- how the assembler identifies labels and variables,
- how screen memory is mapped,
- why the box program checks the keyboard status before painting,
- and how a small change like moving the box down would change the starting row address.

## 9. Summary
This project satisfies the assignment requirements by providing a working assembler, a valid box-drawing Hack program, the required K-based extra feature, and a short report suitable for submission.
