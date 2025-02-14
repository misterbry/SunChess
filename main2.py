import pygame
import chess
import chess.engine
import chess.polyglot
from time import sleep
from web3_connect import *
import menu
from random import randint

# Set window position
os.environ['SDL_VIDEO_WINDOW_POS'] = "900,30"
# Initialize Pygame
pygame.init()
# WIDTH, HEIGHT = 480, 480
WIDTH, HEIGHT = 1020, 1020
SQUARE_SIZE = WIDTH // 8
WHITE = (255, 255, 255)
BLACK = (118, 150, 86)
LIGHT_SQUARE = (238, 238, 210)
DARK_SQUARE = (118, 150, 86)
HIGHLIGHT_COLOR = (186, 202, 68)


# Load chessboard images
PIECES_IMAGES = {}
piece_switch = {'p': 'bp', 'r': 'br', 'n': 'bn', 'b': 'bb', 'q': 'bq', 'k': 'bk', 'P': 'wp', 'R': 'wr', 'N': 'wn', 'B': 'wb', 'Q': 'wq', 'K': 'wk'}
for piece in ['bp', 'br', 'bn', 'bb', 'bq', 'bk', 'wp', 'wr', 'wn', 'wb', 'wq', 'wk']:
   PIECES_IMAGES[piece] = pygame.image.load(f"assets/{piece}.png")
   PIECES_IMAGES[piece] = pygame.transform.scale(PIECES_IMAGES[piece], (SQUARE_SIZE, SQUARE_SIZE))

opponents = {0: "Glassjaw Joe", 1: "Von Kaiser", 2: "Piston Honda", 3: "Don Flamenco", 4: "King Hippo", 5: "Great Tiger", 6: "Bald Bull", 7: "Piston Honda", 8: "Soda Popinski", 9: "Bald Bull", 10: "Don Flamenco", 11: "Mr. Sandman", 12: "Super Macho Man", 13: "Mike Tyson", 14: "Mr. Bryan"}

start_pos = {
   "default": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
   "b_king_only": "4k3/8/8/8/8/8/PPPPPPPP/RNBQKBNR w KQ - 0 1",
   "e4e5": "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"}

# Initialize Chess Board
# board = chess.Board("rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2") ## fen string can be argument
board = chess.Board(start_pos["default"]) ## fen string can be argument

# print(dir(board))

# Initialize Stockfish
# komodo = "/Users/Bryan/Downloads/dragon-osx"
stockfish = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
book_path = "/home/misterbry/Desktop/ChessBot/gm2001.bin"
# stockfish = chess.engine.SimpleEngine.popen_uci(komodo) ## komodo engine
# stockfish.configure({"UCI_LimitStrength": True, "UCI_Elo": 1350})


def draw_board(screen, selected_square=None, last_move=None):
   """Draws the chessboard on the Pygame screen."""
   for row in range(8):
      for col in range(8):
         color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
         square = chess.square(col, 7 - row)
         if selected_square == square or last_move == square:
            color = HIGHLIGHT_COLOR
               
         pygame.draw.rect(screen, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces(screen, board):
   """Draws chess pieces on the board."""
   board_str = board.board_fen()
   for row, line in enumerate(board_str.split("/")):
      col = 0
      for char in line:
         if char.isdigit():
            col += int(char)
         else:
            piece_image = PIECES_IMAGES[piece_switch[char]]
            # piece_image = pygame.transform.scale(PIECES_IMAGES[char], (SQUARE_SIZE, SQUARE_SIZE))
            screen.blit(piece_image, (col * SQUARE_SIZE, row * SQUARE_SIZE))
            col += 1

def get_square_under_mouse():
   """Returns the board square under the mouse pointer."""
   mouse_x, mouse_y = pygame.mouse.get_pos()
   col = mouse_x // SQUARE_SIZE
   row = mouse_y // SQUARE_SIZE
   return chess.square(col, 7 - row)

def noob():
    # Collect user input
    password = getpass("It looks like this is your first time here. Please enter a password >>> ")

    # Generate a salt and derive a key from the password
    salt = os.urandom(16)
    key = derive_key(password, salt)

    # Create a new Ethereum wallet
    web3 = Web3()
    account = web3.eth.account.create()
    wallet_data = account._private_key.hex()

    # Encrypt the wallet
    encrypted_wallet = encrypt_wallet(key, wallet_data)

    # Save the salt and encrypted wallet to the .env file
    initial_setup("WALLET_SALT", base64.b64encode(salt).decode('utf-8'))
    initial_setup("ENCRYPTED_WALLET", base64.b64encode(encrypted_wallet).decode('utf-8'))
    initial_setup("USER_ADDRESS", account.address)
    print(f"Welcome aboard. Your new address is {account.address}.")

def promo_menu(screen):
   screen.fill((255, 255, 255))
   options = ["Queen", "Rook", "Bishop", "Knight"]
   font = pygame.font.Font(None, 36)
   for i, option in enumerate(options):
      text = font.render(option, True, (0, 0, 0))
      screen.blit(text, (WIDTH // 2 - text.get_width() // 2, 100 + i * 50))
      pygame.display.flip()

def is_promotion(move, board):
   piece = board.piece_at(move.from_square)
   if piece and piece.piece_type == chess.PAWN:
      legal_moves = [str(x) for x in board.legal_moves]
      move_string = str(move)
      if chess.square_rank(move.to_square) == (7 if piece.color == chess.WHITE else 0) and chess.square_rank(move.from_square) == (6 if piece.color == chess.WHITE else 0):
         for i in legal_moves:
            try:
               if i[2:4] == move_string[2:]:
                  return True
            except Exception:
               continue
   return False

def handle_promo():
   while True:
      for event in pygame.event.get():
         if event.type == pygame.QUIT:
            pygame.quit()
            exit()
         elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if 100 <= y < 150:
               print(chess.QUEEN)
               return chess.QUEEN
            elif 150 <= y < 200:
               return chess.ROOK
            elif 200 <= y < 250:
               return chess.BISHOP
            elif 250 <= y < 300:
               return chess.KNIGHT
   
                  
def main(account, player):
    i = 0
    # address = os.getenv("USER_ADDRESS")
    address = account.address
    dev_address = os.getenv("DEV_ADDRESS")
    # player = contract.functions.getPlayer(address).call()
    skill_level = int(player[6])
    os.system("clear")
    print(f"Playing {opponents[skill_level]}, level {skill_level}")
    print("-" * len(opponents[skill_level]) + "-" * 18)
    sleep(2)
    stockfish.configure({"Skill Level": skill_level})
    current_skill = stockfish.options["Skill Level"]
    
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(opponents[skill_level])
    clock = pygame.time.Clock()
    selected_square = None
    running = True

    while running:
        #pygame.event.set_grab(False)
        #pygame.event.set_grab(True)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                square = get_square_under_mouse()
                if selected_square is None:
                    # Select a square
                    selected_square = square
                else:
                    # Try to move piece
                    move = chess.Move(from_square=selected_square, to_square=square)
                    # print(move.uci())
                    # move_from_uci = chess.Move.from_uci(move.uci())
                    # print("PROMOTION:", move_from_uci.promotion)
                    if move in board.legal_moves:
                        i += 1
                        print(f"{i}. {board.san(move)}...", end='')
                        board.push(move)
                        selected_square = None

                        # Redraw board after player move
                        if board.is_checkmate():
                            pygame.display.set_caption("Checkmate! You Win :)")
                            print("Checkmate! Nicely done!")
                            draw_board(screen)
                            draw_pieces(screen, board)
                            pygame.display.flip()
                            sleep(2)
                            pygame.display.set_caption("Transacting, please wait...")
                            draw_board(screen)
                            draw_pieces(screen, board)
                            pygame.display.flip()
                            receipt = menu.contract_tx(w3, account, contract, "gameWin")
                            pygame.display.set_caption("Congratulations! Level up.")
                            draw_board(screen)
                            draw_pieces(screen, board)
                            pygame.display.flip()
                            running = False
                            continue
                         
                        draw_board(screen)
                        draw_pieces(screen, board)
                        pygame.display.flip()
                        # Delay before bot move
                        sleep(1)
                        # Stockfish's turn
                        analysis = stockfish.analyse(board, chess.engine.Limit(depth=4, time=1), multipv=3)
                        # print(analysis)
                        best_move = None
                        try:
                           best_move = analysis[0]['pv'][0].uci()
                        except Exception:
                           print("Stalemate!")
                           exit()
                        move_obj = None
                        try:
                           second_best_move = analysis[1]['pv'][0].uci()
                           third_best_move = analysis[2]['pv'][0].uci()
                           # move = analysis[randint(0, 2)]['pv'][0].uci()
                           move_obj = chess.Move.from_uci(third_best_move)
                           # print(third_best_move)
                        except IndexError:
                           move_obj = chess.Move.from_uci(best_move)
                           print("EXCEPTION")
                        
                        #result = stockfish.play(board, chess.engine.Limit(time=1.0, depth=1, nodes=100000))
                        # weakened_move = sorted(analysis["pv"])[1]
                        # print(result.move)
                        # board.push(result.move)
                        try:
                           with chess.polyglot.open_reader(book_path) as reader:
                              # print("DEBUG:", list(reader.find_all(board)))
                              book_move_count = len(list(reader.find_all(board)))
                              # print("Book moves available:", book_move_count)
                              book_move = next(reader.find_all(board)).move
                              book_move_2 = list(reader.find_all(board))[randint(0, book_move_count)].move
                              print(board.san(book_move_2))
                              board.push(book_move_2)
                              print("Book Move")
                        except Exception:
                           print(board.san(move_obj))
                           board.push(move_obj)
                           print("No more book moves")
                        # board.push(weakened_move)
                        if board.is_checkmate():
                            pygame.display.set_caption("Checkmate! You Lose :(")
                            sleep(2)
                            running = False
                            print("You have been checkmated :(\nBetter luck next time!")
                            continue
                    elif is_promotion(move, board):
                       promo_menu(screen)
                       promo_piece = handle_promo()
                       move.promotion = promo_piece
                       print(board.san(move))
                       board.push(move)
                       selected_square = None
                        # Redraw board after player move
                       if board.is_checkmate():
                           pygame.display.set_caption("Checkmate! You Win :)")
                           print("Checkmate! You Win :)")
                           draw_board(screen)
                           draw_pieces(screen, board)
                           pygame.display.flip()
                           sleep(2)
                           pygame.display.set_caption("Transacting, please wait...")
                           draw_board(screen)
                           draw_pieces(screen, board)
                           pygame.display.flip()
                           receipt = menu.contract_tx(w3, account, contract, "gameWin")
                           pygame.display.set_caption("Congratulations! Level up.")
                           draw_board(screen)
                           draw_pieces(screen, board)
                           pygame.display.flip()
                           break
                       draw_board(screen)
                       draw_pieces(screen, board)
                       pygame.display.flip()
                       # Delay before bot move
                       sleep(1)
                       # Stockfish's turn
                       analysis = stockfish.analyse(board, chess.engine.Limit(depth=2), multipv=3)
                       # print(analysis)
                       best_move = analysis[0]['pv'][0].uci()
                       move_obj = None
                       try:
                          second_best_move = analysis[1]['pv'][0].uci()
                          third_best_move = analysis[2]['pv'][0].uci()
                          move = analysis[randint(0, 2)]['pv'][0].uci()
                          move_obj = chess.Move.from_uci(second_best_move)
                          # print(third_best_move)
                       except IndexError:
                          move_obj = chess.Move.from_uci(best_move)

                       #result = stockfish.play(board, chess.engine.Limit(time=1.0, depth=1, nodes=100000))
                       # weakened_move = sorted(analysis["pv"])[1]
                       # print(result.move)
                       # board.push(result.move)
                       try:
                          with chess.polyglot.open_reader(book_path) as reader:
                             book_move = next(reader.find_all(board)).move
                             print(board.san(book_move))
                             board.push(book_move)
                             print("Book Move")
                       except Exception:
                          print(board.san(move_obj))
                          board.push(move_obj)
                          print("No more book moves")                       
                       # board.push(move_obj)
                       # board.push(weakened_move)
                       if board.is_checkmate():
                           pygame.display.set_caption("Checkmate! You Lose :(")
                           break                       
                    else:
                        selected_square = None
                        # print("Move not legal")
                        # print(move)
                        
            # elif event.type == pygame.VIDEORESIZE:
            #     WIDTH, HEIGHT = event.w, event.h
            #     SQUARE_SIZE = min(WIDTH, HEIGHT) // 8
            #     screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        # Draw the board and pieces
        draw_board(screen, selected_square=selected_square)
        draw_pieces(screen, board)

        pygame.display.flip()
        clock.tick(60)

    stockfish.quit()
    pygame.quit()

if __name__ == "__main__":
    player = execute() ## returns (account, player)
    if player != 1:
        main(player[0], player[1])
    else:
        print("Try again later.")
        exit()
   # get_promotion_choice()

   
