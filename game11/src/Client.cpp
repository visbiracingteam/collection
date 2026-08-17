// client.cpp
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>
#include <iostream>
#include <string>
#include <thread>
#include <chrono>
#include <conio.h>

#pragma comment(lib, "ws2_32.lib")

const int WIDTH = 80;
const int HEIGHT = 25;
const int PADDLE_HEIGHT = 5;

class PongClient {
private:
    SOCKET clientSocket;
    bool connected;
    int playerId;

public:
    PongClient() : connected(false), playerId(0) {}

    bool connectToServer(const std::string& serverIP, int port) {
        WSADATA wsaData;
        if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
            std::cerr << "WSAStartup failed\n";
            return false;
        }

        clientSocket = socket(AF_INET, SOCK_STREAM, 0);
        if (clientSocket == INVALID_SOCKET) {
            std::cerr << "Socket creation failed\n";
            return false;
        }

        sockaddr_in serverAddr;
        serverAddr.sin_family = AF_INET;
        serverAddr.sin_port = htons(port);
        inet_pton(AF_INET, serverIP.c_str(), &serverAddr.sin_addr);

        if (connect(clientSocket, (sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
            std::cerr << "Connection failed\n";
            return false;
        }

        connected = true;
        std::cout << "Connected to server\n";

        // Receive player ID
        char buffer[1024];
        int bytes = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);
        if (bytes > 0) {
            buffer[bytes] = '\0';
            std::cout << buffer;
            if (std::string(buffer).find("Player 1") != std::string::npos) {
                playerId = 1;
            } else {
                playerId = 2;
            }
        }

        return true;
    }

    void renderGame(const std::string& gameState) {
        system("cls");
        
        int ballX, ballY, paddle1Y, paddle2Y, score1, score2;
        sscanf(gameState.c_str(), "%d,%d,%d,%d,%d,%d", 
               &ballX, &ballY, &paddle1Y, &paddle2Y, &score1, &score2);

        // Draw top border
        std::cout << "+" << std::string(WIDTH, '-') << "+\n";
        
        for (int y = 0; y < HEIGHT; y++) {
            std::cout << "|";
            for (int x = 0; x < WIDTH; x++) {
                if (x == ballX && y == ballY) {
                    std::cout << "O";
                } else if (x == 0 && y >= paddle1Y && y < paddle1Y + PADDLE_HEIGHT) {
                    std::cout << "|";
                } else if (x == WIDTH - 1 && y >= paddle2Y && y < paddle2Y + PADDLE_HEIGHT) {
                    std::cout << "|";
                } else {
                    std::cout << " ";
                }
            }
            std::cout << "|\n";
        }
        
        std::cout << "+" << std::string(WIDTH, '-') << "+\n";
        std::cout << "Player 1: " << score1 << "  |  Player 2: " << score2 << "\n";
        std::cout << "Player " << playerId << " - Use W/S (Up/Down)\n";
        std::cout << "Press Q to quit\n";
    }

    void sendInput() {
        while (connected) {
            if (_kbhit()) {
                char key = _getch();
                std::string command;
                
                if (key == 'q' || key == 'Q') {
                    command = "quit";
                    send(clientSocket, command.c_str(), command.length(), 0);
                    break;
                } else if (key == 'w' || key == 'W') {
                    command = "up";
                } else if (key == 's' || key == 'S') {
                    command = "down";
                } else {
                    continue;
                }
                
                send(clientSocket, command.c_str(), command.length(), 0);
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(10));
        }
    }

    void receiveGameState() {
        char buffer[1024];
        
        while (connected) {
            int bytes = recv(clientSocket, buffer, sizeof(buffer) - 1, 0);
            if (bytes > 0) {
                buffer[bytes] = '\0';
                renderGame(std::string(buffer));
            } else {
                std::cout << "Disconnected from server\n";
                connected = false;
                break;
            }
        }
    }

    void run() {
        if (!connected) return;

        std::thread inputThread(&PongClient::sendInput, this);
        std::thread receiveThread(&PongClient::receiveGameState, this);

        inputThread.join();
        receiveThread.join();
    }

    ~PongClient() {
        if (clientSocket != INVALID_SOCKET) {
            closesocket(clientSocket);
        }
        WSACleanup();
    }
};

int main() {
    std::string serverIP;
    int port;
    
    std::cout << "Enter server IP address (default: 127.0.0.1): ";
    std::getline(std::cin, serverIP);
    if (serverIP.empty()) serverIP = "127.0.0.1";
    
    std::cout << "Enter server port (default: 8080): ";
    std::cin >> port;
    if (!port) port = 8080;
    
    PongClient client;
    if (client.connectToServer(serverIP, port)) {
        client.run();
    }
    
    return 0;
}
