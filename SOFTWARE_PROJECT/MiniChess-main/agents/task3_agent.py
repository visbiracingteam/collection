import numpy as np
import random
from minichess.chess.fastchess import Chess
from minichess.chess.fastchess_utils import piece_matrix_to_legal_moves, true_bits, unflat, inv_color, flat, set_bit, unset_bit
from agents.base_agent import BaseAgent

class Task3Agent(BaseAgent):
    def __init__(self, name="Task3Agent"):
        super().__init__(name)
        
        self.piece_values = np.array([2, 3, 3, 5, 9])

    def unmake_move(self, board: Chess,
                     i: np.uint8, j: np.uint8, dx: np.int8, dy: np.int8, promotion: int,
                     piece_at: int, captured_piece: int, old_ply_count: int):

        board.half_move_count -= 1
        board.ply_count_without_adv = old_ply_count
        board.turn = inv_color(board.turn) 
        
        moved_piece_type = promotion if promotion != -1 else piece_at
        f_from = flat(i, j, board.dims)
        f_to = flat(i + dx, j + dy, board.dims)

        board.bitboards[board.turn, moved_piece_type] = unset_bit(board.bitboards[board.turn, moved_piece_type], f_to)
        board.piece_lookup[board.turn, i + dx, j + dy] = -1
        
        board.bitboards[board.turn, piece_at] = set_bit(board.bitboards[board.turn, piece_at], f_from)
        board.piece_lookup[board.turn, i, j] = piece_at
            
        if captured_piece != -1:
            enemy_turn = inv_color(board.turn)
            board.bitboards[enemy_turn, captured_piece] = set_bit(board.bitboards[enemy_turn, captured_piece], f_to)
            board.piece_lookup[enemy_turn, i + dx, j + dy] = captured_piece
            
        board.legal_move_cache = None
        board.has_legal_moves = False

    def eval_board(self, turn, board: Chess):
        def find_pawn(self, turn: bool):
            """Returns the position of the king. (i, j)"""
            return board.bit_pos(self.bitboards[turn, 0])
        
        material_score = 0
        for color in [0, 1]:
            sign = 1 if color == turn else -1
            for piece_type in range(5):
                piece_board = board.bitboards[color, piece_type]
                count = bin(int(piece_board)).count('1') # Compatible bit_count
                val = self.piece_values[piece_type] * count
                material_score += sign * val

        # # --- 2. King-Hunter Bonuses ---
        king_mobility_score = 0
        king_edge_bonus = 0
        pawn_score = 0
        
        # This is our "trigger" to start the hunt.
        # We only apply these bonuses if we are up by at least a piece (3 points).
        if material_score >= 8: 
            
            opp_color = 1 - turn
            opp_king_bb = board.bitboards[opp_color, 5] # Assuming 5 is King
            
            (pi, pj) = find_pawn(board, turn)
            if (pi, pj):
                if turn==0:
                    pawn_score += (pj-1)*0.2

                else:
                    pawn_score += (3-pj)*0.2
            
            if opp_king_bb != 0:
                # --- a) King Mobility Penalty (Stronger) ---
                # Find king's position
                i, j = board.find_king(opp_color)
                
                # Get all squares the king *could* move to
                king_pseudo_moves = board.KING_MOVES[i, j]

                # Find squares the king *cannot* move to
                opp_pieces_bb = board.get_all_pieces(ignore_king=False, turns=[opp_color])
                my_attack_bb = board.get_attacked_squares(turn)
                king_legal_moves_bb = king_pseudo_moves & ~opp_pieces_bb & ~my_attack_bb
                num_legal_moves = bin(int(king_legal_moves_bb)).count('1')

                mobility_bonus = (8 - num_legal_moves) * 0.1
                king_mobility_score = mobility_bonus

                center_i = (board.dims[0]+1) / 2.0
                center_j = (board.dims[1]+1) / 2.0
                
                # Distance from center is high on edges, low in middle
                dist_from_center = abs(i - center_i) + abs(j - center_j)
                
                # We reward this distance with a small bonus
                king_edge_bonus = dist_from_center * .1

        # --- 3. Final Score ---
        return material_score + king_mobility_score + king_edge_bonus + pawn_score
    

    def move(self, chess_obj: Chess):     
        moves, proms = chess_obj.legal_moves()
        legal_moves = piece_matrix_to_legal_moves(moves, proms)
        if not legal_moves:
            return None

        original_turn = chess_obj.turn
        best_move = random.choice(legal_moves)
    
        best_val = -10000
        good_moves = []
       
        #  First Depth
        for (i, j), (dx, dy), promo in legal_moves:
            board = chess_obj
            piece_at1 = board.piece_at(i, j, board.turn)
            captured_piece1 = board.piece_at(i + dx, j + dy, inv_color(board.turn))
            old_ply_count1 = board.ply_count_without_adv
            board.make_move(i, j, dx, dy, promo)  # Our First move
            m2, p2 = board.legal_moves()
            opp_moves = piece_matrix_to_legal_moves(m2, p2)

            if not opp_moves:
                res = board.game_result() 
                if res == 0:
                    val = 0 # Draw (stalemate)
                else: 
                    return ((i, j), (dx, dy), promo)
                
            else:
                vals = []
                #  Second Depth
                for (i2, j2), (dx2, dy2), promo2 in opp_moves:
                    piece_at2 = board.piece_at(i2, j2, board.turn)
                    captured_piece2 = board.piece_at(i2 + dx2, j2 + dy2, inv_color(board.turn))
                    old_ply_count2 = board.ply_count_without_adv
                    board.make_move(i2, j2, dx2, dy2, promo2)  # Opponent First move
                    depth2_val = self.eval_board(original_turn, board)
                    
                    if vals and (depth2_val - min(vals)) >= -1:
                        vals.append(depth2_val)
                        self.unmake_move(board, i2, j2, dx2, dy2, promo2, piece_at2, captured_piece2, old_ply_count2)
                        continue

                    m3, p3 = board.legal_moves()
                    legal_moves2 = piece_matrix_to_legal_moves(m3, p3)
                    if not legal_moves2:
                        best_val2 = -10000  
                        vals.append(best_val2) # We got checkmate
                        self.unmake_move(board, i2, j2, dx2, dy2, promo2, piece_at2, captured_piece2, old_ply_count2)
                        continue 
                    vals2 = []

                    #  Third Depth
                    for (i3, j3), (dx3, dy3), promo3 in legal_moves2:
                        piece_at3 = board.piece_at(i3, j3, board.turn)
                        captured_piece3 = board.piece_at(i3 + dx3, j3 + dy3, inv_color(board.turn))
                        old_ply_count3 = board.ply_count_without_adv
                        board.make_move(i3, j3, dx3, dy3, promo3)
                        depth3_val = self.eval_board(original_turn, board)
                        if vals2 and (depth3_val - max(vals2)) < 0:
                            vals2.append(depth3_val)
                            self.unmake_move(board, i3, j3, dx3, dy3, promo3, piece_at3, captured_piece3, old_ply_count3)
                            continue
                            
                        m4, p4 = board.legal_moves()
                        opp_moves2 = piece_matrix_to_legal_moves(m4, p4)

                        if not opp_moves2:
                            res2 = board.game_result() 
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

                            #  Fourth Depth
                            for (i4, j4), (dx4, dy4), promo4 in opp_moves2:
                                piece_at4 = board.piece_at(i4, j4, board.turn)
                                captured_piece4 = board.piece_at(i4 + dx4, j4 + dy4, inv_color(board.turn))
                                old_ply_count4 = board.ply_count_without_adv
                                board.make_move(i4, j4, dx4, dy4, promo4)
                                depth4_val = self.eval_board(original_turn, board)
                                if depth4_val >= 8:                        
                                    if vals3 and (depth4_val - min(vals3)) >= 0:
                                        vals3.append(depth4_val)
                                        self.unmake_move(board, i4, j4, dx4, dy4, promo4, piece_at4, captured_piece4, old_ply_count4)
                                        continue

                                    m5, p5 = board.legal_moves()
                                    legal_moves3 = piece_matrix_to_legal_moves(m5, p5)
                                    if not legal_moves3: 
                                        vals3.append(-10000) # We got checkmate
                                        self.unmake_move(board, i4, j4, dx4, dy4, promo4, piece_at4, captured_piece4, old_ply_count4)
                                        continue 
                                    vals4 = []

                                    #  Fifth Depth
                                    for (i5, j5), (dx5, dy5), promo5 in legal_moves3:
                                        piece_at5 = board.piece_at(i5, j5, board.turn)
                                        captured_piece5 = board.piece_at(i5 + dx5, j5 + dy5, inv_color(board.turn))
                                        old_ply_count5 = board.ply_count_without_adv
                                        board.make_move(i5, j5, dx5, dy5, promo5)
                                        depth5_val = self.eval_board(original_turn, board)
                                        vals4.append(depth5_val)
                                        self.unmake_move(board, i5, j5, dx5, dy5, promo5, piece_at5, captured_piece5, old_ply_count5)
                                    vals3.append(max(vals4))
                                else: vals3.append(depth4_val)
                                vals3.append(depth4_val)
                                self.unmake_move(board, i4, j4, dx4, dy4, promo4, piece_at4, captured_piece4, old_ply_count4)

                            val3 = min(vals3)
                            vals2.append(val3)
                        self.unmake_move(board, i3, j3, dx3, dy3, promo3, piece_at3, captured_piece3, old_ply_count3)

                    val2 = max(vals2)
                    vals.append(val2)
                    self.unmake_move(board, i2, j2, dx2, dy2, promo2, piece_at2, captured_piece2, old_ply_count2)
                val = min(vals) 
                
            if val == best_val:
                good_moves.append(((i, j), (dx, dy), promo))

            elif val > best_val:
                best_val = val
                best_move = ((i, j), (dx, dy), promo)
                good_moves = []
            
            self.unmake_move(board, i, j, dx, dy, promo, piece_at1, captured_piece1, old_ply_count1)
        
        if len(good_moves) > 1:
            return random.choice(good_moves)

        return best_move
    