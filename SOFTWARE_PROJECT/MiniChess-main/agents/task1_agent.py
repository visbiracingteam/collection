import numpy as np
import random
from minichess.chess.fastchess import Chess
from minichess.chess.fastchess_utils import piece_matrix_to_legal_moves
from agents.base_agent import BaseAgent

class Task1Agent(BaseAgent):
    def __init__(self, name="Task1Agent"):
        super().__init__(name)
        self.piece_values = np.array([1, 3, 3, 5, 9, 100])

    def eval_board(self, turn, board: Chess):
        """Faster material evaluation using bitboards."""
        score = 0
        for color in [0, 1]:
            sign = 1 if color == turn else -1
        
            for piece_type in range(5):
                piece_board = board.bitboards[color, piece_type]
                count = piece_board.bit_count()
                val = self.piece_values[piece_type] * count
                score += sign * val
        return score

    def move(self, chess_obj: Chess):
        moves, proms = chess_obj.legal_moves()
        legal_moves = piece_matrix_to_legal_moves(moves, proms)
        if not legal_moves:
            return None

        original_turn = chess_obj.turn
        best_val = -1000
        best_move = random.choice(legal_moves)

        for (i, j), (dx, dy), promo in random.sample(legal_moves, k = int(len(legal_moves)//2.5+1)):
            temp = chess_obj.copy()
            temp.make_move(i, j, dx, dy, promo)

            depth1_val = self.eval_board(original_turn, temp)
            if depth1_val <= -1:
                best_val = depth1_val
                continue
            
            m2, p2 = temp.legal_moves()
            opp_moves = piece_matrix_to_legal_moves(m2, p2)

            if not opp_moves:
                res = temp.game_result() 
                if res == 0:
                    val = 0 # Draw (stalemate)
                elif (res == 1 and original_turn == 1) or \
                     (res == -1 and original_turn == 0):
                    val = 1000 # We won
                else:
                    val = -1000 # We lost

            else:
                vals = []
                for (i2, j2), (dx2, dy2), promo2 in random.sample(opp_moves, k = int(len(opp_moves)//1.5+1)):
                    t2 = temp.copy()
                    t2.make_move(i2, j2, dx2, dy2, promo2)
                    vals.append(self.eval_board(original_turn, t2))
                val = min(vals)

            if val > best_val:
                best_val = val
                best_move = ((i, j), (dx, dy), promo)

            if best_val > 14:  # very good position
                break

        return best_move

