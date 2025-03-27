# Dining Philosophers – SO2 Project

## 📌 Problem Description

This project implements the classic synchronization problem known as **The Dining Philosophers** using C++ and multithreading. Each philosopher is a thread that alternates between thinking and eating. In order to eat, a philosopher must hold two forks (mutexes), one on the left and one on the right.

The goal is to:
- Avoid **deadlock**.
- Correctly synchronize access to shared resources (forks).
- Report philosopher states in the console.

---

## How to Run

### Requirements
- Linux terminal
- `g++` with C++11 support
- Make (optional, for `Makefile`)

### Build using Makefile

```bash
make
```

### Run

```bash
./philosophers <number_of_philosophers>
```

Example:
```bash
./philosophers 5
```

---

## Threads and Their Responsibilities

Each **philosopher** is implemented as a **separate thread**. The philosopher:
- Thinks (waits for a random time)
- Picks up two forks (mutexes)
- Eats (waits for a random time)
- Puts down forks

All actions are printed to the console.

---

## Critical Sections and Synchronization

- **Shared resources**: forks between philosophers
- **Mutexes (`std::mutex`)** are used to protect forks.
- Each fork is represented as a `std::mutex`, shared between two adjacent philosophers.
- **Deadlock is prevented** using an **asymmetric fork-picking strategy**:
  - Even-numbered philosophers pick up the **right** fork first.
  - Odd-numbered philosophers pick up the **left** fork first.
  - This breaks the circular wait condition, thus avoiding deadlock.

---

## Example Output

```
Philosopher 0 is thinking.
Philosopher 1 is thinking.
Philosopher 0 picked up right fork.
Philosopher 0 picked up left fork.
Philosopher 0 is eating.
...
```

---

## Notes

- The simulation runs indefinitely.
- All console outputs are synchronized to avoid interleaving using an I/O mutex.
- This project is intended as the first part of the SO2 (Operating Systems 2) course.

---

## 👨‍💻 Author

- Project for Operating Systems 2 – 2025
- Based on specifications provided by Damian Raczkowski
- Author: Wiktor Nowicki

[Go to repo's README](../README.md)
