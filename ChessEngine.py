"""
Store information about the current state of the chess game. Determines the valid moves at current state,
and keeps a move log
"""
class GameState:
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.move_functions = {'P': self.get_pawn_moves, 'N': self.get_knight_moves, 'B': self.get_bishop_moves,
                               'R': self.get_rook_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}

        self.whiteToMove = True
        self.moveLog = []
        self.en_passant = ()
        self.en_passant_log = [self.en_passant]

        self.white_king = (7, 4)
        self.black_king = (0, 4)
        self.castling_ability = Castle(True, True, True, True)
        self.castle_log = [Castle(self.castling_ability.wks, self.castling_ability.wqs,
                                  self.castling_ability.bks, self.castling_ability.bqs)]
        self.checkmate = False
        self.stalemate = False

    def make_move(self, move):
        if self.board[move.start_row][move.start_col] != "--":
            self.board[move.start_row][move.start_col] = "--"
            self.board[move.end_row][move.end_col] = move.piece_moved
            self.moveLog.append(move)
            self.whiteToMove = not self.whiteToMove

            # Track king locations
            if move.piece_moved == 'wK':
                self.white_king = (move.end_row, move.end_col)

            elif move.piece_moved == 'bK':
                self.black_king = (move.end_row, move.end_col)

            # pawn promotion
            if move.pawn_promotion:
                self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

            if move.en_passant_move:
                self.board[move.start_row][move.end_col] = "--"  # Capture pawn in En passant

            # Change en_passant variable
            if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
                self.en_passant = ((move.start_row + move.end_row) // 2, move.end_col)
            else:
                self.en_passant = ()

            # Castle move
            if move.castle_move:
                if move.end_col - move.start_col == 2:  # King side
                    self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col+1] = '--'
                else:  # Queen side
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2]
                    self.board[move.end_row][move.end_col-2] = '--'

            self.en_passant_log.append(self.en_passant)
            # Castling rights -> rook or king move
            self.update_castle_rights(move)
            self.castle_log.append(Castle(self.castling_ability.wks, self.castling_ability.wqs,
                                          self.castling_ability.bks, self.castling_ability.bqs))

    def update_castle_rights(self, move):
        # King move
        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.castling_ability.wqs = False
                elif move.end_col == 7:
                    self.castling_ability.wks = False
        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.castling_ability.bqs = False
                elif move.end_col == 7:
                    self.castling_ability.bks = False

        if move.piece_moved == 'wK':
            self.castling_ability.wks = False
            self.castling_ability.wqs = False
        elif move.piece_moved == 'bK':
            self.castling_ability.bks = False
            self.castling_ability.bqs = False
        # Rook move
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.castling_ability.wqs = False
                else:  # right rook
                    self.castling_ability.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.castling_ability.bqs = False
                else:
                    self.castling_ability.bks = False

        if move.piece_captured == 'wR':
            if move.end_row == 7:
                if move.end_col == 0:
                    self.castling_ability.wqs = False
                elif move.end_col == 7:
                    self.castling_ability.wks = False

        elif move.piece_captured == 'bR':
            if move.end_row == 0:
                if move.end_col == 0:
                    self.castling_ability.bqs = False
                elif move.end_col == 7:
                    self.castling_ability.bks = False

    def undo_move(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.whiteToMove = not self.whiteToMove

            if move.piece_moved == 'wK':
                self.white_king = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king = (move.start_row, move.start_col)

            if move.en_passant_move:
                self.board[move.end_row][move.end_col] = "--"
                self.board[move.start_row][move.end_col] = move.piece_captured

            self.en_passant_log.pop()
            self.en_passant = self.en_passant_log[-1]

            self.castle_log.pop()
            self.castling_ability.wks = self.castle_log[-1].wks
            self.castling_ability.wqs = self.castle_log[-1].wqs
            self.castling_ability.bks = self.castle_log[-1].bks
            self.castling_ability.bqs = self.castle_log[-1].bqs

            if move.castle_move:
                if move.end_col - move.start_col == 2:  # King side
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-1]
                    self.board[move.end_row][move.end_col-1] = '--'
                else:
                    self.board[move.end_row][move.end_col-2] = self.board[move.end_row][move.end_col+1]
                    self.board[move.end_row][move.end_col+1] = '--'

            self.checkmate = False
            self.stalemate = False

    def get_valid_moves(self):
        temp_en_passant_possible = self.en_passant
        temp_castling_ability = Castle(self.castling_ability.wks, self.castling_ability.wqs,
                                       self.castling_ability.bks, self.castling_ability.bqs)
        moves = self.get_all_possible_moves()
        if self.whiteToMove:
            self.get_castle_moves(self.white_king[0], self.white_king[1], moves)
        else:
            self.get_castle_moves(self.black_king[0], self.black_king[1], moves)

        for i in range(len(moves)-1, -1, -1):
            self.make_move(moves[i])
            self.whiteToMove = not self.whiteToMove
            if self.in_check():
                moves.remove(moves[i])

            self.whiteToMove = not self.whiteToMove
            self.undo_move()

        if len(moves) == 0:
            if self.in_check():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.checkmate = False

        self.en_passant = temp_en_passant_possible
        self.castling_ability = temp_castling_ability
        return moves

    def in_check(self):
        if self.whiteToMove:
            return self.square_under_attack(self.white_king[0], self.white_king[1])
        else:
            return self.square_under_attack(self.black_king[0], self.black_king[1])

    def square_under_attack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        opponents_moves = self.get_all_possible_moves()
        self.whiteToMove = not self.whiteToMove
        for move in opponents_moves:
            if move.end_row == r and move.end_col == c:
                return True

        return False

    def get_all_possible_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn, piece = self.board[r][c][0], self.board[r][c][1]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    self.move_functions[piece](r, c, moves)

        return moves

    def get_pawn_moves(self, r, c, moves):
        # Forward move and double move for white
        if self.whiteToMove:
            if self.board[r - 1][c] == "--":
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board)) 
            # Left
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.en_passant:
                    moves.append(Move((r, c), (r-1, c-1), self.board, en_passant_move=True))
            # Right
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r - 1, c + 1) == self.en_passant:
                    moves.append(Move((r, c), (r - 1, c+1), self.board, en_passant_move=True))
        else:
            # Moves for black
            if self.board[r+1][c] == "--":
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board))

            # Diagonal captures
            # left
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r + 1, c - 1) == self.en_passant:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, en_passant_move=True))

            # right
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r + 1, c + 1) == self.en_passant:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, en_passant_move=True))

    def get_knight_moves(self, r, c, moves):
        knight_moves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        enemy_color = "b" if self.whiteToMove else 'w'
        for move in knight_moves:
            end_row = r + move[0]
            end_col = c + move[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color or end_piece == "--":
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_bishop_moves(self, r, c, moves):
        directions = ((-1, -1), (1, 1), (-1, 1), (1, -1))
        enemy_color = "b" if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_rook_moves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy_color = "b" if self.whiteToMove else 'w'
        for d in directions:
            for i in range(1, 8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece == "--":
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif end_piece[0] == enemy_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break

    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_king_moves(self, r, c, moves):
        directions = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        enemy_color = 'b' if self.whiteToMove else "w"
        for i in range(8):
            end_row = r + directions[i][0]
            end_col = c + directions[i][1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color or end_piece == "--":
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_castle_moves(self, r, c, moves):
        if self.square_under_attack(r, c):
            return
        if (self.whiteToMove and self.castling_ability.wks) or (not self.whiteToMove and self.castling_ability.bks):
            self._get_king_side(r, c, moves)

        if (self.whiteToMove and self.castling_ability.wqs) or (not self.whiteToMove and self.castling_ability.bqs):
            self._get_queen_side(r, c, moves)

    def _get_king_side(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, castle_move=True))

    def _get_queen_side(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, castle_move=True))


class Move:
    rank_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in rank_to_rows.items()}

    files_to_col = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_col.items()}

    def __init__(self, start_square, end_square, board, en_passant_move=False, castle_move=False):
        # start square and end square are tuples that contain (row, col) to identify the square
        self.start_row = start_square[0]
        self.start_col = start_square[1]
        self.end_row = end_square[0]
        self.end_col = end_square[1]

        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        # en_passant
        self.en_passant_move = en_passant_move
        # Having this line is caused by the poor valid_moves algorithm
        if self.en_passant_move:
            self.piece_captured = 'wP' if self.piece_moved == 'bP' else 'bP'

        # pawn promotion
        self.pawn_promotion = (self.piece_moved == 'wP' and self.end_row == 0) or \
                              (self.piece_moved == 'bP' and self.end_row == 7)

        self.castle_move = castle_move

        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False

    def __str__(self):
        return self.piece_moved[1] + self.get_rank_file(self.end_row, self.end_col)

    def get_chess_notation(self):
        if self.piece_moved[1] == "P":
            notation = self.get_rank_file(self.start_row, self.start_col) + " to " + \
                   self.get_rank_file(self.end_row, self.end_col)
        elif self.piece_captured != "--":
            notation = self.piece_moved[1] + self.get_rank_file(self.start_row, self.start_col) + " to " + \
                       self.piece_captured[1] + self.get_rank_file(self.end_row, self.end_col)
        else:
            notation = self.piece_moved[1] + self.get_rank_file(self.start_row, self.start_col) + " to " + \
                       self.get_rank_file(self.end_row, self.end_col)

        return notation

    def get_rank_file(self, row, col):
        return self.cols_to_files[col] + self.rows_to_ranks[row]


class Castle:
    def __init__(self, wks, wqs, bks, bqs):
        self.wks = wks
        self.wqs = wqs
        self.bks = bks
        self.bqs = bqs