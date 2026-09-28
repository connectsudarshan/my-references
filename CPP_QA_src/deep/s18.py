DEEP = {

441: D("Reversing a string in place means swapping characters from both ends toward the middle: `s[i]` with `s[n-1-i]` for `i < n/2`, O(n) time and O(1) extra space.",
"""Two-pointer technique: `for (size_t i = 0, j = s.size(); i + 1 < j; ++i) std::swap(s[i], s[--j]);` or with `left`/`right` indices. Only n/2 swaps are needed.

Interview extensions: reverse words in a sentence (reverse the whole string, then each word), reverse without modifying the input (construct from reverse iterators `std::string(s.rbegin(), s.rend())`), and Unicode: byte-wise reversal corrupts multi-byte UTF-8 characters.""",
"Using signed/unsigned index arithmetic like `size() - 1` on an empty string, which wraps to a huge value and reads out of bounds.",
["How do you reverse the order of words? => Reverse the whole string, then reverse each word in place.",
 "Does byte reversal work for UTF-8? => No; multi-byte characters get scrambled. Reverse by code points or grapheme clusters."]),

442: D("A palindrome reads the same forwards and backwards; check with two indices moving inward and comparing characters, returning false at the first mismatch, O(n) time and O(1) space.",
"""Variants: ignore case and non-alphanumeric characters (skip with `std::isalnum`, compare `std::tolower`, casting to `unsigned char` first), palindromic numbers (reverse half the digits), and \"valid palindrome after deleting at most one character\" (on mismatch, try skipping either side once).

A one-liner `std::equal(s.begin(), s.begin() + s.size()/2, s.rbegin())` is idiomatic.""",
"Calling `std::tolower(c)` with a negative `char` value (non-ASCII bytes), which is undefined behaviour; cast to `unsigned char` first.",
["How do you check a palindrome ignoring punctuation? => Skip non-alphanumeric characters with the two pointers and compare case-insensitively.",
 "How do you check if a number is a palindrome without converting to string? => Reverse its second half numerically and compare with the first half."]),

443: D("Factorial `n! = n × (n-1)!` with `0! = 1` is the classic recursion example: a base case that stops recursion and a recursive case that reduces the problem size.",
"""Recursive version uses O(n) stack depth; iterative is O(1) space and preferred in practice. Overflow is the real concern: `20!` is the largest that fits in 64-bit unsigned; `13!` overflows 32-bit int. Use `unsigned long long`, check for overflow, or a big-integer type.

`constexpr` makes it computable at compile time: `constexpr unsigned long long fact(unsigned n) { return n <= 1 ? 1 : n * fact(n - 1); }`.""",
"Using `int` and returning garbage (signed overflow is undefined behaviour) for n above 12.",
["What's the largest factorial fitting in 64 bits? => 20! (about 2.4 × 10^18).",
 "Why prefer iteration here? => No stack growth and no call overhead, with identical results."]),

444: D("The Fibonacci sequence starts 0, 1 and each term is the sum of the previous two; generate N terms iteratively in O(N) time by keeping only the last two values.",
"""Naive recursion `fib(n-1) + fib(n-2)` is exponential (O(φⁿ)) because it recomputes subproblems; memoization or bottom-up iteration makes it linear. Matrix exponentiation or fast doubling gives O(log n) for the nth term.

Overflow: `fib(93)` is the largest fitting in unsigned 64-bit. The question is often a lead-in to dynamic programming discussions.""",
"Presenting the naive recursive version as the solution without noting its exponential time.",
["How do you compute the nth Fibonacci number in O(log n)? => Matrix exponentiation or the fast-doubling identities.",
 "Why is naive recursion exponential? => It recomputes the same subproblems repeatedly; the call tree grows like φⁿ."]),

445: D("Swapping two numbers without a temporary uses arithmetic (`a = a + b; b = a - b; a = a - b;`) or XOR (`a ^= b; b ^= a; a ^= b;`), but in real code `std::swap` is clearer and at least as fast.",
"""Both tricks break when `a` and `b` refer to the same variable: XOR zeroes it, arithmetic also yields 0. The arithmetic version can overflow signed integers (undefined behaviour).

Compilers turn a temporary-based swap into register moves anyway, so the tricks have no performance benefit on modern hardware. It's a trivia question; say so after answering.""",
"Using XOR swap through references or pointers that may alias, zeroing the value when both refer to the same object.",
["When does XOR swap fail? => When both operands are the same object; the result becomes zero.",
 "Is XOR swap faster than `std::swap`? => No; compilers optimize a temporary swap into register operations."]),

446: D("Finding the largest element is a single linear scan tracking the maximum so far, initialized from the first element, O(n) time and O(1) space; `std::max_element` does it in the standard library.",
"""`std::max_element(v.begin(), v.end())` returns an iterator (end for an empty range, so check before dereferencing). `std::ranges::max(v)` returns the value but requires a non-empty range.

Initialize with the first element or `std::numeric_limits<T>::lowest()`, not `0` (fails for all-negative arrays) and not `INT_MIN` for floating types (`min()` is the smallest positive float).""",
"Initializing the maximum to 0, which gives a wrong answer for arrays of negative numbers.",
["What's the difference between `numeric_limits<double>::min()` and `lowest()`? => `min()` is the smallest positive normal value; `lowest()` is the most negative.",
 "How do you find both min and max efficiently? => `std::minmax_element`, using about 1.5n comparisons."]),

447: D("Counting vowels scans the string once and counts characters that belong to the vowel set, typically after lowercasing, O(n) time.",
"""Idiomatic: `std::count_if(s.begin(), s.end(), [](unsigned char c){ return std::strchr(\"aeiou\", std::tolower(c)) && c; })` or a `switch`, or a lookup table/`std::string_view(\"aeiouAEIOU\").find(c) != npos`.

Discussion points: what counts as a vowel (`y`?), non-ASCII letters, and why a 256-entry lookup table is fastest for huge inputs.""",
"Using `std::strchr(\"aeiou\", c)` without guarding `c == '\\0'`, since `strchr` finds the terminating null and counts it as a vowel.",
["Why cast to `unsigned char` before `tolower`? => Passing negative values other than EOF is undefined behaviour.",
 "How would you count each vowel separately? => An array or map of counts indexed by the vowel."]),

448: D("A number n is prime if it's greater than 1 and has no divisors other than 1 and itself; trial division only needs to test divisors up to √n, skipping even numbers after 2.",
"""Loop `for (i = 3; i * i <= n; i += 2)`, with special cases for n < 2, 2 and even numbers; the 6k±1 optimization checks only numbers of that form. Use `i <= n / i` to avoid `i * i` overflow.

For many queries up to a limit, use the Sieve of Eratosthenes (O(n log log n)); for huge single numbers, Miller-Rabin (deterministic for 64-bit with fixed bases).""",
"Looping up to `n` or `n/2` (much slower) or forgetting that 1 and negative numbers aren't prime.",
["Why is checking up to √n enough? => Any factor larger than √n pairs with one smaller than √n.",
 "How do you find all primes up to N? => The Sieve of Eratosthenes."]),

449: D("Finding the second largest in one pass tracks two values, `first` and `second`: a new element larger than `first` pushes `first` down to `second`; otherwise if it's larger than `second` (and distinct from `first`, if distinctness is required) it becomes `second`.",
"""Clarify requirements: distinct second largest (for `[5,5,3]` answer 3) or second in sorted order (answer 5)? What if no second value exists (return `std::optional`)?

Initialize with `std::numeric_limits<T>::lowest()` or `std::optional`, not sentinel values that may appear in data. Generalization: kth largest uses a min-heap of size k or `std::nth_element`.""",
"Returning a sentinel like `INT_MIN` when there's no second largest, which is indistinguishable from real data containing `INT_MIN`.",
["How do you handle duplicates? => Clarify the requirement; for distinct values skip elements equal to `first`.",
 "How do you generalize to the kth largest? => A min-heap of size k (O(n log k)) or `std::nth_element` (average O(n))."]),

450: D("Removing duplicates from a sorted array in place uses a slow write index and a fast read index: copy each element that differs from the last kept one to the write position, returning the write index as the new length, O(n) time and O(1) space.",
"""In C++ this is exactly `std::unique` followed by `erase`: `v.erase(std::unique(v.begin(), v.end()), v.end());`. `std::unique` only removes consecutive duplicates, so unsorted input must be sorted first (or use a hash set if order must be preserved).

Variation: allow at most two copies of each element (compare with the element two positions back in the output).""",
"Calling `std::unique` without `erase`, leaving the vector's size unchanged with leftover elements at the end.",
["Why doesn't `std::unique` shrink the container? => Algorithms work on iterators and can't change container size; you must call `erase`.",
 "How do you remove duplicates from an unsorted array keeping order? => Track seen values in a hash set."]),

451: D("Two strings are anagrams if they contain the same characters with the same counts; compare frequency counts (O(n) with a 26- or 256-element array) or sort both and compare (O(n log n)).",
"""Counting: increment for characters of the first string, decrement for the second, and check all counts are zero; return early if lengths differ. For Unicode or arbitrary alphabets use `std::unordered_map<char32_t,int>`.

`std::is_permutation(a.begin(), a.end(), b.begin(), b.end())` exists but is O(n²) worst case. Related: grouping anagrams by a sorted key or count signature.""",
"Forgetting to check lengths first, or indexing a 26-element array with non-lowercase characters, causing out-of-bounds access.",
["What's the complexity of the counting approach? => O(n) time and O(alphabet) space.",
 "How do you group a list of words into anagram groups? => Use a hash map keyed by each word's sorted letters or letter counts."]),

452: D("Finding the first non-repeating character takes two passes: count occurrences of each character, then scan the string again and return the first character with count 1, O(n) time.",
"""A 256-entry array suffices for bytes; use a hash map for wider character sets. For a stream (characters arriving one by one), keep counts plus a queue of candidates, popping from the front while the front's count exceeds 1.

Return type: an index, `std::optional<char>`, or a sentinel; clarify case sensitivity.""",
"Returning the first character in iteration order of an `unordered_map`, which isn't string order.",
["How do you solve it for a stream of characters? => Maintain counts and a queue of candidates; pop repeated ones from the front.",
 "Why is the second pass over the string, not the map? => The map doesn't preserve the characters' original order."]),

453: D("Binary search finds a target in a sorted array by repeatedly comparing with the middle element and halving the search range, O(log n) time.",
"""Use `mid = lo + (hi - lo) / 2` to avoid overflow, and be consistent about range conventions (half-open `[lo, hi)` is least error-prone). The standard library provides `std::binary_search` (bool), `std::lower_bound` (first element ≥ target), `std::upper_bound` (first > target), and `std::equal_range`.

Binary search generalizes to \"search on the answer\": finding the smallest value satisfying a monotonic predicate (`std::partition_point`).""",
"Writing `(lo + hi) / 2`, which overflows for large indices, or mixing inclusive and exclusive bounds and looping forever.",
["What does `std::lower_bound` return? => An iterator to the first element not less than the value (insertion point).",
 "What is binary search on the answer? => Searching a monotonic predicate over a value range, e.g. the minimum capacity that works."]),

454: D("Rotating an array right by k in place with O(n) time and O(1) space uses three reversals: reverse the whole array, then reverse the first `k` elements and the remaining `n-k` elements (after taking `k %= n`).",
"""Example `[1,2,3,4,5,6,7]`, k=3: reverse all → `[7,6,5,4,3,2,1]`, reverse first 3 → `[5,6,7,4,3,2,1]`, reverse rest → `[5,6,7,1,2,3,4]`.

The standard library does it directly: `std::rotate(v.begin(), v.end() - k, v.end())` (rotates left so that the given middle becomes first). Alternative: cyclic replacements with gcd(n, k) cycles.""",
"Forgetting `k %= n` (k larger than the size) or dividing by zero for an empty array.",
["How do you rotate right with `std::rotate`? => `std::rotate(v.begin(), v.end() - k, v.end())` after `k %= n`.",
 "Why does the triple-reversal work? => Reversing all puts the last k elements first in reverse order; reversing each part restores their internal order."]),

455: D("For an array containing 1..N with one number missing, the missing number equals the expected sum `N(N+1)/2` minus the actual sum, or the XOR of all 1..N and all array elements.",
"""The sum approach can overflow for large N in 32-bit types; use 64-bit arithmetic or XOR, which never overflows. Both are O(n) time and O(1) space.

Variants: two missing numbers (use sum and sum of squares, or XOR partitioning by a set bit), duplicates plus missing, and \"first missing positive\" in an unsorted array (index marking in place).""",
"Computing `n * (n + 1) / 2` in `int` for n around 100,000 or more, overflowing.",
["Why use XOR instead of the sum? => XOR can't overflow.",
 "How do you find two missing numbers? => XOR everything to get a ^ b, split numbers by one set bit, and XOR each group."]),

456: D("Merging two sorted arrays uses two indices, repeatedly taking the smaller front element into the output, then appending the remainder of whichever array isn't exhausted, O(n + m) time.",
"""The standard library provides `std::merge(a.begin(), a.end(), b.begin(), b.end(), std::back_inserter(out))` and `std::inplace_merge` for two adjacent sorted ranges.

In-place variant (LeetCode's \"merge into the first array with extra space at the end\"): fill from the back so you never overwrite unprocessed elements. Using `<=` keeps the merge stable.""",
"Merging into the first array from the front, overwriting elements that haven't been processed yet.",
["How do you merge in place when the first array has spare capacity? => Fill from the end using the largest elements first.",
 "How do you merge k sorted arrays? => A min-heap of the current front elements, O(N log k)."]),

457: D("Balanced parentheses checking pushes opening brackets onto a stack and, for each closing bracket, checks that the stack isn't empty and the top is the matching opener; the expression is balanced if the stack is empty at the end.",
"""Handles `()`, `[]`, `{}` with a small map from closing to opening bracket. O(n) time, O(n) space worst case. With a single bracket type, a counter suffices (never negative, zero at the end).

Edge cases: closing bracket with an empty stack, leftover openers, and ignoring other characters. Extensions: minimum insertions to balance, longest valid parentheses substring.""",
"Only counting opening and closing brackets, which accepts `([)]` or `)(` as balanced.",
["Why is a counter insufficient for multiple bracket types? => It can't check that the types nest correctly, like `([)]`.",
 "What's the space complexity? => O(n) in the worst case, when all characters are openers."]),

458: D("Floyd's cycle detection moves a slow pointer one step and a fast pointer two steps; if the list has a cycle they eventually meet, and if the fast pointer reaches null there's no cycle, O(n) time and O(1) space.",
"""Inside the cycle, the fast pointer gains one node per step, so it catches up within the cycle's length. Check `fast && fast->next` before advancing to avoid null dereference.

Alternative: store visited node addresses in a hash set (O(n) space). The same technique detects cycles in any iterated function, e.g. repeated states in sequences.""",
"Advancing `fast = fast->next->next` without checking `fast->next`, dereferencing null in lists of odd length.",
["Why must the pointers meet if there's a cycle? => The distance between them decreases by one each step once both are in the cycle.",
 "How do you find the cycle's length? => After meeting, move one pointer around until it returns, counting steps."]),

459: D("Reversing a singly linked list iteratively walks the list with three pointers (`prev`, `curr`, `next`), redirecting each node's `next` to the previous node; `prev` becomes the new head, O(n) time and O(1) space.",
"""Loop: `next = curr->next; curr->next = prev; prev = curr; curr = next;`. The recursive version is elegant but uses O(n) stack, which can overflow for long lists.

Variations: reverse a sublist between positions m and n, reverse in groups of k, and checking whether a list is a palindrome (reverse the second half).""",
"Losing the rest of the list by overwriting `curr->next` before saving it in `next`.",
["Why prefer the iterative version? => O(1) extra space and no risk of stack overflow on long lists.",
 "How do you check if a linked list is a palindrome in O(1) space? => Find the middle, reverse the second half, compare, and optionally restore."]),

460: D("To find the kth largest element, keep a min-heap of size k: push each element and pop the smallest whenever the heap exceeds k; the heap's top is the kth largest, O(n log k) time and O(k) space.",
"""`std::priority_queue<int, std::vector<int>, std::greater<int>>` is a min-heap. Good for streams and when k is small relative to n.

Alternatives: `std::nth_element` (quickselect, average O(n), modifies the array), sorting (O(n log n)), and `std::partial_sort`. For a stream of queries, the heap maintains the answer incrementally.""",
"Using the default `std::priority_queue` (a max-heap) and popping k times after inserting all n elements, which is O(n + k log n) but uses O(n) memory.",
["What does `std::nth_element` guarantee? => The nth element is in its sorted position, with smaller-or-equal elements before and greater-or-equal after.",
 "Why a min-heap for the kth largest? => Its top is the smallest of the k largest seen so far, which is exactly the kth largest."]),

461: D("The Longest Common Subsequence of two strings is the longest sequence of characters appearing in both in the same order (not necessarily contiguous); dynamic programming computes it with `dp[i][j]` = LCS length of the first i and j characters, O(n·m) time.",
"""Recurrence: if `a[i-1] == b[j-1]`, `dp[i][j] = dp[i-1][j-1] + 1`; else `max(dp[i-1][j], dp[i][j-1])`. Reconstruct the subsequence by walking back from `dp[n][m]`.

Space can be reduced to two rows (O(min(n, m))) if only the length is needed. LCS underlies diff tools and edit-distance-like problems; distinguish it from the longest common substring (contiguous).""",
"Confusing subsequence with substring; the substring version resets to 0 on mismatch instead of taking the max.",
["How do you reduce memory? => Keep only the previous and current rows of the DP table.",
 "Where is LCS used in practice? => Diff tools, version control and bioinformatics sequence alignment."]),

462: D("Kadane's algorithm finds the maximum subarray sum in O(n): track the best sum ending at the current index (`cur = max(x, cur + x)`) and the best overall.",
"""Intuition: if the running sum becomes worse than starting fresh at the current element, drop the prefix. Initialize with the first element (not 0) to handle all-negative arrays correctly. Track start and end indices to return the subarray itself.

Extensions: maximum circular subarray (total minus minimum subarray), maximum product subarray (track min and max), and 2D maximum submatrix.""",
"Initializing `best = 0`, which returns 0 for all-negative arrays instead of the largest (least negative) element.",
["How do you handle circular arrays? => Answer is max(normal Kadane, total sum minus minimum subarray), unless all elements are negative.",
 "How do you return the subarray bounds? => Record the start when you restart, and the end when best improves."]),

463: D("To find a cycle's starting node, first detect a meeting point with Floyd's algorithm, then move one pointer to the head and advance both one step at a time; they meet at the cycle start. To remove the cycle, set the `next` of the cycle's last node to null.",
"""Why it works: if the head-to-start distance is `a`, and the meeting point is `b` into the cycle of length `c`, then `a ≡ c - b (mod c)`, so a pointer from the head and one from the meeting point reach the start together.

To remove: from the start node, walk until the node whose `next` is the start, and set that `next` to `nullptr`.""",
"Removing the cycle by breaking the link at the meeting point, which cuts off part of the cycle rather than only the back edge.",
["Why does resetting one pointer to the head find the start? => The distance from head to start equals the distance from the meeting point to start modulo the cycle length.",
 "How do you find the node before the cycle start? => Walk from the start around the cycle until `node->next == start`."]),

464: D("Quicksort picks a pivot, partitions the array so smaller elements come before it and larger after, then recursively sorts both parts; average O(n log n), worst case O(n²), in place.",
"""Partition schemes: Lomuto (simpler, more swaps) and Hoare (fewer swaps). Worst case occurs with bad pivots (e.g. first element on sorted input); mitigations are random or median-of-three pivots and three-way partitioning for many duplicates.

Recursing on the smaller part first and looping on the larger bounds stack depth to O(log n). `std::sort` uses introsort: quicksort switching to heapsort at excessive depth (guaranteed O(n log n)) and insertion sort for small ranges.""",
"Using the first element as pivot on already sorted data, giving O(n²) time and O(n) recursion depth.",
["How does `std::sort` avoid quicksort's worst case? => Introsort switches to heapsort when recursion depth exceeds about 2 log n.",
 "Is quicksort stable? => No; use `std::stable_sort` (merge sort based) for stability."]),

465: D("Two-sum in O(n) uses a hash map from value to index: for each element x, check whether `target - x` has been seen; if yes, report the pair, otherwise record x.",
"""For all pairs (not just one), count occurrences in a map and handle duplicates carefully (x == target - x needs count ≥ 2) and avoid double counting. If the array is sorted, two pointers from both ends achieve O(n) with O(1) space.

Extensions: 3-sum (sort + two pointers, O(n²)), 4-sum, and pair counting in streams.""",
"Adding the current element to the map before checking, which pairs an element with itself when `x == target - x`.",
["What's the approach for sorted arrays? => Two pointers from both ends, moving based on whether the sum is too small or too large.",
 "How do you solve 3-sum? => Sort, then for each element run two-sum with two pointers on the rest, O(n²)."]),

466: D("An LRU cache stores key-value pairs up to a capacity and evicts the least recently used entry; `std::list` keeps usage order (most recent at front) and `std::unordered_map<Key, list::iterator>` gives O(1) lookup, so both get and put are O(1).",
"""Get: look up the iterator, move the node to the front with `list.splice(list.begin(), list, it)` (no reallocation, iterators stay valid), and return the value. Put: update and move if present; otherwise insert at front and, if over capacity, erase the back node and its map entry.

Thread safety requires a mutex (or sharding). Production caches often use approximate LRU (clock algorithm) or segmented LRU for scan resistance.""",
"Erasing and re-inserting list nodes instead of `splice`, invalidating the iterators stored in the map.",
["Why does `splice` matter here? => It moves the node without invalidating iterators, so map entries stay valid.",
 "How do you make it thread-safe efficiently? => Shard the cache by key hash, each shard with its own lock."]),

467: D("The height (maximum depth) of a binary tree is the number of nodes (or edges, by convention) on the longest root-to-leaf path; recursively, `height(node) = 1 + max(height(left), height(right))` with `height(nullptr) = 0`.",
"""O(n) time, O(h) stack space (h up to n for a degenerate tree, which can overflow the stack for very deep trees). Iterative alternative: BFS counting levels, or DFS with an explicit stack of (node, depth).

Clarify the convention: some define height in edges (leaf height 0, empty tree -1).""",
"Recursion on a very deep, skewed tree (millions of nodes) overflowing the call stack; use an iterative approach.",
["How do you compute it iteratively? => Level-order traversal, counting the number of levels.",
 "What's the minimum depth variant's catch? => A node with one child isn't a leaf; you must follow the existing child."]),

468: D("A binary tree is height-balanced if, for every node, the heights of its left and right subtrees differ by at most one; check it in O(n) with a post-order function that returns the height or a failure flag (e.g. -1).",
"""The naive approach calls `height()` at each node, giving O(n²) for skewed trees. The single-pass version: compute left height; if -1 return -1; compute right; if -1 or `abs(l - r) > 1` return -1; else return `1 + max(l, r)`.

Self-balancing trees (AVL, red-black) maintain weaker or stronger balance invariants to guarantee O(log n) operations.""",
"Checking balance only at the root, missing unbalanced subtrees deeper in the tree.",
["Why is the naive approach O(n²)? => It recomputes subtree heights at every node.",
 "How do AVL and red-black trees differ in balance? => AVL keeps heights within 1 (stricter); red-black guarantees the longest path is at most twice the shortest."]),

469: D("Level-order traversal visits a binary tree level by level using a queue: push the root, then repeatedly pop a node, visit it and push its children.",
"""To group nodes by level, process the queue in batches: record `size = q.size()` at the start of each level and pop exactly that many. O(n) time and O(w) space (w = maximum width).

Variants: zigzag order, right side view (last node of each level), level averages, and minimum depth (first leaf found). BFS is the same idea on general graphs, with a visited set.""",
"Using a stack instead of a queue, which produces a depth-first order.",
["How do you print each level on its own line? => Record the queue size at the start of each level and process exactly that many nodes.",
 "What's BFS's space complexity on a tree? => O(w), the maximum width, up to about n/2 for a complete tree."]),

470: D("In a binary search tree, the lowest common ancestor of nodes p and q is the first node, walking down from the root, whose value lies between p and q (inclusive): if both are smaller go left, if both are larger go right, otherwise the current node is the LCA.",
"""O(h) time and O(1) space iteratively, using the BST ordering. For a general binary tree (no ordering), recursive search: return the node if it's p or q; if both subtrees return non-null, the current node is the LCA; O(n).

Many queries on a static tree use binary lifting or Euler tour + RMQ for O(log n) or O(1) per query.""",
"Using the general binary tree algorithm on a BST, missing the O(h) solution, or assuming both nodes exist without clarifying.",
["How does the approach change for a general binary tree? => Recursive search where the node with p and q in different subtrees is the LCA.",
 "How do you answer many LCA queries quickly? => Binary lifting (O(log n) per query) or Euler tour with a sparse table."]),
}
