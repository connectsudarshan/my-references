"""Corrections for 500_CPP_Interview_Questions_Reference.html found by check.py (g++ -std=c++20).

    python fixes.py     # apply to the page (idempotent), then run: python check.py

Each fix replaces the code (and, where the text was wrong, the answer) of one question.
New code avoids backticks and backslashes because the page stores it in JS template literals.
"""
import pathlib, re, sys

PAGE = pathlib.Path(__file__).resolve().parent.parent / "500_CPP_Interview_Questions_Reference.html"

CODE = {
5: """namespace math { int square(int x) { return x*x; } }
int sq = math::square(4);   // qualify a namespace member with ::

int x = 10;                 // global x
void f() { int x = 20; std::cout << ::x; }   // ::x reaches the global (prints 10), not the local""",

7: """static int counter = 0;        // static storage duration; internal linkage at namespace scope
extern int sharedFlag;         // declaration only: defined in another translation unit
thread_local int perThread;    // C++11: one instance per thread

struct Stats {
    mutable int cacheHits = 0; // mutable: class members only; writable even in const objects
    int get() const { ++cacheHits; return 42; }
};
// register int fast_i;        // removed in C++17 (was only an optimization hint)
// auto int y = 1;             // pre-C++11 meaning of auto; now auto means type deduction""",

49: """class Vehicle {};
class Engine {};
class Car : public Vehicle {   // is-a: a Car IS a Vehicle (inheritance)
    Engine e;                  // has-a: a Car HAS an Engine (composition)
};""",

71: """class Buffer {
    int* data_;
public:
    Buffer() : data_(new int(0)) {}                                  // declaring a copy ctor removes the implicit default ctor
    Buffer(const Buffer& other) : data_(new int(*other.data_)) {}    // copy ctor: deep copy
    ~Buffer() { delete data_; }
};
void f(Buffer b) {}

int main() {
    Buffer a;
    Buffer b = a;      // invoked here (copy-initialization)
    f(a);              // and here (pass-by-value)
}""",

121: """class Vec2 {
    double x_, y_;
public:
    Vec2(double x, double y) : x_(x), y_(y) {}
    Vec2 operator+(const Vec2& o) const { return {x_ + o.x_, y_ + o.y_}; }   // uses the constructor
};
Vec2 a{1, 2}, b{3, 4};
Vec2 c = a + b;   // calls a.operator+(b)""",

125: """class Point {
    int x_, y_;
public:
    Point(int x, int y) : x_(x), y_(y) {}
    friend std::ostream& operator<<(std::ostream& os, const Point& p) {
        return os << "(" << p.x_ << "," << p.y_ << ")";
    }
};
int main() { std::cout << Point{1, 2}; }   // prints (1,2)""",

196: """template<typename T>
struct PoolAllocator {
    using value_type = T;                                    // required by the Allocator requirements
    PoolAllocator() = default;
    template<typename U> PoolAllocator(const PoolAllocator<U>&) noexcept {}   // rebind support
    T* allocate(std::size_t n) {                             // real pools hand out pre-reserved blocks
        return static_cast<T*>(::operator new(n * sizeof(T)));
    }
    void deallocate(T* p, std::size_t) noexcept { ::operator delete(p); }
};
template<class T, class U> bool operator==(const PoolAllocator<T>&, const PoolAllocator<U>&) { return true; }

std::vector<int, PoolAllocator<int>> v{1, 2, 3};   // container uses the custom allocator""",

292: """class Buffer {
public:
    Buffer(Buffer&&) noexcept;              // noexcept -> vector will MOVE on reallocation
    Buffer& operator=(Buffer&&) noexcept;   // without noexcept, vector falls back to COPY
};                                          // (std::move_if_noexcept decides which one)""",
}

ANSWER = {
7: "Modern C++ has `static`, `extern`, `thread_local` (C++11) and `mutable` (class members only). They control **storage duration** (automatic, static, thread) and **linkage** (internal, external). History: `auto` was a storage class before C++11 and now means type deduction; `register` was deprecated in C++11 and removed in C++17.",
}


def replace_field(block, field, new):
    m = re.search(field + r":`((?:[^`\\]|\\.)*)`", block)
    if not m:
        sys.exit(f"field {field} not found")
    return block[:m.start(1)] + new + block[m.end(1):]


def main():
    html = PAGE.read_text(encoding="utf-8")
    for num in sorted(set(CODE) | set(ANSWER)):
        start = html.index(f"\nnum:{num}, section:")
        end = html.index("\n{\nnum:", start + 1) if f"\nnum:{num + 1}, section:" in html else html.index("];", start)
        block = html[start:end]
        new = block
        if num in CODE:
            assert "`" not in CODE[num] and "\\" not in CODE[num] and "${" not in CODE[num]
            new = replace_field(new, "code", CODE[num])
        if num in ANSWER:
            new = replace_field(new, "answer", ANSWER[num].replace("`", "\\`"))
        html = html[:start] + new + html[end:]
        print(f"Q{num}: {'code' if num in CODE else ''} {'answer' if num in ANSWER else ''}".strip())
    PAGE.write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
