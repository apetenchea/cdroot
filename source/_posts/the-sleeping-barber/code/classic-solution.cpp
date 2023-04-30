/*
 * Classic solution to the sleeping barber problem, using C++20.
 *
 * Compile with:
 * clang++ -Wall -O2 -std=c++20 -o classic-solution classic-solution.cpp -pthread
 */

#include <atomic>
#include <array>
#include <chrono>
#include <iostream>
#include <random>
#include <mutex>
#include <thread>
#include <semaphore>

constexpr static auto CHAIRS = 5;      // number of chairs in the waiting room
std::atomic_bool shuttingDown{false};  // true when the barbershop is closing
auto waiting = 0;                      // number of waiting customers
std::mutex mx;                         // protection for the waiting room
std::counting_semaphore<CHAIRS> cs{0}; // signals when a customer arrives
std::binary_semaphore bs{0};           // signals when the barber is ready

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
  std::unique_lock lock(mx, std::defer_lock);
  while (!shuttingDown.load()) {
    // "sleep" until a customer arrives, or until the barbershop is closing
    bool arrived = cs.try_acquire_for(std::chrono::seconds(5));
    if (!arrived) {
      continue;
    }
    lock.lock();   // protect the waiting room
    --waiting;     // invite a customer
    lock.unlock(); // let others use the waiting room
    haircut();     // cut hair
    bs.release();  // let the customer go
  }
}

/*
 * Customer routine.
 */
void customer(int id, int delay) {
  std::this_thread::sleep_for(std::chrono::seconds(delay));
  std::unique_lock lock(mx);
  if (waiting < CHAIRS) {
    std::cout << "Customer " << id << " enters the barbershop.\n";
    ++waiting;     // enter the waiting room
    lock.unlock(); // let others use the waiting room
  } else {
    std::cout << "Customer " << id << " leaves the barbershop.\n";
    return;        // leave the barbershop
  }
  cs.release();    // wake up the barber
  bs.acquire();    // wait until the barber finishes the haircut
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
  shuttingDown.store(true);
  barber_thread.join();
  return 0;
}