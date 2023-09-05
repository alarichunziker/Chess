import random

piece_scores = {'K': 0, 'Q': 9, "R": 5, "B": 3, "N": 3, 'P': 1}

knight_score = [[1, 1, 1, 1, 1, 1, 1, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 4, 4, 3, 2, 1],
                [1, 2, 3, 3, 3, 3, 2, 1],
                [1, 2, 2, 2, 2, 2, 2, 1],
                [1, 1, 1, 1, 1, 1, 1, 1]]

bishop_scores = [[4, 3, 2, 1, 1, 2, 3, 4],
                 [3, 4, 3, 2, 2, 3, 4, 3],
                 [2, 3, 4, 3, 3, 4, 3, 2],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [1, 2, 3, 4, 4, 3, 2, 1],
                 [2, 3, 4, 3, 3, 4, 3, 2],
                 [3, 4, 3, 2, 2, 3, 4, 3],
                 [4, 3, 2, 1, 1, 2, 3, 4]]

queen_scores = [[1, 1, 1, 3, 1, 1, 1, 1],
                [1, 1, 2, 3, 3, 1, 1, 1],
                [1, 2, 3, 3, 3, 1, 1, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 2, 3, 3, 3, 2, 2, 1],
                [1, 4, 3, 3, 3, 4, 2, 1],
                [1, 1, 2, 3, 3, 1, 1, 1],
                [1, 1, 1, 3, 1, 1, 1, 1]]


rook_scores = [[4, 3, 4, 4, 4, 4, 3, 4],
               [4, 4, 4, 4, 4, 4, 4, 4],
               [1, 1, 2, 3, 3, 2, 1, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 2, 3, 4, 4, 3, 2, 1],
               [1, 1, 2, 2, 2, 2, 1, 1],
               [4, 4, 4, 4, 4, 4, 4, 4],
               [4, 3, 4, 4, 4, 4, 3, 4]]

pawn_scores_black = [[0, 0, 0, 0, 0, 0, 0, 0],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [1, 1, 2, 3, 3, 2, 1, 1],
                     [1, 2, 3, 4, 4, 3, 2, 1],
                     [2, 3, 3, 5, 5, 3, 3, 2],
                     [5, 6, 6, 7, 7, 6, 6, 5],
                     [8, 8, 8, 8, 8, 8, 8, 8],
                     [8, 8, 8, 8, 8, 8, 8, 8]]

pawn_scores_white = [[8, 8, 8, 8, 8, 8, 8, 8],
                     [8, 8, 8, 8, 8, 8, 8, 8],
                     [5, 6, 6, 7, 7, 6, 6, 5],
                     [2, 3, 3, 5, 5, 3, 3, 2],
                     [1, 2, 3, 4, 4, 3, 2, 1],
                     [1, 1, 1, 0, 0, 1, 1, 1],
                     [0, 0, 0, 0, 0, 0, 0, 0]]

piece_position_scores = {"wP": pawn_scores_white, "bP": pawn_scores_black, "N": knight_score,
                         "B": bishop_scores,  "R": rook_scores, "Q": queen_scores}


checkmate = 1000
stalemate = 0
max_depth = 2

'''
Scoring functions
'''


def score_board(gs):
    if gs.checkmate:
        if gs.whiteToMove:
            return -checkmate
        else:
            return checkmate
    elif gs.stalemate:
        return stalemate

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            square = gs.board[row][col]
            if square != '--':
                piece_position_score = 0
                # normalize this based on the piece type
                if square[1] != 'K':
                    if square[1] == 'P':
                        piece_position_score = piece_position_scores[square][row][col]
                    else:
                        piece_position_score = piece_position_scores[square[1]][row][col]

                if square[0] == 'w':
                    score += (piece_scores[square[1]] + piece_position_score * .1)
                elif square[0] == 'b':
                    score -= (piece_scores[square[1]] + piece_position_score * .1)

    return score


'''
Algorithms to generate chess moves
'''


def find_random_move(valid_moves):
    return random.choice(valid_moves)


def min_max_helper(gs, valid_moves):
    global next_move
    next_move = None
    min_max(gs, valid_moves, max_depth, gs.whiteToMove)
    return next_move


def min_max(gs, valid_moves, move_depth, white_turn):
    global next_move
    if move_depth == 0:

        return score_board(gs)

    if white_turn:
        max_score = -checkmate
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = min_max(gs, next_moves, move_depth-1, False)
            if score > max_score:
                max_score = score
                if move_depth == max_depth:
                    next_move = move
            gs.undo_move()
        return max_score

    else:
        min_score = checkmate
        for move in valid_moves:
            gs.make_move(move)
            next_moves = gs.get_valid_moves()
            score = min_max(gs, next_moves, move_depth-1, True)
            if score < min_score:
                min_score = score
                if move_depth == max_depth:
                    next_move = move
            gs.undo_move()
        return min_score


def nega_max_alphaBeta_helper(gs, valid_moves):
    global next_move
    next_move = None

    nega_max_alphaBeta(gs, valid_moves, max_depth, -checkmate, checkmate, 1 if gs.whiteToMove else -1)
    return next_move


def nega_max_alphaBeta(gs, valid_moves, depth, alpha, beta,  multiplier):
    global next_move

    if depth == 0:
        return score_board(gs) * multiplier

    # move ordering -
    max_score = -checkmate
    for move in valid_moves:
        gs.make_move(move)
        next_moves = gs.get_valid_moves()
        # Reverse values as perspective changes
        score = -nega_max_alphaBeta(gs, next_moves, depth - 1, -beta, -alpha, -multiplier)
        if score > max_score:
            max_score = score
            if depth == max_depth:
                next_move = move
        gs.undo_move()
        #pruning
        if max_score > alpha:
            alpha = max_score
        if alpha >= beta:
            break

    return max_score