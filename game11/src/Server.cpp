// server.cpp
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <iostream>
#include <string>
#include <thread>
#include <vector>
#include <mutex>
#include <chrono>
#include <conio.h>

#pragma comment(lib, "ws2_32.lib")

const int WIDTH = 80;
const int HEIGHT = 25;
const int PADDLE_HEIGHT = 5;
const int BALL_SPEED = 2;

struct Ball {
    int x, y;
    int dx, dy;
};

struct Player {
    int y;
    int score;
    int paddleY;
    bool ready;
};

class PongGame {
private:
    SOCKET serverSocket;
    SOCKET clientSockets[2];
    bool gameRunning;
    std::mutex gameMutex;
    Ball ball;
    Player players[2];
    int connectedPlayers;
    bool gameStarted;

public:
    PongGame() : gameRunning(true), connectedPlayers(0), gameStarted(false) {
        ball = {WIDTH/2, HEIGHT/2, BALL_SPEED, BALL_SPEED};
        players[0] = {HEIGHT/2, 0, HEIGHT/2 - PADDLE_HEIGHT/2, false};
        players[1] = {HEIGHT/2, 0, HEIGHT/2 - PADDLE_HEIGHT/2, false};
        clientSockets[0] = INVALID_SOCKET;
        clientSockets[1] = INVALID_SOCKET;
    }

    bool initializeServer(int port) {
        WSADATA wsaData;
        if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
            std::cerr << "WSAStartup failed\n";
            return false;
        }

        serverSocket = socket(AF_INET, SOCK_STREAM, 0);
        if (serverSocket == INVALID_SOCKET) {
            std::cerr << "Socket creation failed\n";
            return false;
        }

        sockaddr_in serverAddr;
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_addr.s_addr = INADDR_ANY;
        serverAddr.sin_port = htons(port);

        if (bind(serverSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
            std::cerr << "Bind failed\n";
            return false;
        }

        if (listen(serverSocket, 2) == SOCKET_ERROR) {
            std::cerr << "Listen failed\n";
            return false;
        }

        std::cout << "Server started on port " << port << "\n";
        std::cout << "Waiting for players to connect...\n";
        return true;
    }

    void acceptPlayers() {
        while (connectedPlayers < 2 && gameRunning) {
            SOCKET client = accept(serverSocket, NULL, NULL);
            if (client != INVALID_SOCKET) {
                std::lock_guard<std::mutex> lock(gameMutex);
                int playerId = connectedPlayers;
                clientSockets[playerId] = client;
                connectedPlayers++;
                
                std::string msg = "Connected as Player " + std::to_string(playerId + 1) + "\n";
                send(client, msg.c_str(), msg.length(), 0);
                
                std::cout << "Player " << (playerId + 1) << " connected\n";
                
                if (connectedPlayers == 2) {
                    gameStarted = true;
                    std::cout << "Both players connected! Game starting...\n";
                }
            }
        }
    }

    void sendGameState() {
        std::lock_guard<std::mutex> lock(gameMutex);
        std::string state = std::to_string(ball.x) + "," + 
                           std::to_string(ball.y) + "," +
                           std::to_string(players[0].paddleY) + "," +
                           std::to_string(players[1].paddleY) + "," +
                           std::to_string(players[0].score) + "," +
                           std::to_string(players[1].score) + "\n";

        for (int i = 0; i < 2; i++) {
            if (clientSockets[i] != INVALID_SOCKET) {
                send(clientSockets[i], state.c_str(), state.length(), 0);
            }
        }
    }

    void updateGame() {
        if (!gameStarted) return;

        // Move ball
        ball.x += ball.dx;
        ball.y += ball.dy;

        // Ball collision with top/bottom walls
        if (ball.y <= 0 || ball.y >= HEIGHT - 1) {
            ball.dy = -ball.dy;
        }

        // Ball collision with paddles
        // Left paddle (Player 1)
        if (ball.x <= 2 && ball.y >= players[0].paddleY && 
            ball.y <= players[0].paddleY + PADDLE_HEIGHT) {
            ball.dx = -ball.dx;
            ball.x = 3;
        }
        // Right paddle (Player 2)
        else if (ball.x >= WIDTH - 3 && ball.y >= players[1].paddleY && 
                 ball.y <= players[1].paddleY + PADDLE_HEIGHT) {
            ball.dx = -ball.dx;
            ball.x = WIDTH - 4;
        }

        // Scoring
        if (ball.x < 0) {
            players[1].score++;
            resetBall();
        } else if (ball.x > WIDTH) {
            players[0].score++;
            resetBall();
        }

        // Move paddles automatically for AI (or you can use player input)
        // For simplicity, we'll let players control via network messages
    }

    void resetBall() {
        ball.x = WIDTH/2;
        ball.y = HEIGHT/2;
        ball.dx = BALL_SPEED * (rand() % 2 ? 1 : -1);
        ball.dy = BALL_SPEED * (rand() % 2 ? 1 : -1);
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    void handlePlayerInput() {
        fd_set readSet;
        char buffer[1024];

        while (gameRunning) {
            FD_ZERO(&readSet);
            for (int i = 0; i < 2; i++) {
                if (clientSockets[i] != INVALID_SOCKET) {
                    FD_SET(clientSockets[i], &readSet);
                }
            }

            timeval timeout = {0, 100};
            int activity = select(0, &readSet, NULL, NULL, &timeout);

            if (activity > 0) {
                for (int i = 0; i < 2; i++) {
                    if (clientSockets[i] != INVALID_SOCKET && 
                        FD_ISSET(clientSockets[i], &readSet)) {
                        int bytes = recv(clientSockets[i], buffer, sizeof(buffer) - 1, 0);
                        if (bytes > 0) {
                            buffer[bytes] = '\0';
                            std::string input(buffer);
                            
                            std::lock_guard<std::mutex> lock(gameMutex);
                            if (input == "up" && players[i].paddleY > 0) {
                                players[i].paddleY--;
                            } else if (input == "down" && 
                                      players[i].paddleY < HEIGHT - PADDLE_HEIGHT) {
                                players[i].paddleY++;
                            }
                        }
                    }
                }
            }
        }
    }

    void gameLoop() {
        while (gameRunning) {
            std::this_thread::sleep_for(std::chrono::milliseconds(16)); // ~60 FPS
            
            std::lock_guard<std::mutex> lock(gameMutex);
            if (gameStarted) {
                updateGame();
                sendGameState();
            }
        }
    }

    void run() {
        std::thread acceptThread(&PongGame::acceptPlayers, this);
        std::thread inputThread(&PongGame::handlePlayerInput, this);
        std::thread gameThread(&PongGame::gameLoop, this);

        acceptThread.join();
        inputThread.join();
        gameThread.join();
    }

    ~PongGame() {
        gameRunning = false;
        for (int i = 0; i < 2; i++) {
            if (clientSockets[i] != INVALID_SOCKET) {
                closesocket(clientSockets[i]);
            }
        }
        closesocket(serverSocket);
        WSACleanup();
    }
};

int main() {
    srand(time(NULL));
    PongGame game;
    
    if (game.initializeServer(8080)) {
        game.run();
    }
    
    return 0;
}
