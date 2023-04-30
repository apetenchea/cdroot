/*
 * Program used to illustrate a data-race.
 * Compile it with ThreadSanitizer enabled:
 * clang++ -Wall -O2 -std=c++20 -fsanitize=thread -o data-race data-race.cpp
 */

#include <iostream>
#include <thread>

int shared_data = 0;

void increment() {
  for (int i = 0; i < 100000; ++i) {
    ++shared_data;
  }
}

int main() {
  std::thread t1(increment);
  std::thread t2(increment);

  t1.join();
  t2.join();

  std::cout << "Shared data: " << shared_data << '\n';
  return 0;
}