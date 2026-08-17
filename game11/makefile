# Makefile for Windows
CXX = g++
CXXFLAGS = -std=c++11 -Wall
LDFLAGS = -lws2_32

all: server client

server: server.cpp
	$(CXX) $(CXXFLAGS) -o server.exe server.cpp $(LDFLAGS)

client: client.cpp
	$(CXX) $(CXXFLAGS) -o client.exe client.cpp $(LDFLAGS)

clean:
	del *.exe *.o
