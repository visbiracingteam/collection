# gameplay_ascii.py
import time
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_frame(ball_x, ball_y, paddle1_y, paddle2_y, score1, score2):
    WIDTH = 50
    HEIGHT = 15
    PADDLE_HEIGHT = 4
    
    frame = ""
    # Top border
    frame += "+" + "-" * WIDTH + "+\n"
    
    for y in range(HEIGHT):
        frame += "|"
        for x in range(WIDTH):
            # Ball
            if x == ball_x and y == ball_y:
                frame += "●"
            # Left paddle (Player 1)
            elif x == 0 and paddle1_y <= y < paddle1_y + PADDLE_HEIGHT:
                frame += "█"
            # Right paddle (Player 2)
            elif x == WIDTH - 1 and paddle2_y <= y < paddle2_y + PADDLE_HEIGHT:
                frame += "█"
            # Middle net
            elif x == WIDTH // 2 and y % 2 == 0:
                frame += "│"
            else:
                frame += " "
        frame += "|\n"
    
    # Bottom border
    frame += "+" + "-" * WIDTH + "+\n"
    frame += f"Player 1: {score1}  |  Player 2: {score2}\n"
    frame += "Controls: Player 1 (W/S)  Player 2 (Up/Down Arrow)\n"
    
    return frame

def simulate_gameplay():
    # Initial positions
    ball_x, ball_y = 25, 7
    dx, dy = 1, 1
    paddle1_y, paddle2_y = 5, 5
    score1, score2 = 0, 0
    frame_count = 0
    
    while True:
        clear_screen()
        
        # Ball movement
        ball_x += dx
        ball_y += dy
        
        # Wall collisions
        if ball_y <= 0 or ball_y >= 14:
            dy = -dy
        
        # Paddle collisions
        if ball_x <= 1 and paddle1_y <= ball_y < paddle1_y + 4:
            dx = -dx
            ball_x = 2
        elif ball_x >= 48 and paddle2_y <= ball_y < paddle2_y + 4:
            dx = -dx
            ball_x = 47
        
        # Scoring
        if ball_x < 0:
            score2 += 1
            ball_x, ball_y = 25, 7
            dx = 1
            dy = 1 if ball_y < 7 else -1
        elif ball_x > 49:
            score1 += 1
            ball_x, ball_y = 25, 7
            dx = -1
            dy = 1 if ball_y < 7 else -1
        
        # AI paddle movement (simple)
        if ball_y < paddle1_y + 2 and paddle1_y > 0:
            paddle1_y -= 1
        elif ball_y > paddle1_y + 2 and paddle1_y < 11:
            paddle1_y += 1
            
        if ball_y < paddle2_y + 2 and paddle2_y > 0:
            paddle2_y -= 1
        elif ball_y > paddle2_y + 2 and paddle2_y < 11:
            paddle2_y += 1
        
        # Display frame
        frame = create_frame(ball_x, ball_y, paddle1_y, paddle2_y, score1, score2)
        print(frame)
        print(f"Frame: {frame_count} | Press Ctrl+C to quit")
        
        time.sleep(0.1)
        frame_count += 1
        
        # End after 20 frames for demo
        if frame_count > 200:
            break

if __name__ == "__main__":
    try:
        simulate_gameplay()
    except KeyboardInterrupt:
        print("\nGame ended.")
