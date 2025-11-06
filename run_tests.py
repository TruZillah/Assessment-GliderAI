import sys

# Simple test harness that marks unimplemented functions as TODO

PASSED = 0
FAILED = 0
TODO = 0

def check(name, func, args, expected):
    global PASSED, FAILED, TODO
    try:
        result = func(*args)
        if result == expected:
            PASSED += 1
            print(f"PASS  - {name}: {args} -> {result}")
        else:
            FAILED += 1
            print(f"FAIL  - {name}: {args} -> {result} (expected {expected})")
    except NotImplementedError as nie:
        TODO += 1
        print(f"TODO  - {name}: not implemented ({nie})")
    except Exception as ex:
        FAILED += 1
        print(f"ERROR - {name}: raised {type(ex).__name__}: {ex}")

def test_summation():
    from problems.summation import summation
    check("summation", summation, (2, 3), 5)
    check("summation", summation, (-1, 1), 0)
    check("summation", summation, (0, 0), 0)

def test_palindrome():
    from problems.palindrome import is_palindrome
    check("is_palindrome", is_palindrome, ("A man, a plan, a canal: Panama",), True)
    check("is_palindrome", is_palindrome, ("race a car",), False)
    check("is_palindrome", is_palindrome, ("",), True)

def test_second_largest():
    from problems.second_largest import second_largest
    check("second_largest", second_largest, ([2, 3, 1],), 2)
    check("second_largest", second_largest, ([5, 5, 5],), None)
    check("second_largest", second_largest, ([-1, -2, -3],), -2)

def test_frequency_sort():
    from problems.frequency_sort import frequency_sort
    check("frequency_sort", frequency_sort, ("tree",), "eert")
    check("frequency_sort", frequency_sort, ("cccaaa",), "aaaccc")
    check("frequency_sort", frequency_sort, ("",), "")

def test_merge_intervals():
    from problems.merge_intervals import merge_intervals
    check("merge_intervals", merge_intervals, ([[1,3],[2,6],[8,10],[15,18]],), [[1,6],[8,10],[15,18]])
    check("merge_intervals", merge_intervals, ([[1,4],[4,5]],), [[1,5]])
    check("merge_intervals", merge_intervals, ([],), [])

def test_two_sum():
    from problems.two_sum import two_sum
    check("two_sum", two_sum, ([2,7,11,15], 9), [0,1])
    check("two_sum", two_sum, ([3,2,4], 6), [1,2])
    check("two_sum", two_sum, ([3,3], 6), [0,1])
    check("two_sum", two_sum, ([1,2,3], 10), [-1,-1])

def test_balanced_brackets():
    from problems.balanced_brackets import balanced_brackets
    check("balanced_brackets", balanced_brackets, ("()[]{}",), True)
    check("balanced_brackets", balanced_brackets, ("(]",), False)
    check("balanced_brackets", balanced_brackets, ("([{}])",), True)

def test_max_subarray():
    from problems.max_subarray import max_subarray
    check("max_subarray", max_subarray, ([-2,1,-3,4,-1,2,1,-5,4],), 6)
    check("max_subarray", max_subarray, ([1],), 1)
    check("max_subarray", max_subarray, ([-1,-2,-3],), -1)

def test_product_except_self():
    from problems.product_except_self import product_except_self
    check("product_except_self", product_except_self, ([1,2,3,4],), [24,12,8,6])
    check("product_except_self", product_except_self, ([0,1,2,3],), [6,0,0,0])

def test_three_sum():
    from problems.three_sum import three_sum
    check("three_sum", three_sum, ([-1,0,1,2,-1,-4],), [[-1,-1,2],[-1,0,1]])
    check("three_sum", three_sum, ([0,1,1],), [])

def test_two_sum_sorted():
    from problems.two_sum_sorted import two_sum_sorted
    check("two_sum_sorted", two_sum_sorted, ([2,7,11,15], 9), [0,1])
    check("two_sum_sorted", two_sum_sorted, ([1,2,3,4,4,9], 8), [3,4])

def test_longest_substring_without_repeating_characters():
    from problems.longest_substring_without_repeating_characters import \
        longest_substring_without_repeating_characters
    check("longest_substring_without_repeating_characters", longest_substring_without_repeating_characters, ("abcabcbb",), 3)
    check("longest_substring_without_repeating_characters", longest_substring_without_repeating_characters, ("bbbbb",), 1)
    check("longest_substring_without_repeating_characters", longest_substring_without_repeating_characters, ("pwwkew",), 3)

def test_group_anagrams():
    from problems.group_anagrams import group_anagrams
    check("group_anagrams", group_anagrams, ((["eat","tea","tan","ate","nat","bat"]).copy(),), [["ate","eat","tea"],["nat","tan"],["bat"]])

def test_top_k_frequent():
    from problems.top_k_frequent import top_k_frequent
    check("top_k_frequent", top_k_frequent, ([1,1,1,2,2,3], 2), [1,2])
    check("top_k_frequent", top_k_frequent, ([4,1,-1,2,-1,2,3], 2), [-1,2])

def test_kth_largest():
    from problems.kth_largest import kth_largest
    check("kth_largest", kth_largest, ([3,2,1,5,6,4], 2), 5)
    check("kth_largest", kth_largest, ([3,2,3,1,2,4,5,5,6], 4), 4)

def test_binary_search():
    from problems.binary_search import binary_search
    check("binary_search", binary_search, ([1,2,3,4,5], 4), 3)
    check("binary_search", binary_search, ([1,2,3,4,5], 6), -1)

def test_search_rotated_sorted_array():
    from problems.search_rotated_sorted_array import \
        search_rotated_sorted_array
    check("search_rotated_sorted_array", search_rotated_sorted_array, ([4,5,6,7,0,1,2], 0), 4)
    check("search_rotated_sorted_array", search_rotated_sorted_array, ([4,5,6,7,0,1,2], 3), -1)

def test_max_product_subarray():
    from problems.max_product_subarray import max_product_subarray
    check("max_product_subarray", max_product_subarray, ([2,3,-2,4],), 6)
    check("max_product_subarray", max_product_subarray, ([-2,0,-1],), 0)

def test_coin_change():
    from problems.coin_change import coin_change
    check("coin_change", coin_change, ([1,2,5], 11), 3)
    check("coin_change", coin_change, ([2], 3), -1)

def test_climb_stairs():
    from problems.climb_stairs import climb_stairs
    check("climb_stairs", climb_stairs, (2,), 2)
    check("climb_stairs", climb_stairs, (3,), 3)

def test_min_window_substring():
    from problems.min_window_substring import min_window_substring
    check("min_window_substring", min_window_substring, ("ADOBECODEBANC", "ABC"), "BANC")
    check("min_window_substring", min_window_substring, ("a", "aa"), "")

def test_longest_palindromic_substring():
    from problems.longest_palindromic_substring import \
        longest_palindromic_substring
    check("longest_palindromic_substring", longest_palindromic_substring, ("babad",), "bab")
    check("longest_palindromic_substring", longest_palindromic_substring, ("cbbd",), "bb")

def test_rotate_matrix():
    from problems.rotate_matrix import rotate_matrix
    check("rotate_matrix", rotate_matrix, ([[1,2,3],[4,5,6],[7,8,9]],), [[7,4,1],[8,5,2],[9,6,3]])

def test_number_of_islands():
    from problems.number_of_islands import number_of_islands
    grid = [["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]
    check("number_of_islands", number_of_islands, (grid,), 3)


def main():
    print("Running practice tests...\n")
    test_summation()
    test_palindrome()
    test_second_largest()
    test_frequency_sort()
    test_merge_intervals()
    test_two_sum()
    test_balanced_brackets()
    test_max_subarray()
    test_product_except_self()
    test_three_sum()
    test_two_sum_sorted()
    test_longest_substring_without_repeating_characters()
    test_group_anagrams()
    test_top_k_frequent()
    test_kth_largest()
    test_binary_search()
    test_search_rotated_sorted_array()
    test_max_product_subarray()
    test_coin_change()
    test_climb_stairs()
    test_min_window_substring()
    test_longest_palindromic_substring()
    test_rotate_matrix()
    test_number_of_islands()

    total = PASSED + FAILED + TODO
    print("\nSummary:")
    print(f"  Passed: {PASSED}")
    print(f"  Failed: {FAILED}")
    print(f"  TODO:   {TODO}")
    print(f"  Total:  {total}")

    # Exit non-zero only if there are failures (TODOs are allowed for practice)
    if FAILED > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
