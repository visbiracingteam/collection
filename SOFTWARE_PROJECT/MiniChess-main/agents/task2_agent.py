import numpy as np
import random
from minichess.chess.fastchess import Chess
from minichess.chess.fastchess_utils import piece_matrix_to_legal_moves
from agents.base_agent import BaseAgent

class Task2Agent(BaseAgent):
    def __init__(self, name="Task2Agent"):
        super().__init__(name)
        
        self.piece_values = np.array([1, 3, 3, 5, 9, 10])

    def eval_board(self, turn, board: Chess):
        
        def find_pawn(self, turn: bool):
            """Returns the position of the king. (i, j)"""
            return board.bit_pos(self.bitboards[turn, 0])
        
        material_score = 0
        for color in [0, 1]:
            sign = 1 if color == turn else -1
            for piece_type in range(4):
                piece_board = board.bitboards[color, piece_type]
                count = bin(int(piece_board)).count('1') # Compatible bit_count
                val = self.piece_values[piece_type] * count
                material_score += sign * val

        pawn_score = 0                
        (pi, pj) = find_pawn(board, turn)
        if (pi, pj):
            if turn==0:
                pawn_score += (pj-1)/5
            else:
                pawn_score += (3-pj)/5
        return material_score + pawn_score


    def move(self, chess_obj: Chess):

        def find_pawn(self, turn: bool):
            """Returns the position of the king. (i, j)"""
            return self.bit_pos(self.bitboards[turn, 0])


        moves, proms = chess_obj.legal_moves()
        legal_moves = piece_matrix_to_legal_moves(moves, proms)
        if not legal_moves:
            return None

        original_turn = chess_obj.turn
        best_val = -10000
        best_move = random.choice(legal_moves)
        (i, j) = find_pawn(chess_obj, original_turn)
        if (i, j):
            for dx in [1, -1]:
                for dy in [1, -1]:
                    if ((i, j), (dx, dy), -1) in legal_moves:
                        return ((i, j), (dx, dy), -1)

        for (i, j), (dx, dy), promo in legal_moves:
            if promo != -1: promo = 4
            t1 = chess_obj.copy()
            t1.make_move(i, j, dx, dy, promo)  # Our First move
            depth1_val = self.eval_board(original_turn, t1)

            m2, p2 = t1.legal_moves()
            opp_moves = piece_matrix_to_legal_moves(m2, p2)

            if not opp_moves:
                res = t1.game_result() 
                if res == 0:
                    val = 0 # Draw (stalemate)
                elif (res == 1 and original_turn == 1) or \
                     (res == -1 and original_turn == 0):
                    val = 10000 # We won
                else:
                    val = -10000 # We lost

            else:
                vals = []
                for (i2, j2), (dx2, dy2), promo2 in opp_moves:
                    t2 = t1.copy()
                    t2.make_move(i2, j2, dx2, dy2, promo2)  # Opponent First move
                    depth2_val = self.eval_board(original_turn, t2)
                    if vals and (depth2_val - min(vals)) >= 0:
                        vals.append(depth2_val)
                        continue

                    m3, p3 = t2.legal_moves()
                    legal_moves2 = piece_matrix_to_legal_moves(m3, p3)
                    if not legal_moves2:
                        best_val2 = -10000  
                        vals.append(best_val2) # Add this to the list for the 'min' step
                        continue # Continue to the next opponent move


                    vals2 = []
                    for (i3, j3), (dx3, dy3), promo3 in legal_moves2:
                        t3 = t2.copy()
                        t3.make_move(i3, j3, dx3, dy3, promo3)
                        depth3_val = self.eval_board(original_turn, t3)
                        if vals2 and (max(vals2) - depth3_val) >= 0:
                            vals2.append(depth3_val)
                            continue
                        m4, p4 = t3.legal_moves()
                        opp_moves2 = piece_matrix_to_legal_moves(m4, p4)

                        if not opp_moves2:
                            res2 = t3.game_result() 
                            if res2 == 0:
                                val3 = 0 # Draw (stalemate)
                            elif (res2 == 1 and original_turn == 1) or \
                                (res2 == -1 and original_turn == 0):
                                val3 = 10000 # We won
                            else:
                                val3 = -10000 # We lost
                            vals2.append(val3)

                        else:
                            vals3 = []
                            for (i4, j4), (dx4, dy4), promo4 in opp_moves2:
                                t4 = t3.copy()
                                t4.make_move(i4, j4, dx4, dy4, promo4)
                                vals3.append(self.eval_board(original_turn, t4))
                            val3 = min(vals3)
                            vals2.append(val3)

                    val2 = max(vals2)
                    vals.append(val2)
                val = min(vals) 

            if val > best_val:
                best_val = val
                best_move = ((i, j), (dx, dy), promo)

            if best_val > 15:  # very good position
                break

        return best_move
    