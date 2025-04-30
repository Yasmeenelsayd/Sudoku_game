import random


class Cell:

    def __init__(self, row, col, value, editable):
   
        self.row = row
        self.col = col
        self.value = value
        self._editable = editable

    @property
    def row(self):
        return self._row

    @row.setter
    def row(self, row):
        if row < 0 or row > 8:
            raise AttributeError('Row must be between 0 and 8.')
        else:
            self._row = row

    @property
    def col(self):
        return self._col

    @col.setter
    def col(self, col):
        if col < 0 or col > 8:
            raise AttributeError('Col must be between 0 and 8.')
        else:
            self._col = col

    @property
    def value(self):
        return self._value

    @property
    def editable(self):
        return self._editable

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'

    @value.setter
    def value(self, value):
        if value is not None and (value < 1 or value > 9):
            raise AttributeError('Value must be between 1 and 9.')
        else:
            self._value = value


class Sudoku:

    def __init__(self, board):
        self.board = []
        for row in range(9):
            self.board.append([])
            for col in range(9):
                if board[row][col] == 0:
                    val = None
                    editable = True
                else:
                    val = board[row][col]
                    editable = False
                self.board[row].append(Cell(row, col, val, editable))

    def check_move(self, cell, num):
        for col in range(9):
            if self.board[cell.row][col].value == num and col != cell.col:
                return False

        for row in range(9):
            if self.board[row][cell.col].value == num and row != cell.row:
                return False

        for row in range(cell.row // 3 * 3, cell.row // 3 * 3 + 3):
            for col in range(cell.col // 3 * 3, cell.col // 3 * 3 + 3):
                if (
                    self.board[row][col].value == num
                    and row != cell.row
                    and col != cell.col
                ):
                    return False
                
        return True

    def get_possible_moves(self, cell):
        possible_moves = [num for num in range(1, 10)]

        for col in range(9):
            if self.board[cell.row][col].value in possible_moves:
                possible_moves.remove(self.board[cell.row][col].value)

        for row in range(9):
            if self.board[row][cell.col].value in possible_moves:
                possible_moves.remove(self.board[row][cell.col].value)

        for row in range(cell.row // 3 * 3, cell.row // 3 * 3 + 3):
            for col in range(cell.col // 3 * 3, cell.col // 3 * 3 + 3):
                if self.board[row][col].value in possible_moves:
                    possible_moves.remove(self.board[row][col].value)

        return possible_moves

    def get_empty_cell(self):
        for row in range(9):
            for col in range(9):
                if self.board[row][col].value is None:
                    return self.board[row][col]

        return False

    def solve(self):
        cell = self.get_empty_cell()

        if not cell:
            return True

        for val in range(1, 10):

            if not self.check_move(cell, val):
                continue

            cell.value = val

            if self.solve():
                return True

            cell.value = None

        return False

    def get_board(self):
        return [[self.board[row][col].value for col in range(9)] for row in range(9)]

    def test_solve(self):
        current_board = self.get_board()
        solvable = self.solve()

        for row in range(9):
            for col in range(9):
                self.board[row][col].value = current_board[row][col]

        return solvable

    def reset(self):
        for row in self.board:
            for cell in row:
                if cell.editable:
                    cell.value = None

