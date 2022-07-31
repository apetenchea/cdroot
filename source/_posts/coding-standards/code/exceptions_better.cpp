#include <set>
#include <list>
#include <iostream>

class Set {
  private:
    std::set<int> set;
  public:
    void insert(int n) noexcept(false) {
      if (set.size() >= 1) {
        throw "Set insertion failed: size limit exceeded!";
      }
      set.insert(n);
    }
};

class List {
  private:
    std::list<int> list;
  public:
    int insert(int n) noexcept {
      if (list.size() >= 1) {
        return 12; // indicates size limit exceeded
      }
      list.push_back(n);
      return 0;
    }
};

int main() {
  Set a;
  List b;
  b.insert(1);
  if (b.insert(2) == 12) {
    std::cerr << "List insertion failed: size limit exceeded!";
  }
  try {
    a.insert(1);
    a.insert(2);
  } catch (char const* e) {
    std::cerr << e; 
  }
  return 0;
}