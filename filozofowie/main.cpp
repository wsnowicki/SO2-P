#include <iostream>
#include <thread>
#include <mutex>
#include <vector>
#include <chrono>
#include <random>

using namespace std;

class Philosopher {
public:
    Philosopher(int id, mutex* left, mutex* right, bool even_strategy)
        : id(id), left_fork(left), right_fork(right), even_strategy(even_strategy) {}

    void dine() {
        while (true) {
            think();
            if (even_strategy && id % 2 == 0) {
                pick_up_right();
                pick_up_left();
            } else {
                pick_up_left();
                pick_up_right();
            }
            eat();
            put_down();
        }
    }

private:
    int id;
    mutex* left_fork;
    mutex* right_fork;
    bool even_strategy;

    void think() {
        print_state("is thinking");
        this_thread::sleep_for(random_time());
    }

    void eat() {
        print_state("is eating");
        this_thread::sleep_for(random_time());
    }

    void pick_up_left() {
        left_fork->lock();
        print_state("picked up left fork");
    }

    void pick_up_right() {
        right_fork->lock();
        print_state("picked up right fork");
    }

    void put_down() {
        left_fork->unlock();
        right_fork->unlock();
        print_state("put down forks");
    }

    void print_state(const string& state) {
        lock_guard<mutex> guard(io_mutex);
        cout << "Philosopher " << id << " " << state << "." << endl;
    }

    chrono::milliseconds random_time() {
        static thread_local mt19937 rng(random_device{}());
        uniform_int_distribution<int> dist(500, 1500);
        return chrono::milliseconds(dist(rng));
    }

    static mutex io_mutex;
};

mutex Philosopher::io_mutex;

int main(int argc, char* argv[]) {
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <number_of_philosophers>" << endl;
        return 1;
    }

    int N = stoi(argv[1]);
    if (N < 2) {
        cerr << "There must be at least 2 philosophers." << endl;
        return 1;
    }

    vector<mutex> forks(N);
    vector<thread> philosophers;

    for (int i = 0; i < N; ++i) {
        mutex* left = &forks[i];
        mutex* right = &forks[(i + 1) % N];
        bool even_strategy = true; // Prevent deadlock by changing fork pickup order for some philosophers

        philosophers.emplace_back(&Philosopher::dine, Philosopher(i, left, right, even_strategy));
    }

    for (auto& p : philosophers) {
        p.join();
    }

    return 0;
}

