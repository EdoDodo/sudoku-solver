#!/usr/bin/env python3

from sudoku import Sudoku

def z3_solving(sudoku, colours):
    """ Function solving the given sudoku puzzle using Z3 """

    from z3 import Solver, Int, Or, Sum, Distinct, sat

    #positions = cross("ABCDEFGHI", "123456789")
    symbols = {pos: Int(pos) for pos in sudoku.positions}

    # first we build a solver with the general constraints for sudoku puzzles:
    s = Solver()

    # assure that every cell holds a value of [1,9]
    for symbol in symbols.values():
        s.add(Or([symbol == i for i in range(1, 10)]))

    # assure that every row covers every value:
    for row in "ABCDEFGHI":
        s.add(Distinct([symbols[row + col] for col in "123456789"]))

    # assure that every column covers every value:
    for col in "123456789":
        s.add(Distinct([symbols[row + col] for row in "ABCDEFGHI"]))

    # assure that every block covers every value:
    for i in range(3):
        for j in range(3):
            s.add(Distinct([symbols["ABCDEFGHI"[m + i * 3] + "123456789"[n + j * 3]] for m in range(3) for n in range(3)]))

    # now we put the assumptions of the given puzzle into the solver:
    for pos, value in sudoku.grid.items():
        if value in "123456789":
            s.add(symbols[pos] == value)

    for colour in colours:
        blobs = []
        for blob in colour:
            blobs.append(Sum([symbols[blob[i:i+2]] for i in range(0, len(blob), 2)]))
        for blob in blobs[1:]:
            s.add(blob == blobs[0])

    if s.check() != sat:
        raise Exception("unsolvable")

    model = s.model()
    values = {pos: model.evaluate(s).as_string() for pos, s in symbols.items()}
    return Sudoku(values)

def main(puzzle):
    print("[+] parsing puzzle:", puzzle)

    s = Sudoku.parse(puzzle)

    print("[+] start solving using Z3")

    s_solved = z3_solving(s, [])

    print("[+] solved:", s_solved.is_solved())
    print(s_solved)

def colour(puzzle):
    print("[+] parsing colour puzzle:", puzzle)

    colours = []
    for colour in puzzle.split(";"):
        colours.append(colour.split(","))

    print("[+] start solving using Z3")

    s_solved = z3_solving(Sudoku(), colours)

    print("[+] solved")
    print(Sudoku.parse(str(s_solved)).pretty_print())

if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        main(argv[1])
    elif (argv[1] == "-c"):
        colour(argv[2])
    else:
        print("[!] we are using some test puzzle due to invalid arguments")
        main("4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......")