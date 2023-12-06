import json
import sys

from machine.isa import Opcode
from compiler import Compiler
from lexer import Lexer
from parsing import Parser

STDLIB_FILE = "../examples/stdlib.clisp"


def write_code(filename: str, instruction_code: list[dict], static_data: list[int]):
    with open(filename, "w", encoding="utf-8") as file:
        json.dump({"code": instruction_code, "data": static_data}, file, indent=4)


def read_code(filename: str) -> tuple[list[dict], list[int]]:
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())
        # TODO: deserialize Addressing and Register
        for instruction in code:
            instruction["opcode"] = Opcode(instruction["opcode"])
    return code["code"], code["data"]


def translate(source_code: str) -> tuple[list[dict], list[int]]:
    # TODO: append standard library
    lex = Lexer(source_code)
    tokens = lex.tokenize()
    ast = Parser(tokens).parse()
    compiler = Compiler(ast, 1024, 1024)
    compiler.compile()
    return compiler.text.instructions, compiler.data.layout()


def main(source_file: str, target_file: str):
    with open(STDLIB_FILE, encoding="utf-8") as file:
        stdlib_source = file.read() + '\n'
    with open(source_file, encoding="utf-8") as file:
        source_file = file.read() + stdlib_source
        instruction_code, static_memory = translate(source_file)
        write_code(target_file, instruction_code, static_memory)
        print(
            "source LoC:",
            len(source_file.split("\n")),
            "code instr: {}".format(len(instruction_code)),
            "static memory: {}".format(len(static_memory))
        )


if __name__ == "__main__":
    assert len(sys.argv) == 3, "Wrong arguments: translator.py <input_file> <target_file>"
    _, source, target = sys.argv
    main(source, target)