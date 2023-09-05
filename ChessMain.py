"""
Driver file, handle user input and display the state of the game
"""
import pygame as p
import ChessEngine
import ChessAI


width = height = 480
dimension = 8
sq_size = height // dimension
transparency = 100
transparency_color = 'blue'
highlight_color = 'yellow'
max_fps = 15
images = {}
names = {}


'''
Initialize a global dictionary of images and populate dictionary
'''


def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR", "bP",
              "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR", "wP"]

    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (sq_size, sq_size))


def createNames(pieces):
    full_names = ["Black Rook", "Black Knight", "Black Bishop", "Black Queen", "Black Queen",
                  "Black King", "Black Knight", "Black Rook", "Black Pawn",
                  "White Rook", "White Knight", "White Bishop", "White Queen", "White Queen",
                  "White King", "White Knight", "White Rook", "White Pawn"]

    for i in range(len(pieces)):
        names[pieces[i]] = full_names[i]


'''
Main driver for code, this will handle user input and updating graphics
'''


def main():
    p.init()
    screen = p.display.set_mode((width, height))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    valid_moves = gs.get_valid_moves()
    move_made = False
    animate = False
    game_done = False

    loadImages()

    sq_selected = ()
    player_clicks = []

    player_one = True  # White - True if human
    player_two = False  # Black

    running = True
    while running:
        human_turn = (gs.whiteToMove and player_one) or (not gs.whiteToMove and player_two)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False

            # Undo moves and reset game
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()

                    move_made = True
                    animate = False
                    game_done = False
                elif e.key == p.K_r:
                    gs = ChessEngine.GameState()
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False
                    game_done = False

            # Select square and move piece
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_done and human_turn:
                    location = p.mouse.get_pos()
                    col = location[0] // sq_size
                    row = location[1] // sq_size

                    if sq_selected == (row, col):
                        sq_selected = ()
                        player_clicks = []
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)

                    if len(player_clicks) == 2:
                        move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])
                                print(move.get_chess_notation())
                                move_made = True
                                animate = True
                                sq_selected = ()
                                player_clicks.clear()

                        if not move_made:
                            player_clicks = [sq_selected]

        # AI moves
        if not game_done and not human_turn:
            AI_move = ChessAI.nega_max_alphaBeta_helper(gs, valid_moves)
            if AI_move is None:
                AI_move = ChessAI.find_random_move(valid_moves)
            gs.make_move(AI_move)
            move_made = True
            animate = True

        if move_made:
            if animate:
                animate_move(gs.moveLog[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()
            move_made = False

        drawGameState(screen, gs, valid_moves, sq_selected)
        if gs.checkmate:
            game_done = True
            if gs.whiteToMove:
                draw_text(screen, 'Black wins by checkmate')
            else:
                draw_text(screen, 'White wins by checkmate')

        elif gs.stalemate:
            game_done = True
            draw_text(screen, "Stalemate")

        clock.tick(max_fps)
        p.display.flip()


'''
Highlight Squares
'''


def highlight_squares(screen, gs, valid_moves, sq_selected):
    if sq_selected != ():
        r, c = sq_selected
        enemy_color = ('b' if gs.whiteToMove else 'w')
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # highlight selected square
            s = p.Surface((sq_size, sq_size))
            s.set_alpha(transparency)
            s.fill(p.Color(transparency_color))
            screen.blit(s, (c*sq_size, r*sq_size))

            # highlight moves
            s.fill(p.Color(highlight_color))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (sq_size*move.end_col, sq_size*move.end_row))


'''
Animation
'''


def animate_move(move, screen, board, clock):
    global colors
    dR = move.end_row - move.start_row
    dC = move.end_col - move.start_col
    frames_per_square = 3
    frames = frames_per_square * (abs(dR) + abs(dC))
    for frame in range(frames + 1):
        r, c = (move.start_row + dR * frame / frames, move.start_col + dC * frame / frames)
        drawBoard(screen)
        drawPieces(screen, board)

        color = colors[(move.end_col + move.end_col) % 2]
        end_square = p.Rect(move.end_col * sq_size, move.end_row * sq_size, sq_size, sq_size)
        p.draw.rect(screen, color, end_square)

        if move.piece_captured != '--':
            if move.en_passant_move:
                en_passant_row = (move.end_row + 1) if move.piece_captured[0] == 'b' else (move.end_row - 1)
                end_square = p.Rect(move.end_col * sq_size, en_passant_row * sq_size, sq_size, sq_size)
            screen.blit(images[move.piece_captured], end_square)
        if move.piece_moved != '--':
            screen.blit(images[move.piece_moved], p.Rect(c*sq_size, r*sq_size, sq_size, sq_size))
        p.display.flip()
        clock.tick(60)


'''
Draws endgame text
'''


def draw_text(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    text_object = font.render(text, False, p.Color('Gray'))
    text_loc = p.Rect(0, 0, width, height)\
        .move(width/2 - text_object.get_width()/2, height/2 - text_object.get_height()/2)
    screen.blit(text_object, text_loc)
    text_object = font.render(text, False, p.Color('Black'))
    screen.blit(text_object, text_loc.move(2, 2))


'''
Draws the squares and pieces on the board, draws current game state graphics
'''


def drawGameState(screen, gs, valid_moves, sq_selected):
    drawBoard(screen)  # Draw squares
    highlight_squares(screen, gs, valid_moves, sq_selected)
    drawPieces(screen, gs.board)  # Draw pieces


def drawBoard(screen):
    global colors
    colors = [p.Color("white"), p.Color("gray")]
    for row in range(dimension):
        for col in range(dimension):
            color = colors[((row+col) % 2)]
            p.draw.rect(screen, color, p.Rect(col*sq_size, row*sq_size, sq_size, sq_size))


def drawPieces(screen, board):
    for row in range(dimension):
        for col in range(dimension):
            piece = board[row][col]
            if piece != '--':
                screen.blit(images[piece], p.Rect(col*sq_size, row*sq_size, sq_size, sq_size))


if __name__ == "__main__":
    main()