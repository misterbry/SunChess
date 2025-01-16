from stockfish import Stockfish

# Initialize Stockfish with the downloaded binary
stockfish = Stockfish("/usr/local/bin/stockfish")
stockfish.set_skill_level(10)

def main():
   print("Welcome to Chess! Enter your moves in algebraic notation Example: e3e4.")

   while True:
       print("\nCurrent Position:")
       print(stockfish.get_board_visual())

       # User move
       user_move = input("\nYour move: ").strip()
       if not stockfish.is_move_correct(user_move):
           print("Invalid move. Please try again.")
           continue
       stockfish.make_moves_from_current_position([user_move])

       # Check if the game is over
       # if stockfish.is_game_over():
       #     print("\nGame Over!")
       #     print(stockfish.get_evaluation())
       #     break

       # Bot move
       print("\nBot is thinking...")
       bot_move = stockfish.get_best_move()
       stockfish.make_moves_from_current_position([bot_move])
       print(f"Bot moves: {bot_move}")

if __name__ == "__main__":
   main()
