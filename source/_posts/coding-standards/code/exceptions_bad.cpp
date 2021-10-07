#include <set>
#include <list>

class Set {
  private:
    std::set<int> set;
  public:
    void insert(int n) {
      if (set.size() >= 1) {
        throw "insertion failed: size limit exceeded";
      }
      set.insert(n);
    }
};

class List {
  private:
    std::list<int> list;
  public:
    int insert(int n) {
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
  b.insert(1); // inserts 1 into the list
  b.insert(2); // returns error code
  a.insert(1); // inserts 1 into the set
  a.insert(2); // throws an exception and crashes
  return 0;
}
