/*
 * Solution to the sleeping barber problem, using C++20 atomics.
 *
 * Compile with:
 * clang++ -Wall -O2 -std=c++20 -o atomic-solution atomic-solution.cpp -pthread
 */

#include <atomic>
#include <array>
#include <chrono>
#include <iostream>
#include <random>
#include <thread>

constexpr static auto CHAIRS = 5;     // number of chairs in the waiting room
std::atomic_bool shuttingDown{false}; // true when the barbershop is closing
std::atomic_int waiting{0};           // number of waiting customers
std::atomic_bool bs{false};           // signals when the barber is ready

// random number generator
std::random_device rd;
std::mt19937 gen(rd());
std::uniform_int_distribution<> dist(1, 3);

/*
 * Cut hair for a random amount of time.
 */
void haircut() {
  std::cout << "The barber is cutting hair.\n";
  auto duration = dist(gen);
  std::this_thread::sleep_for(std::chrono::seconds(duration));
}

/*
 * Barber routine.
 */
void barber() {
  while (true) {
    waiting.wait(0); // "sleep" until a customer arrives
    if (shuttingDown.load()) {
      break;
    }
    haircut();       // cut hair
    bs.store(true);  // barber is ready
    bs.notify_one(); // let the customer go
  }
}

/*
 * Customer routine.
 */
void customer(int id, int delay) {
  std::this_thread::sleep_for(std::chrono::seconds(delay));
  while (!shuttingDown.load()) {
    auto w = waiting.load();
    if (w < CHAIRS) {
      if (waiting.compare_exchange_strong(w, w + 1)) {
        std::cout << "Customer " << id << " enters the barbershop.\n";
        waiting.notify_one(); // wake up the barber
        break;
      }
    } else {
      std::cout << "Customer " << id << " leaves the barbershop.\n";
      return;
    }
  }
  bs.wait(false); // wait until the barber finishes the haircut
  std::cout << "Customer " << id << " got a haircut.\n";
}

int main() {
  std::array<std::thread, CHAIRS * 2> customers;
  std::array<int, CHAIRS * 2> delays;
  for (auto& delay : delays) {
    delay = dist(gen);
  }

  std::cout << "The barbershop is opening.\n";
  std::thread barber_thread(barber);
  for (auto idx = 0; idx < CHAIRS * 2; ++idx) {
    customers[idx] = std::thread(customer, idx, delays[idx]);
  }
  for (auto& customer : customers) {
    customer.join();
  }

  std::cout << "The barbershop is closing.\n";

  // Best friend arrives to tell the barber it's time to go home.
  shuttingDown.store(true);
  ++waiting;
  waiting.notify_one();

  barber_thread.join();
  return 0;
}