import sys
import re


class Parser:
    A_INSTRUCTION = "A_INSTRUCTION"
    C_INSTRUCTION = "C_INSTRUCTION"
    L_INSTRUCTION = "L_INSTRUCTION"

    def __init__(self, file) -> None:
        """
        Opens the input file / stream and gets ready to parse it.
        """
        with open(file, "r") as file:
            self.instructions = file.read().splitlines()
            self.current_instruction = "start"
            self.current_line_number = -1

    def hasMoreLines(self) -> bool:
        """
        Are there more lines in the input?
        """
        return len(self.instructions) > 0

    def advance(self):
        """
        Skips over white space and comments, if necessary.
        Reads the next instruction from the input, and makes it the current instruction.
        This routine should be called only if hasMoreLines is true.
        Initially there is no current instruction.
        """
        self.current_instruction = self.instructions.pop(0).strip()
        while self.current_instruction.startswith("//") or not self.current_instruction:
            if not self.hasMoreLines():
                self.current_instruction = None
                return
            self.current_instruction = self.instructions.pop(0).strip()
        if not self.instructionType() == self.L_INSTRUCTION:
            self.current_line_number += 1

    def instructionType(self):
        """Returns the type of the current instruction:
        A_INSTRUCTION for@xxx, where xxx is
        either a decimal number or a symbol.
        C_INSTRUCTION for
        L_INSTRUCTION for (xxx), where xxx is a
        symbol."""
        if self.current_instruction == None:
            return None
        elif self.current_instruction.startswith("@"):
            return self.A_INSTRUCTION
        elif self.current_instruction.startswith("("):
            return self.L_INSTRUCTION
        return self.C_INSTRUCTION

    def symbol(self):
        """If the current instruction is (xxx), returns
        the symbol xxx. If the current instruction is
        @vxx, returns the symbol or decimal xxx (as a
        string).
        Should be called only if instruction Type
        is A_INSTRUCTION or L_INSTRUCTION."""
        if self.instructionType() == self.A_INSTRUCTION:
            return self.current_instruction[1:]
        elif self.instructionType() == self.L_INSTRUCTION:
            return self.current_instruction[1:-1]

    def dest(self):
        """Returns the symbolic dest part of the current
        C-instruction (8 possibilities).
        Should be called only if instruction Type
        is c_INSTRUCTION."""
        if "=" in self.current_instruction:
            return self.current_instruction.split("=")[0]
        return "null"

    def comp(self):
        """Returns the symbolic comp part of the
        current C-instruction (28 possibilities).
        Should be called only if instruction Type
        isc INSTRUCTION."""
        splits = re.split("[=;]", self.current_instruction)
        if len(splits) == 1:
            return splits[0]
        elif len(splits) == 3:
            return splits[1]
        else:
            if "=" in self.current_instruction:
                return splits[1]
            return splits[0]

    def jump(self):
        """Retums the symbolic jump part of the
        current C-instruction (8 possibilities).
        Should be called only if instructionType
        is C INSTRUCTION."""
        if ";" in self.current_instruction:
            return self.current_instruction.split(";")[1]
        return "null"


class Code:
    """This module provides services for translating symbolic Hack mnemonics into their binary codes. Specifically, it translates symbolic Hack mnemonics into their binary codes"""

    DEST = {
        "null": "000",
        "M": "001",
        "D": "010",
        "DM": "011",
        "MD": "011",
        "A": "100",
        "AM": "101",
        "MA": "101",
        "AD": "110",
        "DA": "110",
        "ADM": "111",
        "AMD": "111",
    }
    JUMP = {
        "null": "000",
        "JGT": "001",
        "JEQ": "010",
        "JGE": "011",
        "JLT": "100",
        "JNE": "101",
        "JLE": "110",
        "JMP": "111",
    }
    COMP = {
        "0": "0101010",
        "1": "0111111",
        "-1": "0111010",
        "D": "0001100",
        "A": "0110000",
        "!D": "0001101",
        "!A": "0110001",
        "-D": "0001111",
        "-A": "0110011",
        "D+1": "0011111",
        "A+1": "0110111",
        "D-1": "0001110",
        "A-1": "0110010",
        "D+A": "0000010",
        "A+D": "0000010",
        "D-A": "0010011",
        "A-D": "0000111",
        "D&A": "0000000",
        "A&D": "0000000",
        "D|A": "0010101",
        "A|D": "0010101",
        "M": "1110000",
        "!M": "1110001",
        "-M": "1110011",
        "M+1": "1110111",
        "M-1": "1110010",
        "D+M": "1000010",
        "M+D": "1000010",
        "D-M": "1010011",
        "M-D": "1000111",
        "D&M": "1000000",
        "M&D": "1000000",
        "D|M": "1010101",
        "M|D": "1010101",
    }

    def __init__(self) -> None:
        pass

    def dest(self, dest) -> str:
        """Returns the binary code of the dest mnemonic."""
        return self.DEST[dest]

    def comp(self, comp) -> str:
        """Returns the binary code of the comp mnemonic."""
        return self.COMP[comp]

    def jump(self, jump) -> str:
        """Returns the binary code of the jump mnemonic."""
        return self.JUMP[jump]


class SymbolTable:

    def __init__(self) -> None:
        self.table = {
            "R0": 0,
            "R1": 1,
            "R2": 2,
            "R3": 3,
            "R4": 4,
            "R5": 5,
            "R6": 6,
            "R7": 7,
            "R8": 8,
            "R9": 9,
            "R10": 10,
            "R11": 11,
            "R12": 12,
            "R13": 13,
            "R14": 14,
            "R15": 15,
            "SP": 0,
            "LCL": 1,
            "ARG": 2,
            "THIS": 3,
            "THAT": 4,
            "SCREEN": 16384,
            "KBD": 24576,
        }

    def addEntry(self, symbol, address=None):
        self.table[symbol] = address
        return

    def contains(self, symbol) -> bool:
        return symbol in self.table

    def getAdress(self, symbol) -> int:
        return self.table[symbol]


path = sys.argv[1]
symbolTable = SymbolTable()
code = Code()

# first pass
parser = Parser(path)
while parser.hasMoreLines() and parser.current_instruction:
    parser.advance()

    if parser.instructionType() == parser.A_INSTRUCTION:

        symbol = parser.symbol()
        if not symbol.isdigit() and not symbolTable.contains(symbol):
            symbolTable.addEntry(symbol)
    elif parser.instructionType() == parser.L_INSTRUCTION:
        symbolTable.addEntry(parser.symbol(), parser.current_line_number + 1)

# second pass
with open(path.split(".")[0] + ".hack", "w") as output_file:
    parser = Parser(path)
    current_address = 16
    while parser.hasMoreLines() and parser.current_instruction:
        parser.advance()
        if parser.instructionType() == parser.A_INSTRUCTION:
            symbol = parser.symbol()
            address = None
            if symbol.isdigit():
                address = int(symbol)
            else:
                address = symbolTable.getAdress(symbol)
                if address == None:
                    address = current_address
                    symbolTable.addEntry(symbol, address)
                    current_address += 1
            output_file.write(f"0{bin(address)[2:].zfill(15)}\n")
        elif parser.instructionType() == parser.C_INSTRUCTION:
            binary = (
                code.comp(parser.comp())
                + code.dest(parser.dest())
                + code.jump(parser.jump())
            )
            output_file.write(f"111{binary}\n")
