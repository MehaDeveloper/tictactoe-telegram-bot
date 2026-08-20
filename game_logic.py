import random
import db
from lexicon import LEXICON
from db import get_difficulty


async def show_result(user_id: int) -> str:
    field = await db.array_field(user_id)
    res = ''
    for i in range(0, 9, 3):
        res += (LEXICON[field[i]] + '   ' +
                LEXICON[field[i + 1]] + '   ' +
                LEXICON[field[i + 2]] + '\n')
    return res


def check_winner_board(field: list[int]) -> tuple[bool, int]:
    for i in range(0, 9, 3):
        if field[i] == field[i + 1] == field[i + 2] != 0:
            return True, field[i]

    for i in range(3):
        if field[i] == field[i + 3] == field[i + 6] != 0:
            return True, field[i]

    if field[0] == field[4] == field[8] != 0:
        return True, field[0]
    if field[2] == field[4] == field[6] != 0:
        return True, field[2]

    return False, 0


async def check_winner(user_id: int) -> tuple[bool, int]:
    field = await db.array_field(user_id)
    return check_winner_board(field)


def minimax(field: list[int], depth: int, is_maximizing: bool) -> int:
    has_winner, winner = check_winner_board(field)

    if has_winner:
        return 10 - depth if winner == 2 else -10 + depth

    if 0 not in field:
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(9):
            if field[i] == 0:
                field[i] = 2
                score = minimax(field, depth + 1, False)
                field[i] = 0
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for i in range(9):
            if field[i] == 0:
                field[i] = 1
                score = minimax(field, depth + 1, True)
                field[i] = 0
                best_score = min(score, best_score)
        return best_score


async def get_bot_move(field: list[int], user_id: int) -> int:
    difficulty = await get_difficulty(user_id)
    if difficulty == 'easy':
        return get_worst_move(field)
    elif difficulty == 'medium':
        if random.random() < 0.5:
            return get_worst_move(field)
        return get_best_move(field)
    return get_best_move(field)


def get_worst_move(field: list[int]) -> int:
    empty_cells = [i for i, val in enumerate(field) if field[i] == 0]
    return random.choice(empty_cells)


def get_best_move(board: list[int]) -> int:
    best_score = -float('inf')
    best_move = -1
    for i in range(9):
        if board[i] == 0:
            board[i] = 2
            score = minimax(board, 0, False)
            board[i] = 0
            if score > best_score:
                best_score = score
                best_move = i
    return best_move
