import pygame
import sys
import time
import copy
import random
from collections import deque
import heapq
from solver import Sudoku


pygame.init()

cell_size = 75
minor_grid_size = 1
major_grid_size = 3
buffer = 5
button_height = 70
button_width = 150
button_border = 2
extra_top_ui = 70
extra_bottom_ui = 100
left_ui = 250
width =  cell_size*9 + minor_grid_size*6 + major_grid_size*4 + buffer*2 
height = cell_size*9 + minor_grid_size*6 + \
    major_grid_size*4 + button_height + buffer*3 + button_border*2 
size = width+170, height
white = 255, 255, 255
black = 0, 0, 0
brown =  0,0,153 #dark blue  #142, 119,84 brown
gray = 200, 200, 200
green = 0, 175, 0
red = 200, 0, 0
blue = 51,153,255
d_purple = 102, 0, 102
d_pink = 153,0,76
pink = 255,0,127
l_pink = 255, 153, 204
inactive_btn = d_purple    #142, 119, 84
active_btn =  156, 0, 165  #165, 42, 42    #0, 0, 0 



screen = pygame.display.set_mode(size)
pygame.display.set_caption('Sudoku')

class RectCell(pygame.Rect):

    def __init__(self, left, top, row, col):
        super().__init__(left, top, cell_size, cell_size)
        self.row = row
        self.col = col


def create_cells():

    cells = [[] for _ in range(9)]

    row = 0
    col = 0
    left = buffer + major_grid_size
    top = buffer + major_grid_size

    while row < 9:
        while col < 9:
            cells[row].append(RectCell(left, top, row, col))

            left += cell_size + minor_grid_size
            if col != 0 and (col + 1) % 3 == 0:
                left = left + major_grid_size - minor_grid_size
            col += 1


        top += cell_size + minor_grid_size
        if row != 0 and (row + 1) % 3 == 0:
            top = top + major_grid_size - minor_grid_size
        left = buffer + major_grid_size
        col = 0
        row += 1

    return cells


def draw_grid():
    lines_drawn = 0
    pos = buffer + major_grid_size + cell_size
    while lines_drawn < 6:
        pygame.draw.line(screen, l_pink, (pos, buffer),
                         (pos, width-buffer-1), minor_grid_size)
        pygame.draw.line(screen, l_pink, (buffer, pos),
                         (width-buffer-1, pos), minor_grid_size)

        lines_drawn += 1

        pos += cell_size + minor_grid_size
        if lines_drawn % 2 == 0:
            pos += cell_size + major_grid_size

    for pos in range(buffer+major_grid_size//2, width, cell_size*3 + minor_grid_size*2 + major_grid_size):
        pygame.draw.line(screen, l_pink, (pos, buffer),
                         (pos, width-buffer-1), major_grid_size)
        pygame.draw.line(screen, l_pink, (buffer, pos),
                         (width-buffer-1, pos), major_grid_size)


def fill_cells(cells, board):
    font = pygame.font.Font(None, 38)

    for row in range(9):
        for col in range(9):
            if board.board[row][col].value is None:
                continue

            if not board.board[row][col].editable:
                font.bold = True
                text = font.render(f'{board.board[row][col].value}', 1, d_pink)

            else:
                font.bold = False
                if board.check_move(board.board[row][col], board.board[row][col].value):
                    text = font.render(
                        f'{board.board[row][col].value}', 1, green)
                else:
                    text = font.render(
                        f'{board.board[row][col].value}', 1, red)

            xpos, ypos = cells[row][col].center
            textbox = text.get_rect(center=(xpos, ypos))
            screen.blit(text, textbox)


def draw_button(left, top, width, height, border, color, border_color, text):
    pygame.draw.rect(
        screen,
        border_color,
        (left, top, width+border*2, height+border*2),
    )

    button = pygame.Rect(
        left+border,
        top+border,
        width,
        height
    )
    pygame.draw.rect(screen, color, button)

    font = pygame.font.Font(None, 26)
    text = font.render(text, 1, white)
    xpos, ypos = button.center
    textbox = text.get_rect(center=(xpos, ypos))
    screen.blit(text, textbox)

    return button


def draw_board(active_cell, cells, game):
    draw_grid()
    if active_cell is not None:
        pygame.draw.rect(screen, gray, active_cell)

    fill_cells(cells, game)


def visual_solve(game, cells):
    cell = game.get_empty_cell()

    if not cell:
        return True

    for val in range(1, 10):
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        cell.value = val

        screen.fill(white)
        draw_board(None, cells, game)
        cell_rect = cells[cell.row][cell.col]
        pygame.draw.rect(screen, red, cell_rect, 5)
        pygame.display.update([cell_rect])
        #time.sleep(0.02)

        if not game.check_move(cell, val):
            cell.value = None
            continue

        screen.fill(white)
        pygame.draw.rect(screen, green, cell_rect, 5)
        draw_board(None, cells, game)
        pygame.display.update([cell_rect])

        if visual_solve(game, cells):
            return True

        cell.value = None


    screen.fill(white)
    pygame.draw.rect(screen, white, cell_rect, 5)
    draw_board(None, cells, game)
    pygame.display.update([cell_rect])
    return False


def bfs_solve(game, cells):

    queue = deque()
    visited = set()

    def board_signature(board):
        return tuple(tuple(cell.value for cell in row) for row in board)

    initial_state = copy.deepcopy(game.board)
    queue.append(initial_state)

    while queue:
        current_board = queue.popleft()
        sig = board_signature(current_board)
        if sig in visited:
            continue
        visited.add(sig)

        for r in range(9):
            for c in range(9):
                game.board[r][c].value = current_board[r][c].value

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill(white)
        draw_board(None, cells, game)
        pygame.display.flip()
        #time.sleep(0.02)
          
        cell = game.get_empty_cell()
        if not cell:
            return True

        for val in range(1, 10):

            cell.value = val

            screen.fill(white)
            draw_board(None, cells, game)
            cell_rect = cells[cell.row][cell.col]
            pygame.draw.rect(screen, red, cell_rect, 5)
            pygame.display.update([cell_rect])


            if not game.check_move(cell, val):
                cell.value = None
                continue

            new_state = copy.deepcopy(current_board)
            new_state[cell.row][cell.col].value = val
            queue.append(new_state)
            screen.fill(white)
            pygame.draw.rect(screen, green, cell_rect, 5)
            draw_board(None, cells, game)
            pygame.display.update([cell_rect])

    screen.fill(white)
    pygame.draw.rect(screen, white, cell_rect, 5)
    draw_board(None, cells, game)
    pygame.display.update([cell_rect])    

    return False


def dls_solve(game, cells, limit, depth=0):

    cell = game.get_empty_cell()
    if not cell:
        return True
    
    if depth > limit:
        return False

    for val in range(1, 10):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
  

        if not game.check_move(cell, val):
            continue

        cell.value = val

        screen.fill(white)
        draw_board(None, cells, game)
        cell_rect = cells[cell.row][cell.col]
        pygame.draw.rect(screen, red, cell_rect, 5)
        pygame.display.update([cell_rect])
        #time.sleep(0.02)

        if dls_solve(game, cells, limit, depth + 1):
            return True

        cell.value = None

    screen.fill(white)
    draw_board(None, cells, game)
    pygame.display.update()
    return False


def ids_solve(game, cells):        
    depth = 0
    while True:
        result = dls_solve(game, cells, depth)
        if result:
            return True
        depth += 1


from itertools import count
def astar_solve(sudoku,cells):
    
    def heuristic(board):
        #return sum(1 for row in board for cell in row if cell.value is None)
        return sum(len(sudoku.get_possible_moves(cell)) for row in board for cell in row if cell.value is None)

    def board_signature(board):
        return tuple(tuple(cell.value for cell in row) for row in board)

    pq = []
    visited = set()
    counter = count()
    heapq.heappush(pq, (heuristic(sudoku.board), 0, next(counter), copy.deepcopy(sudoku.board)))

    while pq:
        f, g, _, current_board = heapq.heappop(pq)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        cell = sudoku.get_empty_cell()
        if not cell:
            return True

        sig = board_signature(current_board)
        if sig in visited:
            continue
        visited.add(sig)

        for r in range(9):
            for c in range(9):
                sudoku.board[r][c].value = current_board[r][c].value

        screen.fill(white)  
        cell_rect = cells[cell.row][cell.col]
        pygame.draw.rect(screen, green, cell_rect, 5)
        draw_board(None, cells, sudoku)
        pygame.display.update([cell_rect])
        time.sleep(0.02) 

        for row in range(9):
            for col in range(9):
                cell = current_board[row][col]

                if cell.value is None:
                    
                    possible = sudoku.get_possible_moves(cell)
                    for val in possible:
                        new_board = copy.deepcopy(current_board)
                        new_board[row][col].value = val
                        h = heuristic(new_board)
                        heapq.heappush(pq, (g + 1 + h, g + 1, next(counter), new_board))
                    break
            else:
                continue
            break
    return False


def greedy_solve(sudoku, cells):
    
    def heuristic(board):
        #return sum(1 for row in board for cell in row if cell.value is None)
        return sum(len(sudoku.get_possible_moves(cell)) for row in board for cell in row if cell.value is None)


    def board_signature(board):
        return tuple(tuple(cell.value for cell in row) for row in board)

    pq = []
    visited = set()
    counter = count()
    heapq.heappush(pq, (heuristic(sudoku.board), next(counter), copy.deepcopy(sudoku.board)))

    while pq:
        f, _, current_board = heapq.heappop(pq)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        cell = sudoku.get_empty_cell()
        if not cell:
            return True

        sig = board_signature(current_board)
        if sig in visited:
            continue
        visited.add(sig)

        for r in range(9):
            for c in range(9):
                sudoku.board[r][c].value = current_board[r][c].value

        screen.fill(white) 
        cell_rect = cells[cell.row][cell.col]
        pygame.draw.rect(screen, green, cell_rect, 5)
        draw_board(None, cells, sudoku)
        pygame.display.update([cell_rect])
        time.sleep(0.02) 


        for row in range(9):
            for col in range(9):
                cell = current_board[row][col]

                if cell.value is None:
                    
                    possible = sudoku.get_possible_moves(cell)
                    for val in possible:
                        new_board = copy.deepcopy(current_board)
                        new_board[row][col].value = val
                        h = heuristic(new_board)
                        heapq.heappush(pq, (h , next(counter), new_board))
                    break
            else:
                continue
            break
    return False

    
def check_sudoku(sudoku):

    if sudoku.get_empty_cell():
        raise ValueError('Game is not complete')

    row_sets = [set() for _ in range(9)]
    col_sets = [set() for _ in range(9)]
    box_sets = [set() for _ in range(9)]

    for row in range(9):
        for col in range(9):
            box = (row // 3) * 3 + col // 3
            value = sudoku.board[row][col].value

            if value in row_sets[row] or value in col_sets[col] or value in box_sets[box]:
                return False

            row_sets[row].add(value)
            col_sets[col].add(value)
            box_sets[box].add(value)

    return True


def play():

    def is_valid(board, row, col, num):
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False
        box_x = col // 3 * 3
        box_y = row // 3 * 3
        for i in range(3):
            for j in range(3):
                if board[box_y + i][box_x + j] == num:
                    return False
        return True
    
    def solve_board(board):
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if is_valid(board, row, col, num):
                            board[row][col] = num
                            if solve_board(board):
                                return True
                            board[row][col] = 0
                    return False
        return True    

    def remove_by_percentage(board, percent):
        total_cells = 81
        to_remove = int((percent / 100.0) * total_cells)
        removed = 0
        while removed < to_remove:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if board[row][col] != 0:
                board[row][col] = 0
                removed += 1
        return board
    
    def generate_board(level='easy'):
        percent_map = {
            'easy': 40,
            'medium': 60,
            'hard': 70
        }
        percent = percent_map.get(level, 40)
        board = [[0 for _ in range(9)] for _ in range(9)]
        solve_board(board)
        puzzle = copy.deepcopy(board)
        puzzle = remove_by_percentage(puzzle, percent)
        return puzzle


    puzzle = generate_board('easy')
    game = Sudoku(puzzle)
    cells = create_cells()
    active_cell = None

    dfs_time = None
    bfs_time = None
    ids_time = None
    astar_time = None
    greedy_time = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()


            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = pygame.mouse.get_pos()

                if l_easy.collidepoint(mouse_pos):
                    puzzle = generate_board('easy')
                    game = Sudoku(puzzle)

                if l_medium.collidepoint(mouse_pos):
                    puzzle = generate_board('medium')
                    game = Sudoku(puzzle)

                if l_hard.collidepoint(mouse_pos):
                    puzzle = generate_board('hard')
                    game = Sudoku(puzzle)

                if reset_btn.collidepoint(mouse_pos):
                    game.reset()

                if solve_btn.collidepoint(mouse_pos):
                    screen.fill(white)
                    active_cell = None
                    draw_board(active_cell, cells, game)
                    reset_btn = draw_button(
                        width+160 - buffer - button_border*2 - button_width,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Reset'
                    )
                    l_easy = draw_button(
                        width+100 - buffer*3 - button_border*2 - button_width - 130 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Easy'
                    )
                    l_medium = draw_button(
                        width - buffer*3 - button_border*2 - button_width - 265 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Medium'
                    )
                    l_hard = draw_button(
                        width-100 - buffer*3 - button_border*2 - button_width - 400 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Hard'
                    )
                    solve_btn = draw_button(
                        width+160  - button_border*2 - button_width,
                        height-650 - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        black,
                        'DFS Solve'
                    )
                    astar_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-130 - button_height - button_border*2 - buffer,
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "A* Solve"
                    )
                    greedy_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-260 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "Greedy Solve" 
                    )
                    bfs_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-520 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "BFS Solve"
                    )
                    ids_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-390 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "IDS Solve"
                    )

                    pygame.display.flip()
                    start_time = time.time() 
                    visual_solve(game, cells)
                    dfs_time = time.time() - start_time

                 
                if bfs_btn.collidepoint(mouse_pos):
                    screen.fill(white)
                    active_cell = None
                    draw_board(active_cell, cells, game)
                    reset_btn = draw_button(
                        width+160 - buffer - button_border*2 - button_width,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Reset'
                    )
                    l_easy = draw_button(
                        width+100 - buffer*3 - button_border*2 - button_width - 130 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Easy'
                    )
                    l_medium = draw_button(
                        width - buffer*3 - button_border*2 - button_width - 265 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Medium'
                    )
                    l_hard = draw_button(
                        width-100 - buffer*3 - button_border*2 - button_width - 400 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Hard'
                    )
                    solve_btn = draw_button(
                        width+160  - button_border*2 - button_width,
                        height-650 - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        black,
                        'DFS Solve'
                    )
                    astar_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-130 - button_height - button_border*2 - buffer,
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "A* Solve"
                    )
                    greedy_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-260 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "Greedy Solve" 
                    )
                    bfs_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-520 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "BFS Solve"
                    )
                    ids_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-390 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "IDS Solve"
                    )

                    pygame.display.flip()
                    start_time = time.time() 
                    bfs_solve(game, cells)
                    bfs_time = time.time() - start_time

                 
                if ids_btn.collidepoint(mouse_pos):
                    screen.fill(white)
                    active_cell = None
                    draw_board(active_cell, cells, game)
                    reset_btn = draw_button(
                        width+160 - buffer - button_border*2 - button_width,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Reset'
                    )
                    l_easy = draw_button(
                        width+100 - buffer*3 - button_border*2 - button_width - 130 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Easy'
                    )
                    l_medium = draw_button(
                        width - buffer*3 - button_border*2 - button_width - 265 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Medium'
                    )
                    l_hard = draw_button(
                        width-100 - buffer*3 - button_border*2 - button_width - 400 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Hard'
                    )
                    solve_btn = draw_button(
                        width+160  - button_border*2 - button_width,
                        height-650 - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        black,
                        'DFS Solve'
                    )
                    astar_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-130 - button_height - button_border*2 - buffer,
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "A* Solve"
                    )
                    greedy_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-260 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "Greedy Solve" 
                    )
                    bfs_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-520 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "BFS Solve"
                    )
                    ids_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-390 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "IDS Solve"
                    )

                    pygame.display.flip()
                    start_time = time.time() 
                    ids_solve(game, cells)
                    #dls_solve(game, cells,limit=81)
                    ids_time = time.time() - start_time
                

                if astar_btn.collidepoint(mouse_pos):
                    screen.fill(white)
                    active_cell = None
                    draw_board(active_cell, cells, game)
                    reset_btn = draw_button(
                        width+160 - buffer - button_border*2 - button_width,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Reset'
                    )
                    l_easy = draw_button(
                        width+100 - buffer*3 - button_border*2 - button_width - 130 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Easy'
                    )
                    l_medium = draw_button(
                        width - buffer*3 - button_border*2 - button_width - 265 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Medium'
                    )
                    l_hard = draw_button(
                        width-100 - buffer*3 - button_border*2 - button_width - 400 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Hard'
                    )
                    solve_btn = draw_button(
                        width+160  - button_border*2 - button_width,
                        height-650 - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        black,
                        'DFS Solve'
                    )
                    astar_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-130 - button_height - button_border*2 - buffer,
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "A* Solve"
                    )
                    greedy_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-260 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "Greedy Solve" 
                    )
                    bfs_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-520 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "BFS Solve"
                    )
                    ids_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-390 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "IDS Solve"
                    )

                    pygame.display.flip()
                    start_time = time.time() 
                    astar_solve(game, cells)
                    astar_time = time.time() - start_time
                

                if greedy_btn.collidepoint(mouse_pos):
                    screen.fill(white)
                    active_cell = None
                    draw_board(active_cell, cells, game)
                    reset_btn = draw_button(
                        width+160 - buffer - button_border*2 - button_width,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Reset'
                    )
                    l_easy = draw_button(
                        width+100 - buffer*3 - button_border*2 - button_width - 130 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Easy'
                    )
                    l_medium = draw_button(
                        width - buffer*3 - button_border*2 - button_width - 265 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Medium'
                    )
                    l_hard = draw_button(
                        width-100 - buffer*3 - button_border*2 - button_width - 400 ,
                        height - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        white,
                        'Hard'
                    )
                    solve_btn = draw_button(
                        width+160  - button_border*2 - button_width,
                        height-650 - button_height - button_border*2 - buffer,
                        button_width,
                        button_height,
                        button_border,
                        inactive_btn,
                        black,
                        'DFS Solve'
                    )
                    astar_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-130 - button_height - button_border*2 - buffer,
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "A* Solve"
                    )
                    greedy_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-260 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "Greedy Solve" 
                    )
                    bfs_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-520 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "BFS Solve"
                    )
                    ids_btn = draw_button(
                        width +160- button_border*2 - button_width ,
                        height-390 - button_height - button_border*2 - buffer, 
                        button_width, 
                        button_height, 
                        button_border, 
                        inactive_btn, 
                        white, 
                        "IDS Solve"
                    )

                    pygame.display.flip()
                    start_time = time.time() 
                    greedy_solve(game,cells)
                    greedy_time = time.time() - start_time

                # Test if point in any cell
                active_cell = None
                for row in cells:
                    for cell in row:
                        if cell.collidepoint(mouse_pos):
                            active_cell = cell

                # Test if active cell is empty
                if active_cell and not game.board[active_cell.row][active_cell.col].editable:
                    active_cell = None

            if event.type == pygame.KEYUP:
                if active_cell is not None:

                    if event.key == pygame.K_0 or event.key == pygame.K_KP0:
                        game.board[active_cell.row][active_cell.col].value = 0
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                        game.board[active_cell.row][active_cell.col].value = 1
                    if event.key == pygame.K_2 or event.key == pygame.K_KP2:
                        game.board[active_cell.row][active_cell.col].value = 2
                    if event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        game.board[active_cell.row][active_cell.col].value = 3
                    if event.key == pygame.K_4 or event.key == pygame.K_KP4:
                        game.board[active_cell.row][active_cell.col].value = 4
                    if event.key == pygame.K_5 or event.key == pygame.K_KP5:
                        game.board[active_cell.row][active_cell.col].value = 5
                    if event.key == pygame.K_6 or event.key == pygame.K_KP6:
                        game.board[active_cell.row][active_cell.col].value = 6
                    if event.key == pygame.K_7 or event.key == pygame.K_KP7:
                        game.board[active_cell.row][active_cell.col].value = 7
                    if event.key == pygame.K_8 or event.key == pygame.K_KP8:
                        game.board[active_cell.row][active_cell.col].value = 8
                    if event.key == pygame.K_9 or event.key == pygame.K_KP9:
                        game.board[active_cell.row][active_cell.col].value = 9
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        game.board[active_cell.row][active_cell.col].value = None

        screen.fill(white)

        draw_board(active_cell, cells, game)

        font = pygame.font.Font(None, 30)
        text = font.render('AI Algorithms', 1, d_purple)
        screen.blit(text, ( width+15, height-770))

        reset_btn = draw_button(
            width+160 - buffer - button_border*2 - button_width,
            height - button_height - button_border*2 - buffer,
            button_width,
            button_height,
            button_border,
            inactive_btn,
            white,
            'Reset'
        )        
        l_easy = draw_button(
            width+100 - buffer*3 - button_border*2 - button_width - 130 ,
            height - button_height - button_border*2 - buffer,
            button_width,
            button_height,
            button_border,
            inactive_btn,
            white,
            'Easy'
        )
        l_medium = draw_button(
            width - buffer*3 - button_border*2 - button_width - 265,
            height - button_height - button_border*2 - buffer,
            button_width,
            button_height,
            button_border,
            inactive_btn,
            white,
            'Medium'
        )
        l_hard = draw_button(
            width -100- buffer*3 - button_border*2 - button_width - 400,
            height - button_height - button_border*2 - buffer,
            button_width,
            button_height,
            button_border,
            inactive_btn,
            white,
            'Hard'
        )
        solve_btn = draw_button(
            width +160 - button_border*2 - button_width ,
            height-650 - button_height - button_border*2 - buffer,
            button_width,
            button_height,
            button_border,
            inactive_btn,
            white,
            'DFS Solve'
        )
        astar_btn = draw_button(
            width +160- button_border*2 - button_width ,
            height-130 - button_height - button_border*2 - buffer,
            button_width, 
            button_height, 
            button_border, 
            inactive_btn, 
            white, 
            "A* Solve"
        )
        greedy_btn = draw_button(
            width +160- button_border*2 - button_width ,
            height-260 - button_height - button_border*2 - buffer, 
            button_width, 
            button_height, 
            button_border, 
            inactive_btn, 
            white, 
            "Greedy Solve" 
        )
        bfs_btn = draw_button(
            width +160- button_border*2 - button_width ,
            height-520 - button_height - button_border*2 - buffer, 
            button_width, 
            button_height, 
            button_border, 
            inactive_btn, 
            white, 
            "BFS Solve"
        )
        ids_btn = draw_button(
            width +160- button_border*2 - button_width ,
            height-390 - button_height - button_border*2 - buffer, 
            button_width, 
            button_height, 
            button_border, 
            inactive_btn, 
            white, 
            "IDS Solve"
        )

        if reset_btn.collidepoint(pygame.mouse.get_pos()):
            reset_btn = draw_button(
                width+160 - buffer - button_border*2 - button_width,
                height - button_height - button_border*2 - buffer,
                button_width,
                button_height,
                button_border,
                active_btn,
                black,
                'Reset'
            )        
        if l_easy.collidepoint(pygame.mouse.get_pos()):
            l_easy = draw_button(
                width+100 - buffer*3 - button_border*2 - button_width - 130,
                height - button_height - button_border*2 - buffer,
                button_width,
                button_height,
                button_border,
                active_btn,
                black,
                'Easy'
            )
        if l_medium.collidepoint(pygame.mouse.get_pos()):
            l_medium = draw_button(
                width - buffer*3 - button_border*2 - button_width - 265,
                height - button_height - button_border*2 - buffer,
                button_width,
                button_height,
                button_border,
                active_btn,
                black,
                'Medium'
            )
        if l_hard.collidepoint(pygame.mouse.get_pos()):
            l_hard = draw_button(
                width-100 - buffer*3 - button_border*2 - button_width - 400,
                height - button_height - button_border*2 - buffer,
                button_width,
                button_height,
                button_border,
                active_btn,
                black,
                'Hard'
            )
        if solve_btn.collidepoint(pygame.mouse.get_pos()):
            solve_btn = draw_button(
                width+160  - button_border*2 - button_width ,
                height-650 - button_height - button_border*2 - buffer,
                button_width,
                button_height,
                button_border,
                active_btn,
                black,
                'DFS Solve'
            )
        if astar_btn.collidepoint(pygame.mouse.get_pos()):
            astar_btn = draw_button(
                width +160- button_border*2 - button_width ,
                height-130 - button_height - button_border*2 - buffer,
                button_width, 
                button_height, 
                button_border, 
                active_btn, 
                black, 
                "A* Solve"
            )
        if greedy_btn.collidepoint(pygame.mouse.get_pos()):
                greedy_btn = draw_button(
                width +160- button_border*2 - button_width ,
                height-260 - button_height - button_border*2 - buffer, 
                button_width, 
                button_height, 
                button_border, 
                active_btn, 
                black, 
                "Greedy Solve" 
            )
        if bfs_btn.collidepoint(pygame.mouse.get_pos()):
            bfs_btn = draw_button(
                width +160- button_border*2 - button_width ,
                height-520 - button_height - button_border*2 - buffer, 
                button_width, 
                button_height, 
                button_border, 
                active_btn, 
                black, 
                "BFS Solve"
            )   
        if ids_btn.collidepoint(pygame.mouse.get_pos()):
            ids_btn = draw_button(
                width +160- button_border*2 - button_width ,
                height-390 - button_height - button_border*2 - buffer, 
                button_width, 
                button_height, 
                button_border, 
                active_btn, 
                black, 
                "IDS Solve"
            )

        mid_x = width // 2 
        mid_y = (cell_size * 9) // 2 + buffer
      
        if not game.get_empty_cell():
            if check_sudoku(game):
                
                font = pygame.font.Font(None, 50)
                text = font.render('Solved!', 1, green)
                textbox = text.get_rect(center=(mid_x,mid_y))
                screen.blit(text, textbox)

                font = pygame.font.Font(None, 24)
                if dfs_time is not None:
                    time_text = font.render(f'{dfs_time:.3f} s', True, black)
                    screen.blit(time_text, ( width+50, height-635))
                if bfs_time is not None:
                    time_text = font.render(f'{bfs_time:.3f} s', True, black)
                    screen.blit(time_text, ( width+50, height-505))
                if ids_time is not None:
                    time_text = font.render(f'{ids_time:.3f} s', True, black)
                    screen.blit(time_text, ( width+50, height-375))
                if astar_time is not None:
                    time_text = font.render(f'{astar_time:.3f} s', True, black)
                    screen.blit(time_text, ( width+50, height-115))
                if greedy_time is not None:
                    time_text = font.render(f'{greedy_time:.3f} s', True, black)
                    screen.blit(time_text, ( width+50, height-245))
                    
        pygame.display.flip()

    


if __name__ == '__main__':
    play()
