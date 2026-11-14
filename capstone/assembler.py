#!/usr/bin/env python3
"""Hack assembler for the Nand to Tetris capstone project."""

"""Requirements from the assignment:
- Remove comments and blank lines
- Record labels
- Assign variables to RAM addresses starting at 16
- Convert every Hack instruction to 16-bit binary
- For K = 42 (K % 3 == 0), export symbols.txt containing labels and variables
"""

from __future__ import annotations

import sys
from pathlib import Path

K = 42

PREDEFINED = {
    "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
    "SCREEN": 16384, "KBD": 24576,
    "R0": 0, "R1": 1, "R2": 2, "R3": 3, "R4": 4, "R5": 5, "R6": 6, "R7": 7,
    "R8": 8, "R9": 9, "R10": 10, "R11": 11, "R12": 12, "R13": 13, "R14": 14, "R15": 15,
}

COMP = {
    "0": "0101010", "1": "0111111", "-1": "0111010", "D": "0001100", "A": "0110000", "M": "1110000",
    "!D": "0001101", "!A": "0110001", "!M": "1110001", "-D": "0001111", "-A": "0110011",
    "-M": "1110011", "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010", "D+A": "0000010", "D+M": "1000010",
    "D-A": "0010011", "A-D": "0000111", "D-M": "1010011", "M-D": "1000111",
    "D&A": "0000000", "D|A": "0101010", "D&M": "1000000", "D|M": "1010101",
    "A&D": "0000000", "A|D": "0101010", "M&D": "1000000", "M|D": "1010101",
}

DEST = {"": "000", "M": "001", "D": "010", "MD": "011", "A": "100", "AM": "101", "AD": "110", "AMD": "111"}
JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011", "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111"}


def strip_comments(raw: str) -> str:
    return raw.split("//", 1)[0].strip()


def normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def parse_instruction(line: str):
    if not line:
        return None
    if line.startswith("@"):
        return ("A", line[1:])
    if line.startswith("(") and line.endswith(")"):
        return ("LABEL", line[1:-1])
    return ("C", line)


def first_pass(lines):
    symbol_table = PREDEFINED.copy()
    instruction_count = 0
    for raw in lines:
        line = strip_comments(raw)
        if not line:
            continue
        kind, payload = parse_instruction(line)
        if kind == "LABEL":
            label = normalize_symbol(payload)
            if label in symbol_table and label not in {"SCREEN", "KBD", *[f"R{i}" for i in range(16)]}:  # keep valid labels unique
                pass
            symbol_table[label] = instruction_count
        else:
            instruction_count += 1
    return symbol_table


def canonical_comp(comp: str) -> str:
    s = comp.replace(" ", "")
    aliases = {
        "M+D": "D+M",
        "A+D": "D+A",
        "M&D": "D&M",
        "A&D": "D&A",
        "M|D": "D|M",
        "A|D": "D|A",
    }
    return aliases.get(s, s)


def assemble_a_instruction(token: str, symbols: dict, next_var: int):
    normalized = normalize_symbol(token)
    if normalized.isdigit():
        value = int(normalized)
    elif normalized in symbols:
        value = symbols[normalized]
    else:
        value = next_var
        symbols[normalized] = value
        next_var += 1
    return f"0{value:015b}", next_var


def assemble_c_instruction(line: str):
    if "=" in line:
        left, right = line.split("=", 1)
        dest = left.strip()
        remainder = right.strip()
    else:
        dest = ""
        remainder = line.strip()

    if ";" in remainder:
        comp_part, jump_part = remainder.split(";", 1)
        jump = jump_part.strip()
    else:
        comp_part = remainder
        jump = ""

    comp = canonical_comp(comp_part.strip())
    if comp not in COMP:
        raise ValueError(f"invalid computation: {comp_part!r}")
    return f"111{('1' if 'M' in comp else '0')}{COMP[comp]}{DEST.get(dest, '000')}{JUMP.get(jump, '000')}"


def assemble(source: Path, output: Path):
    with source.open("r", encoding="utf-8") as fh:
        raw_lines = fh.readlines()

    cleaned = []
    for raw in raw_lines:
        line = strip_comments(raw)
        if line:
            cleaned.append(line)

    symbols = first_pass(cleaned)

    # assign variables after labels; labels already occupy addresses
    next_var = 16
    final_symbols = symbols.copy()
    assembled = []
    for raw in cleaned:
        line = strip_comments(raw)
        if not line:
            continue
        kind, payload = parse_instruction(line)
        if kind == "LABEL":
            continue
        if kind == "A":
            token = payload.strip()
            token_norm = normalize_symbol(token)
            if token_norm.isdigit():
                value = int(token_norm)
                assembled.append(f"0{value:015b}")
                continue
            if token_norm in final_symbols:
                value = final_symbols[token_norm]
                assembled.append(f"0{value:015b}")
                continue
            value = next_var
            final_symbols[token_norm] = value
            next_var += 1
            assembled.append(f"0{value:015b}")
        elif kind == "C":
            assembled.append(assemble_c_instruction(line))

    output.write_text("\n".join(assembled) + ("\n" if assembled else ""), encoding="utf-8")
    return final_symbols


def export_symbols(symbol_table: dict, folder: Path):
    entries = []
    for name, value in sorted(symbol_table.items(), key=lambda kv: (kv[1], kv[0])):
        if name not in PREDEFINED and not name.isdigit():
            entries.append(f"{name} {value}")
    path = folder / "symbols.txt"
    path.write_text("\n".join(entries) + ("\n" if entries else ""), encoding="utf-8")


def main():
    if len(sys.argv) < 2:
        print("Usage: assembler.py <source.asm> [output.hack]")
        return 1

    source = Path(sys.argv[1])
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else source.with_suffix(".hack")
    symbols = assemble(source, output)
    if K % 3 == 0:
        export_symbols(symbols, source.parent)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
