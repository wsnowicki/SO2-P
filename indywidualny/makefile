CXX = g++
CXXFLAGS = -std=c++11 -pthread -Wall -Wextra
TARGET = filozofowie
SRC = main.cpp

all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

clean:
	rm -f $(TARGET)

