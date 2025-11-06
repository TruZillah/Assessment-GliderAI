"""
Flask web app for practicing multi-language assessment problems in the browser.
Supports Python, JavaScript, Java, and C++.
"""

import io
import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import tempfile
import traceback
from contextlib import redirect_stderr, redirect_stdout
from typing import Optional
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder='static', static_url_path='')

# Simple .env loader to avoid extra deps
def _load_env_file(path: str = '.env'):
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()
    except FileNotFoundError:
        pass

def _parse_env_file(path: str = '.env') -> dict:
    """Parse .env file and return dict without modifying os.environ."""
    env_dict = {}
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '=' in line:
                    k, v = line.split('=', 1)
                    env_dict[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env_dict

def _validate_env_dict(env_dict: dict) -> bool:
    """Check if env dict has a valid OPENAI_API_KEY."""
    key = env_dict.get('OPENAI_API_KEY', '')
    return key.startswith('sk-') and len(key) > 20

def reload_env_if_valid() -> tuple:
    """
    Re-read .env if it exists and is valid, then return the effective API key and message.
    Returns (key, msg) tuple. Key from file if valid, else from os.environ, else None.
    """
    env_dict = _parse_env_file()
    if env_dict and _validate_env_dict(env_dict):
        # Valid .env found; update os.environ
        for k, v in env_dict.items():
            os.environ[k] = v
        return (env_dict.get('OPENAI_API_KEY'), 'loaded from .env')
    # Fallback to existing env
    existing = os.environ.get('OPENAI_API_KEY', '')
    if existing:
        return (existing, 'from environment')
    return (None, 'no API key found')

# Load .env on startup
_load_env_file()

# Initialize OpenAI configuration from environment
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4')

# Language executors
def execute_python(code: str, test_args: list, problem_name: str) -> tuple:
    """Execute Python code with test arguments."""
    namespace = {}
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    
    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, namespace)
            func = namespace.get(problem_name)
            if not func:
                raise NameError(f'Function {problem_name} not found')
            result = func(*test_args)
        return result, stdout_capture.getvalue(), stderr_capture.getvalue()
    except Exception as e:
        return None, stdout_capture.getvalue(), f'{type(e).__name__}: {e}'

def execute_javascript(code: str, test_args: list, problem_name: str) -> tuple:
    """Execute JavaScript code with Node.js."""
    temp_dir = tempfile.mkdtemp()
    try:
        js_file = os.path.join(temp_dir, 'solution.js')
        test_code = f"""{code}

// Test harness
const args = {json.dumps(test_args)};
const result = {problem_name}(...args);
console.log('RESULT:' + JSON.stringify(result));
"""
        with open(js_file, 'w') as f:
            f.write(test_code)
        
        proc = subprocess.run(
            ['node', js_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if proc.returncode != 0:
            raise RuntimeError(f'JavaScript error: {proc.stderr}')
        
        output = proc.stdout
        for line in output.split('\n'):
            if line.startswith('RESULT:'):
                result_str = line[7:]
                result = json.loads(result_str)
                return result, output, proc.stderr
        
        raise RuntimeError(f'Could not find RESULT in output: {output}')
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def execute_java(code: str, test_args: list, problem_name: str) -> tuple:
    """Execute Java code by compiling and running."""
    temp_dir = tempfile.mkdtemp()
    try:
        java_file = os.path.join(temp_dir, 'TestRunner.java')
        
        # Build test harness - simpler approach without external dependencies
        # Convert Python args to Java literals
        def python_to_java(val):
            if isinstance(val, bool):
                return 'true' if val else 'false'
            elif isinstance(val, str):
                # Escape quotes and backslashes
                escaped = val.replace('\\', '\\\\').replace('"', '\\"')
                return f'"{escaped}"'
            elif isinstance(val, (int, float)):
                return str(val)
            elif isinstance(val, (list, tuple)):
                items = ', '.join(python_to_java(v) for v in val)
                return f'new Object[]{{{items}}}'
            return str(val)
        
        java_args = ', '.join(python_to_java(arg) for arg in test_args)
        
        test_code = f"""
{code.replace('public class', 'class')}

public class TestRunner {{
    public static void main(String[] args) {{
        Solution sol = new Solution();
        Object result = sol.{problem_name}({java_args});
        System.out.println("RESULT:" + result);
    }}
}}
"""
        with open(java_file, 'w') as f:
            f.write(test_code)
        
        # Compile
        compile_proc = subprocess.run(
            ['javac', java_file],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=temp_dir
        )
        
        if compile_proc.returncode != 0:
            raise RuntimeError(f'Java compilation error: {compile_proc.stderr}')
        
        # Run
        run_proc = subprocess.run(
            ['java', '-cp', temp_dir, 'TestRunner'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if run_proc.returncode != 0:
            raise RuntimeError(f'Java runtime error: {run_proc.stderr}')
        
        output = run_proc.stdout
        for line in output.split('\n'):
            if line.startswith('RESULT:'):
                result_str = line[7:].strip()
                # Parse result
                try:
                    # Try to parse as number
                    if '.' in result_str:
                        result = float(result_str)
                    else:
                        result = int(result_str)
                except ValueError:
                    # Handle boolean or string
                    if result_str.lower() == 'true':
                        result = True
                    elif result_str.lower() == 'false':
                        result = False
                    else:
                        result = result_str
                return result, output, run_proc.stderr
        
        raise RuntimeError(f'Could not find RESULT in output: {output}')
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def execute_cpp(code: str, test_args: list, problem_name: str) -> tuple:
    """Execute C++ code by compiling with g++."""
    temp_dir = tempfile.mkdtemp()
    try:
        cpp_file = os.path.join(temp_dir, 'solution.cpp')
        exe_file = os.path.join(temp_dir, 'solution.exe' if os.name == 'nt' else 'solution')
        
        # Convert Python args to C++ literals
        def python_to_cpp(val):
            if isinstance(val, bool):
                return 'true' if val else 'false'
            elif isinstance(val, str):
                # Escape quotes and backslashes
                escaped = val.replace('\\', '\\\\').replace('"', '\\"')
                return f'"{escaped}"'
            elif isinstance(val, (int, float)):
                return str(val)
            return str(val)
        
        cpp_args = ', '.join(python_to_cpp(arg) for arg in test_args)
        
        test_code = f"""
#include <iostream>
#include <vector>
#include <string>
#include <sstream>
using namespace std;

{code}

int main() {{
    auto result = {problem_name}({cpp_args});
    cout << "RESULT:" << result << endl;
    return 0;
}}
"""
        with open(cpp_file, 'w') as f:
            f.write(test_code)
        
        # Compile
        compile_proc = subprocess.run(
            ['g++', '-std=c++17', cpp_file, '-o', exe_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if compile_proc.returncode != 0:
            raise RuntimeError(f'C++ compilation error: {compile_proc.stderr}')
        
        # Run
        run_proc = subprocess.run(
            [exe_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if run_proc.returncode != 0:
            raise RuntimeError(f'C++ runtime error: {run_proc.stderr}')
        
        # Parse result
        output = run_proc.stdout
        for line in output.split('\n'):
            if line.startswith('RESULT:'):
                result_str = line[7:].strip()
                try:
                    if '.' in result_str:
                        result = float(result_str)
                    else:
                        result = int(result_str)
                except ValueError:
                    # Handle boolean or string
                    if result_str == '1':
                        result = True
                    elif result_str == '0':
                        result = False
                    else:
                        result = result_str
                return result, output, run_proc.stderr
        
        raise RuntimeError(f'Could not find RESULT in output: {output}')
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


LANGUAGE_EXECUTORS = {
    'python': execute_python,
    'javascript': execute_javascript,
    'java': execute_java,
    'cpp': execute_cpp
}


PROBLEMS = {
    'summation': {
        'name': 'summation',
        'title': 'Sum of Two Integers',
        'description': 'Implement summation(a, b) that returns the sum of two integers.',
        'signature': 'def summation(a, b):',
        'stubs': {
            'python': 'def summation(a, b):\n    # Write your code here\n    pass\n',
            'javascript': 'function summation(a, b) {\n    // Write your code here\n}\n',
            'java': 'public class Solution {\n    public int summation(int a, int b) {\n        // Write your code here\n        return 0;\n    }\n}\n',
            'cpp': 'int summation(int a, b) {\n    // Write your code here\n    return 0;\n}\n'
        },
        'tests': [
            {'args': (2, 3), 'expected': 5},
            {'args': (-1, 1), 'expected': 0},
            {'args': (0, 0), 'expected': 0},
        ]
    },
    'palindrome': {
        'name': 'palindrome',
        'title': 'Is Palindrome',
        'description': 'Implement is_palindrome(s) that checks if a string is a palindrome (ignore non-alphanumeric, case-insensitive).',
        'signature': 'def is_palindrome(s):',
        'stubs': {
            'python': 'def is_palindrome(s):\n    # Write your code here\n    pass\n',
            'javascript': 'function is_palindrome(s) {\n    // Write your code here\n}\n',
            'java': 'public class Solution {\n    public boolean is_palindrome(String s) {\n        // Write your code here\n        return false;\n    }\n}\n',
            'cpp': 'bool is_palindrome(string s) {\n    // Write your code here\n    return false;\n}\n'
        },
        'tests': [
            {'args': ("A man, a plan, a canal: Panama",), 'expected': True},
            {'args': ("race a car",), 'expected': False},
            {'args': ("",), 'expected': True},
        ]
    },
    'second_largest': {
        'name': 'second_largest',
        'title': 'Second Largest',
        'description': 'Implement second_largest(nums) that returns the second largest distinct integer, or None if it doesn\'t exist.',
        'signature': 'def second_largest(nums):',
        'tests': [
            {'args': ([2, 3, 1],), 'expected': 2},
            {'args': ([5, 5, 5],), 'expected': None},
            {'args': ([-1, -2, -3],), 'expected': -2},
        ]
    },
    'frequency_sort': {
        'name': 'frequency_sort',
        'title': 'Frequency Sort',
        'description': 'Implement frequency_sort(s) that sorts characters by frequency (desc), then alphabetically (asc).',
        'signature': 'def frequency_sort(s):',
        'tests': [
            {'args': ("tree",), 'expected': "eert"},
            {'args': ("cccaaa",), 'expected': "aaaccc"},
            {'args': ("",), 'expected': ""},
        ]
    },
    'merge_intervals': {
        'name': 'merge_intervals',
        'title': 'Merge Intervals',
        'description': 'Implement merge_intervals(intervals) that merges overlapping intervals.',
        'signature': 'def merge_intervals(intervals):',
        'tests': [
            {'args': ([[1,3],[2,6],[8,10],[15,18]],), 'expected': [[1,6],[8,10],[15,18]]},
            {'args': ([[1,4],[4,5]],), 'expected': [[1,5]]},
            {'args': ([],), 'expected': []},
        ]
    },
    'two_sum': {
        'name': 'two_sum',
        'title': 'Two Sum',
        'description': 'Implement two_sum(nums, target) that returns indices [i,j] summing to target, or [-1,-1].',
        'signature': 'def two_sum(nums, target):',
        'stubs': {
            'python': 'def two_sum(nums, target):\n    # Write your code here\n    pass\n',
            'javascript': 'function two_sum(nums, target) {\n    // Write your code here\n}\n',
            'java': 'public class Solution {\n    public int[] two_sum(int[] nums, int target) {\n        // Write your code here\n        return new int[]{-1, -1};\n    }\n}\n',
            'cpp': 'vector<int> two_sum(vector<int>& nums, int target) {\n    // Write your code here\n    return {-1, -1};\n}\n'
        },
        'tests': [
            {'args': ([2,7,11,15], 9), 'expected': [0,1]},
            {'args': ([3,2,4], 6), 'expected': [1,2]},
            {'args': ([3,3], 6), 'expected': [0,1]},
            {'args': ([1,2,3], 10), 'expected': [-1,-1]},
        ]
    },
    'balanced_brackets': {
        'name': 'balanced_brackets',
        'title': 'Balanced Brackets',
        'description': 'Implement balanced_brackets(s) that checks if brackets are balanced: (), {}, []',
        'signature': 'def balanced_brackets(s):',
        'tests': [
            {'args': ("()[]{}",), 'expected': True},
            {'args': ("(]",), 'expected': False},
            {'args': ("([{}])",), 'expected': True},
        ]
    },
    # --- Added harder problems below ---
    'max_subarray': {
        'name': 'max_subarray',
        'title': 'Maximum Subarray Sum',
        'description': 'Implement max_subarray(nums) returning the maximum possible subarray sum (Kadane\'s algorithm).',
        'signature': 'def max_subarray(nums):',
        'tests': [
            {'args': ([-2,1,-3,4,-1,2,1,-5,4],), 'expected': 6},  # [4,-1,2,1]
            {'args': ([1],), 'expected': 1},
            {'args': ([-1,-2,-3],), 'expected': -1},
        ]
    },
    'product_except_self': {
        'name': 'product_except_self',
        'title': 'Product of Array Except Self',
        'description': 'Implement product_except_self(nums) without using division, return an array where each element is the product of all other elements.',
        'signature': 'def product_except_self(nums):',
        'tests': [
            {'args': ([1,2,3,4],), 'expected': [24,12,8,6]},
            {'args': ([0,1,2,3],), 'expected': [6,0,0,0]},
        ]
    },
    'three_sum': {
        'name': 'three_sum',
        'title': '3Sum',
        'description': 'Implement three_sum(nums) returning a list of unique triplets [a,b,c] such that a+b+c=0. Order of triplets and elements within triplets does not matter.',
        'signature': 'def three_sum(nums):',
        'tests': [
            {'args': ([-1,0,1,2,-1,-4],), 'expected': [[-1,-1,2],[-1,0,1]]},
            {'args': ([0,1,1],), 'expected': []},
        ]
    },
    'two_sum_sorted': {
        'name': 'two_sum_sorted',
        'title': 'Two Sum II (Sorted)',
        'description': 'Implement two_sum_sorted(nums, target) where nums is sorted ascending, return 0-based indices [i,j] or [-1,-1].',
        'signature': 'def two_sum_sorted(nums, target):',
        'tests': [
            {'args': ([2,7,11,15], 9), 'expected': [0,1]},
            {'args': ([1,2,3,4,4,9], 8), 'expected': [3,4]},
        ]
    },
    'longest_substring_without_repeating_characters': {
        'name': 'longest_substring_without_repeating_characters',
        'title': 'Longest Substring Without Repeating Characters',
        'description': 'Implement longest_substring_without_repeating_characters(s) and return its length.',
        'signature': 'def longest_substring_without_repeating_characters(s):',
        'tests': [
            {'args': ("abcabcbb",), 'expected': 3},
            {'args': ("bbbbb",), 'expected': 1},
            {'args': ("pwwkew",), 'expected': 3},
        ]
    },
    'group_anagrams': {
        'name': 'group_anagrams',
        'title': 'Group Anagrams',
        'description': 'Implement group_anagrams(strs) that groups words that are anagrams. Return groups sorted internally and externally for determinism.',
        'signature': 'def group_anagrams(strs):',
        'tests': [
            {'args': ((["eat","tea","tan","ate","nat","bat"]).copy(),), 'expected': [["ate","eat","tea"],["nat","tan"],["bat"]]},
        ]
    },
    'top_k_frequent': {
        'name': 'top_k_frequent',
        'title': 'Top K Frequent Elements',
        'description': 'Implement top_k_frequent(nums, k) returning a list of k most frequent elements (any order acceptable, but sort ascending for determinism).',
        'signature': 'def top_k_frequent(nums, k):',
        'tests': [
            {'args': ([1,1,1,2,2,3], 2), 'expected': [1,2]},
            {'args': ([4,1,-1,2,-1,2,3], 2), 'expected': [-1,2]},
        ]
    },
    'kth_largest': {
        'name': 'kth_largest',
        'title': 'Kth Largest Element',
        'description': 'Implement kth_largest(nums, k) returning the k-th largest element in the array.',
        'signature': 'def kth_largest(nums, k):',
        'tests': [
            {'args': ([3,2,1,5,6,4], 2), 'expected': 5},
            {'args': ([3,2,3,1,2,4,5,5,6], 4), 'expected': 4},
        ]
    },
    'binary_search': {
        'name': 'binary_search',
        'title': 'Binary Search',
        'description': 'Implement binary_search(nums, target) returning index or -1. nums is sorted ascending.',
        'signature': 'def binary_search(nums, target):',
        'tests': [
            {'args': ([1,2,3,4,5], 4), 'expected': 3},
            {'args': ([1,2,3,4,5], 6), 'expected': -1},
        ]
    },
    'search_rotated_sorted_array': {
        'name': 'search_rotated_sorted_array',
        'title': 'Search in Rotated Sorted Array',
        'description': 'Implement search_rotated_sorted_array(nums, target) returning index or -1.',
        'signature': 'def search_rotated_sorted_array(nums, target):',
        'tests': [
            {'args': ([4,5,6,7,0,1,2], 0), 'expected': 4},
            {'args': ([4,5,6,7,0,1,2], 3), 'expected': -1},
        ]
    },
    'max_product_subarray': {
        'name': 'max_product_subarray',
        'title': 'Maximum Product Subarray',
        'description': 'Implement max_product_subarray(nums) returning the maximum product of a contiguous subarray.',
        'signature': 'def max_product_subarray(nums):',
        'tests': [
            {'args': ([2,3,-2,4],), 'expected': 6},
            {'args': ([-2,0,-1],), 'expected': 0},
        ]
    },
    'coin_change': {
        'name': 'coin_change',
        'title': 'Coin Change (Min Coins)',
        'description': 'Implement coin_change(coins, amount) to return the minimum number of coins to make up amount, or -1 if not possible.',
        'signature': 'def coin_change(coins, amount):',
        'tests': [
            {'args': ([1,2,5], 11), 'expected': 3},
            {'args': ([2], 3), 'expected': -1},
        ]
    },
    'climb_stairs': {
        'name': 'climb_stairs',
        'title': 'Climbing Stairs',
        'description': 'Implement climb_stairs(n) where you can climb 1 or 2 steps at a time; return number of distinct ways.',
        'signature': 'def climb_stairs(n):',
        'tests': [
            {'args': (2,), 'expected': 2},
            {'args': (3,), 'expected': 3},
        ]
    },
    'min_window_substring': {
        'name': 'min_window_substring',
        'title': 'Minimum Window Substring',
        'description': 'Implement min_window_substring(s, t) returning the smallest substring of s that contains all chars of t (with multiplicity). Return "" if none.',
        'signature': 'def min_window_substring(s, t):',
        'tests': [
            {'args': ("ADOBECODEBANC", "ABC"), 'expected': "BANC"},
            {'args': ("a", "aa"), 'expected': ""},
        ]
    },
    'longest_palindromic_substring': {
        'name': 'longest_palindromic_substring',
        'title': 'Longest Palindromic Substring',
        'description': 'Implement longest_palindromic_substring(s) returning one longest palindromic substring.',
        'signature': 'def longest_palindromic_substring(s):',
        'tests': [
            {'args': ("babad",), 'expected': "bab"},
            {'args': ("cbbd",), 'expected': "bb"},
        ]
    },
    'rotate_matrix': {
        'name': 'rotate_matrix',
        'title': 'Rotate Matrix 90°',
        'description': 'Implement rotate_matrix(matrix) to return a new matrix rotated 90 degrees clockwise.',
        'signature': 'def rotate_matrix(matrix):',
        'tests': [
            {'args': ([[1,2,3],[4,5,6],[7,8,9]],), 'expected': [[7,4,1],[8,5,2],[9,6,3]]},
        ]
    },
    'number_of_islands': {
        'name': 'number_of_islands',
        'title': 'Number of Islands',
        'description': 'Implement number_of_islands(grid) where grid is a list of list of "1" and "0"; return count of islands (4-direction).',
        'signature': 'def number_of_islands(grid):',
        'tests': [
            {'args': (([["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]),), 'expected': 3},
        ]
    },
}

# Optional per-problem hints shown in the UI
HINTS = {
    'summation': {
        'python': {
            'bullets': [
                'Step 1: This is a simple function that returns the sum of two integers.',
                'Step 2: In Python, the + operator works directly on integers with no overflow concerns.',
                'Step 3: Python integers have arbitrary precision - they can grow as large as memory allows.',
                'Step 4: Simply return a + b. No need for type checking or edge cases.',
                'Example: summation(5, 3) → 8, summation(-10, 20) → 10',
            ],
            'pseudocode': 'def summation(a, b):\\n    # Return the sum of two integers\\n    return a + b\\n'
        },
        'javascript': {
            'bullets': [
                'Be careful with implicit type coercion; ensure inputs are numbers.',
                'Return a + b; Node.js will handle number addition.',
            ],
            'pseudocode': 'function summation(a, b) {\\n    return a + b;\\n}\\n'
        },
        'java': {
            'bullets': [
                'Use primitive ints to avoid boxing overhead.',
                'Return a + b from the method.',
            ],
            'pseudocode': 'public int summation(int a, int b) {\\n    return a + b;\\n}\\n'
        },
        'cpp': {
            'bullets': [
                'Use int (or long) depending on expected range.',
                'Return a + b from the function.',
            ],
            'pseudocode': 'int summation(int a, int b) {\\n    return a + b;\\n}\\n'
        },
    },
    'palindrome': {
        'python': {
            'bullets': [
                'Step 1: A palindrome reads the same forward and backward (e.g., "racecar", "A man a plan a canal Panama").',
                'Step 2: First, filter the string to keep only alphanumeric characters (letters and numbers).',
                'Step 3: Use str.isalnum() to check if a character is alphanumeric, and convert to lowercase with .lower().',
                'Step 4: Build a filtered list using list comprehension: [c.lower() for c in s if c.isalnum()].',
                'Step 5: Use two pointers: i starts at 0 (beginning), j starts at len(t)-1 (end).',
                'Step 6: Compare characters at i and j. If they don\'t match, it\'s not a palindrome - return False.',
                'Step 7: Move pointers inward: i += 1, j -= 1. Continue until pointers meet.',
                'Step 8: If all comparisons match, return True. Empty string is considered a palindrome.',
                'Example: "A man, a plan, a canal: Panama" → filtered:"amanaplanacanalpanama" → palindrome!',
            ],
            'pseudocode': 'def is_palindrome(s):\\n    # Step 1: Filter to alphanumeric and lowercase\\n    t = [c.lower() for c in s if c.isalnum()]\\n    \\n    # Step 2: Two pointers from both ends\\n    i, j = 0, len(t)-1\\n    \\n    # Step 3: Compare characters while moving inward\\n    while i < j:\\n        if t[i] != t[j]:\\n            return False  # Mismatch found\\n        i += 1\\n        j -= 1\\n    \\n    # Step 4: All characters matched\\n    return True\\n'
        },
        'javascript': {
            'bullets': [
                'Normalize with regex: keep alphanumeric and toLowerCase().',
                'Use two indices or reverse the string and compare.',
            ],
            'pseudocode': 'function is_palindrome(s) {\\n    const t = s.replace(/[^a-z0-9]/gi, "").toLowerCase();\\n    return t === t.split("").reverse().join("");\\n}\\n'
        },
        'java': {
            'bullets': [
                'Use Character.isLetterOrDigit and Character.toLowerCase for normalization.',
                'Use two-pointer approach on a char array.',
            ],
            'pseudocode': 'public boolean is_palindrome(String s) {\\n    StringBuilder sb = new StringBuilder();\\n    for (char c: s.toCharArray()) if (Character.isLetterOrDigit(c)) sb.append(Character.toLowerCase(c));\\n    String t = sb.toString(); return new StringBuilder(t).reverse().toString().equals(t);\\n}\\n'
        },
        'cpp': {
            'bullets': [
                'Use isalnum from <cctype> and tolower for normalization.',
                'Build a filtered string and compare with reverse.',
            ],
            'pseudocode': 'bool is_palindrome(string s) {\\n    string t; for (char c: s) if (isalnum((unsigned char)c)) t.push_back(tolower((unsigned char)c)); return equal(t.begin(), t.begin()+t.size()/2, t.rbegin());\\n}\\n'
        },
    },
    'second_largest': {
        'python': {
            'bullets': [
                'Step 1: Find the second largest DISTINCT value in an array. Duplicates don\'t count.',
                'Step 2: Track two variables: top1 (largest) and top2 (second largest). Initialize both to None.',
                'Step 3: For each element x in the array, check if it\'s larger than top1.',
                'Step 4: If x > top1 (or top1 is None), update top2 to the old top1 value, then update top1 to x.',
                'Step 5: IMPORTANT: Only update top2 if x is different from top1 (skip duplicates).',
                'Step 6: Else if x < top1 but x > top2 (and x != top1), update top2 to x.',
                'Step 7: After processing all elements, return top2.',
                'Step 8: Edge case: If array has fewer than 2 distinct values, top2 will be None.',
                'Example: [5,3,5,9,3,7] → top1=9, top2=7 (skipped duplicate 5s and 3s)',
            ],
            'pseudocode': 'def second_largest(nums):\\n    # Step 1: Initialize tracking variables\\n    top1 = top2 = None\\n    \\n    # Step 2: Process each number\\n    for x in nums:\\n        # Step 3: Check if new largest\\n        if top1 is None or x > top1:\\n            # Update top2 only if x is distinct\\n            if x != top1:\\n                top2 = top1\\n            top1 = x\\n        # Step 4: Check if new second largest\\n        elif x != top1 and (top2 is None or x > top2):\\n            top2 = x\\n    \\n    return top2\\n'
        },
        'javascript': {
            'bullets': [
                'Track top1 and top2 distinct values in one pass.',
                'Update top2 when you update top1; skip duplicates.',
            ],
            'pseudocode': 'function secondLargest(nums) {\\n    let top1 = null, top2 = null;\\n    for (const x of nums) {\\n        if (top1 === null || x > top1) { if (x !== top1) top2 = top1; top1 = x; }\\n        else if (x !== top1 && (top2 === null || x > top2)) top2 = x;\\n    }\\n    return top2;\\n}\\n'
        },
        'java': {
            'bullets': [
                'Track top1 and top2 distinct values in one pass.',
                'Update top2 when you update top1; skip duplicates.',
            ],
            'pseudocode': 'Integer secondLargest(int[] nums) {\\n    Integer top1 = null, top2 = null;\\n    for (int x : nums) {\\n        if (top1 == null || x > top1) { if (x != top1) top2 = top1; top1 = x; }\\n        else if (x != top1 && (top2 == null || x > top2)) top2 = x;\\n    }\\n    return top2;\\n}\\n'
        },
        'cpp': {
            'bullets': [
                'Track top1 and top2 distinct values in one pass.',
                'Update top2 when you update top1; skip duplicates.',
            ],
            'pseudocode': 'int secondLargest(vector<int>& nums) {\\n    int top1 = INT_MIN, top2 = INT_MIN;\\n    bool has1 = false, has2 = false;\\n    for (int x : nums) {\\n        if (!has1 || x > top1) { if (has1 && x != top1) { top2 = top1; has2 = true; } top1 = x; has1 = true; }\\n        else if (x != top1 && (!has2 || x > top2)) { top2 = x; has2 = true; }\\n    }\\n    return has2 ? top2 : INT_MIN;\\n}\\n'
        },
    },
    'frequency_sort': {
        'python': {
            'bullets': [
                'Step 1: Import Counter from collections module - a dictionary subclass for counting hashable objects.',
                'Step 2: Use Counter(s) to count frequency of each character. Returns a dict where keys are characters and values are their counts.',
                'Step 3: Sort using sorted() with a custom key. The lambda function returns a tuple: (-frequency, character).',
                'Step 4: Negative frequency ensures descending order (most frequent first). Character ensures lexicographical order for ties.',
                'Step 5: Use list comprehension to repeat each character by its frequency: ch*freq.',
                'Step 6: Join all repeated characters into a single string with "".join().',
                'Example: "tree" → Counter: {"t":1,"r":1,"e":2} → sorted: [("e",2),("r",1),("t",1)] → "eerт" or "eert"',
            ],
            'pseudocode': 'from collections import Counter\\n\\ndef frequency_sort(s):\\n    # Step 1: Count character frequencies\\n    counts = Counter(s)\\n    \\n    # Step 2: Sort by frequency (desc), then lexicographically (asc)\\n    parts = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))\\n    \\n    # Step 3: Repeat each character by its frequency and join\\n    return "".join(ch*freq for ch,freq in parts)\\n'
        },
        'javascript': {
            'bullets': [
                'Count with a Map/object.',
                'Sort by (-freq, char).',
            ],
            'pseudocode': 'function frequencySort(s) {\\n    const counts = new Map();\\n    for (const c of s) counts.set(c, (counts.get(c) || 0) + 1);\\n    const parts = [...counts.entries()].sort((a,b) => b[1]-a[1] || a[0].localeCompare(b[0]));\\n    return parts.map(([ch, f]) => ch.repeat(f)).join("");\\n}\\n'
        },
        'java': {
            'bullets': [
                'Count with HashMap and sort entries.',
                'Sort by freq desc then char asc.',
            ],
            'pseudocode': 'String frequencySort(String s) {\\n    Map<Character, Integer> cnt = new HashMap<>();\\n    for (char c : s.toCharArray()) cnt.put(c, cnt.getOrDefault(c, 0) + 1);\\n    // Sort and build result\\n}\\n'
        },
        'cpp': {
            'bullets': [
                'Count with unordered_map and sort vector of pairs.',
                'Sort by freq desc then char asc.',
            ],
            'pseudocode': 'string frequencySort(string s) {\\n    unordered_map<char, int> cnt;\\n    for (char c : s) cnt[c]++;\\n    vector<pair<char, int>> v(cnt.begin(), cnt.end());\\n    sort(v.begin(), v.end(), [](auto &a, auto &b) {\\n        return a.second != b.second ? a.second > b.second : a.first < b.first;\\n    });\\n    string out;\\n    for (auto &p : v) out += string(p.second, p.first);\\n    return out;\\n}\\n'
        },
    },
    'merge_intervals': {
        'python': {
            'bullets': [
                'Step 1: An interval is [start, end]. Overlapping intervals should be merged into one.',
                'Step 2: First, sort all intervals by their start time. This groups overlapping intervals together.',
                'Step 3: Use key=lambda x: x[0] to sort by the first element (start time).',
                'Step 4: Initialize an empty result list to store merged intervals.',
                'Step 5: For each interval [s, e], check if it overlaps with the last interval in result.',
                'Step 6: Intervals overlap if current start <= last end. Example: [1,3] and [2,6] overlap.',
                'Step 7: If NO overlap (s > res[-1][1]), append the interval as a new entry.',
                'Step 8: If overlap, merge by updating the end: res[-1][1] = max(res[-1][1], e).',
                'Step 9: Time: O(n log n) for sorting + O(n) for merging = O(n log n).',
                'Example: [[1,3],[2,6],[8,10],[15,18]] → sorted → merge [1,3] & [2,6] → [[1,6],[8,10],[15,18]]',
            ],
            'pseudocode': 'def merge_intervals(intervals):\\n    # Step 1: Sort by start time\\n    intervals.sort(key=lambda x: x[0])\\n    \\n    # Step 2: Initialize result list\\n    res = []\\n    \\n    # Step 3: Process each interval\\n    for s, e in intervals:\\n        # Step 4: Check if overlaps with last interval\\n        if not res or s > res[-1][1]:\\n            # No overlap - add as new interval\\n            res.append([s, e])\\n        else:\\n            # Overlap - merge by extending end\\n            res[-1][1] = max(res[-1][1], e)\\n    \\n    return res\\n'
        },
        'javascript': {
            'bullets': [
                'Sort and merge intervals similarly.',
            ],
            'pseudocode': 'function mergeIntervals(intervals) {\\n    intervals.sort((a, b) => a[0] - b[0]);\\n    const res = [];\\n    for (const [s, e] of intervals) {\\n        if (!res.length || s > res[res.length-1][1]) res.push([s, e]);\\n        else res[res.length-1][1] = Math.max(res[res.length-1][1], e);\\n    }\\n    return res;\\n}\\n'
        },
        'java': {
            'bullets': [
                'Sort intervals and merge in one pass.',
            ],
            'pseudocode': 'int[][] mergeIntervals(int[][] intervals) {\\n    Arrays.sort(intervals, (a, b) -> a[0] - b[0]);\\n    List<int[]> res = new ArrayList<>();\\n    for (int[] it : intervals) {\\n        if (res.isEmpty() || it[0] > res.get(res.size()-1)[1]) res.add(it);\\n        else res.get(res.size()-1)[1] = Math.max(res.get(res.size()-1)[1], it[1]);\\n    }\\n    return res.toArray(new int[res.size()][]);\\n}\\n'
        },
        'cpp': {
            'bullets': [
                'Sort and merge intervals.',
            ],
            'pseudocode': 'vector<vector<int>> mergeIntervals(vector<vector<int>>& intervals) {\\n    sort(intervals.begin(), intervals.end());\\n    vector<vector<int>> res;\\n    for (auto &v : intervals) {\\n        if (res.empty() || v[0] > res.back()[1]) res.push_back(v);\\n        else res.back()[1] = max(res.back()[1], v[1]);\\n    }\\n    return res;\\n}\\n'
        },
    },
    'two_sum': {
        'python': {
            'bullets': [
                'Step 1: Create an empty dictionary called "seen" to store value→index mappings.',
                'Step 2: Iterate through the array with enumerate() to get both index and value.',
                'Step 3: For each element x, calculate the complement y = target - x.',
                'Step 4: Check if complement y exists in the "seen" dictionary. If yes, we found our pair!',
                'Step 5: Return [seen[y], i] - the index of the complement and current index.',
                'Step 6: If not found, add current value to "seen": seen[x] = i.',
                'Step 7: We check BEFORE inserting to avoid using the same element twice.',
                'Example: nums=[2,7,11,15], target=9 → i=0:seen={}, y=7, add 2→0 → i=1:y=2, found! return [0,1]',
            ],
            'pseudocode': 'def two_sum(nums, target):\\n    # Step 1: Create hashmap to store value→index\\n    seen = {}\\n    \\n    # Step 2: Iterate with index and value\\n    for i, x in enumerate(nums):\\n        # Step 3: Calculate complement\\n        y = target - x\\n        \\n        # Step 4: Check if complement exists\\n        if y in seen:\\n            return [seen[y], i]\\n        \\n        # Step 5: Store current value and index\\n        seen[x] = i\\n    \\n    return [-1, -1]  # No solution found\\n'
        },
        'javascript': {
            'bullets': [
                'Use a Map to store seen values to indices.',
                'Be mindful of === vs == when comparing.',
            ],
            'pseudocode': 'function two_sum(nums, target) {\\n    const seen = new Map();\\n    for (let i = 0; i < nums.length; i++) {\\n        const y = target - nums[i];\\n        if (seen.has(y)) return [seen.get(y), i];\\n        seen.set(nums[i], i);\\n    }\\n    return [-1, -1];\\n}\\n'
        },
        'java': {
            'bullets': [
                'Use HashMap<Integer,Integer> to map value→index.',
                'Beware of integer boxing/unboxing; use primitives where convenient.',
            ],
            'pseudocode': 'public int[] two_sum(int[] nums, int target) {\\n    Map<Integer,Integer> seen = new HashMap<>();\\n    for (int i=0;i<nums.length;i++) {\\n        int y = target - nums[i];\\n        if (seen.containsKey(y)) return new int[]{seen.get(y), i};\\n        seen.put(nums[i], i);\\n    }\\n    return new int[]{-1,-1};\\n}\\n'
        },
        'cpp': {
            'bullets': [
                'Use unordered_map<int,int> for O(1) lookups.',
                'Return vector<int>{idx1, idx2} or {-1,-1} if not found.',
            ],
            'pseudocode': 'vector<int> two_sum(vector<int>& nums, int target) {\\n    unordered_map<int,int> seen;\\n    for (int i=0;i<nums.size();++i) {\\n        int y = target - nums[i];\\n        if (seen.count(y)) return {seen[y], i};\\n        seen[nums[i]] = i;\\n    }\\n    return {-1,-1};\\n}\\n'
        },
    },
    'balanced_brackets': {
        'python': {
            'bullets': [
                'Step 1: Create a dictionary mapping each closing bracket to its corresponding opening bracket.',
                'Step 2: Initialize an empty list to use as a stack. Stack follows LIFO (Last In First Out).',
                'Step 3: Iterate through each character in the string.',
                'Step 4: If the character is an opening bracket "([{", push it onto the stack.',
                'Step 5: If it\'s a closing bracket ")]}", check if stack is empty or top doesn\'t match - return False.',
                'Step 6: If it matches, pop the opening bracket from the stack.',
                'Step 7: After processing all characters, return True if stack is empty (all brackets matched).',
                'Example: "({[]})" → push(, push{, push[, pop[ matches ], pop{ matches }, pop( matches ) → stack empty → valid!',
            ],
            'pseudocode': 'def is_valid(s):\\n    # Step 1: Map closing brackets to opening brackets\\n    pairs = {")": "(", "]": "[", "}": "{"}\\n    \\n    # Step 2: Initialize stack\\n    stack = []\\n    \\n    # Step 3: Process each character\\n    for c in s:\\n        # Step 4: If opening bracket, push to stack\\n        if c in "([{":\\n            stack.append(c)\\n        # Step 5: If closing bracket, validate\\n        elif c in ")]}":\\n            if not stack or stack[-1] != pairs[c]:\\n                return False\\n            # Step 6: Pop matching opening bracket\\n            stack.pop()\\n    \\n    # Step 7: Valid if all brackets matched (stack empty)\\n    return not stack\\n'
        },
        'javascript': {
            'bullets': [
                'Use an array as a stack, map closing to opening char.',
            ],
            'pseudocode': 'function isValid(s) {\\n    const pairs = {")":"(", "]":"[", "}":"{"};\\n    const st = [];\\n    for (const c of s) {\\n        if ("([{".includes(c)) st.push(c);\\n        else if (st.length === 0 || st.pop() !== pairs[c]) return false;\\n    }\\n    return st.length === 0;\\n}\\n'
        },
        'java': {
            'bullets': [
                'Use Deque/Stack to track opens.',
            ],
            'pseudocode': 'boolean isValid(String s) {\\n    Map<Character,Character> pairs = Map.of(\\n        \\\')\\\', \\\'(\\\', \\\']\\\', \\\'[\\\', \\\'}\\\', \\\'{\\\');\\n    Deque<Character> st = new ArrayDeque<>();\\n    for (char c : s.toCharArray()) {\\n        if (pairs.containsValue(c)) st.push(c);\\n        else if (st.isEmpty() || st.pop() != pairs.get(c)) return false;\\n    }\\n    return st.isEmpty();\\n}\\n'
        },
        'cpp': {
            'bullets': [
                'Use vector<char> as stack and mapping for closes.',
            ],
            'pseudocode': 'bool isValid(string s) {\\n    unordered_map<char,char> pairs = {{\\\')\\\',\\\'(\\\'},{\\\']\\\',\\\'[\\\'},{\\\'}\\\',\\\'{\\\'}}; \\n    vector<char> st;\\n    for (char c : s) {\\n        if (c==\\\'(\\\'||c==\\\'[\\\'||c==\\\'{\\\') st.push_back(c);\\n        else if (st.empty() || st.back()!=pairs[c]) return false; else st.pop_back();\\n    }\\n    return st.empty();\\n}\\n'
        },
    },
    'max_subarray': {
        'python': {
            'bullets': [
                'Step 1: This is Kadane\'s Algorithm - a classic dynamic programming approach for maximum subarray sum.',
                'Step 2: Initialize both "best" and "current" to the first element of the array.',
                'Step 3: "current" represents the maximum sum ending at the current position.',
                'Step 4: "best" represents the maximum sum found so far across all positions.',
                'Step 5: For each element x (starting from index 1), decide: start fresh with x, or extend previous subarray with cur+x.',
                'Step 6: Update current = max(x, current + x). If cur+x is negative, it\'s better to start fresh.',
                'Step 7: Update best = max(best, current) to track the overall maximum.',
                'Step 8: Why it works: negative prefixes only hurt future sums, so we discard them.',
                'Example: [-2,1,-3,4,-1,2,1,-5,4] → cur at index 3 becomes 4 (start fresh), then 3,5,6... best=6',
            ],
            'pseudocode': 'def max_subarray(nums):\\n    # Step 1: Initialize with first element\\n    best = current = nums[0]\\n    \\n    # Step 2: Process remaining elements\\n    for x in nums[1:]:\\n        # Step 3: Decide to extend or start fresh\\n        current = max(x, current + x)\\n        \\n        # Step 4: Update global maximum\\n        best = max(best, current)\\n    \\n    return best\\n'
        },
        'javascript': {
            'bullets': [
                "Kadane's algorithm",
            ],
            'pseudocode': 'function maxSubarray(nums) {\\n    let best = nums[0], cur = nums[0];\\n    for (let i = 1; i < nums.length; i++) {\\n        cur = Math.max(nums[i], cur + nums[i]);\\n        best = Math.max(best, cur);\\n    }\\n    return best;\\n}\\n'
        },
        'java': {
            'bullets': [
                "Kadane's algorithm",
            ],
            'pseudocode': 'int maxSubarray(int[] nums) {\\n    int best = nums[0], cur = nums[0];\\n    for (int i = 1; i < nums.length; i++) {\\n        cur = Math.max(nums[i], cur + nums[i]);\\n        best = Math.max(best, cur);\\n    }\\n    return best;\\n}\\n'
        },
        'cpp': {
            'bullets': [
                "Kadane's algorithm",
            ],
            'pseudocode': 'int maxSubarray(vector<int>& nums) {\\n    int best = nums[0], cur = nums[0];\\n    for (size_t i = 1; i < nums.size(); ++i) {\\n        cur = max(nums[i], cur + nums[i]);\\n        best = max(best, cur);\\n    }\\n    return best;\\n}\\n'
        },
    },
    'product_except_self': {
        'python': {
            'bullets': [
                'Step 1: The goal is to compute products of all elements except self WITHOUT using division.',
                'Step 2: Key insight: result[i] = (product of all elements before i) × (product of all elements after i).',
                'Step 3: Initialize result array with all 1s of length n.',
                'Step 4: FIRST PASS (left to right): Build prefix products. For each position i, store product of all elements to the left.',
                'Step 5: Use variable "pre" to track running product. Start pre=1, then res[i]=pre, then pre*=nums[i].',
                'Step 6: SECOND PASS (right to left): Multiply by suffix products. For each position i, multiply by product of all elements to the right.',
                'Step 7: Use variable "suf" to track running product from right. Start suf=1, then res[i]*=suf, then suf*=nums[i].',
                'Step 8: Time: O(n), Space: O(1) extra (output doesn\'t count).',
                'Example: [1,2,3,4] → prefix:[1,1,2,6] → suffix:[24,12,4,1] → result:[24,12,8,6]',
            ],
            'pseudocode': 'def product_except_self(nums):\\n    n = len(nums)\\n    res = [1] * n\\n    \\n    # First pass: prefix products\\n    pre = 1\\n    for i in range(n):\\n        res[i] = pre  # Product of all elements before i\\n        pre *= nums[i]\\n    \\n    # Second pass: suffix products\\n    suf = 1\\n    for i in range(n-1, -1, -1):\\n        res[i] *= suf  # Multiply by product of all elements after i\\n        suf *= nums[i]\\n    \\n    return res\\n'
        },
        'javascript': {
            'bullets': [
                'Compute prefix and suffix products.',
            ],
            'pseudocode': 'function productExceptSelf(nums) {\\n    const n = nums.length, res = Array(n).fill(1);\\n    let pre = 1;\\n    for (let i = 0; i < n; i++) { res[i] = pre; pre *= nums[i]; }\\n    let suf = 1;\\n    for (let i = n-1; i >= 0; i--) { res[i] *= suf; suf *= nums[i]; }\\n    return res;\\n}\\n'
        },
        'java': {
            'bullets': [
                'Compute prefix and suffix without division.',
            ],
            'pseudocode': 'int[] productExceptSelf(int[] nums) {\\n    int n = nums.length, res[] = new int[n];\\n    Arrays.fill(res, 1);\\n    int pre = 1;\\n    for (int i = 0; i < n; i++) { res[i] = pre; pre *= nums[i]; }\\n    int suf = 1;\\n    for (int i = n-1; i >= 0; i--) { res[i] *= suf; suf *= nums[i]; }\\n    return res;\\n}\\n'
        },
        'cpp': {
            'bullets': [
                'Compute prefix and suffix.',
            ],
            'pseudocode': 'vector<int> productExceptSelf(vector<int>& nums) {\\n    int n = nums.size();\\n    vector<int> res(n, 1);\\n    int pre = 1;\\n    for (int i = 0; i < n; i++) { res[i] = pre; pre *= nums[i]; }\\n    int suf = 1;\\n    for (int i = n-1; i >= 0; i--) { res[i] *= suf; suf *= nums[i]; }\\n    return res;\\n}\\n'
        },
    },
    'three_sum': {
        'python': {
            'bullets': [
                'Step 1: Sort the array first. This allows us to use two-pointer technique and easily skip duplicates.',
                'Step 2: Fix the first element at index i, then find two other elements that sum to -nums[i].',
                'Step 3: Use two pointers: left = i+1 (start) and right = len-1 (end).',
                'Step 4: Calculate sum = nums[i] + nums[left] + nums[right].',
                'Step 5: If sum == 0, we found a triplet! Add it to results and move both pointers.',
                'Step 6: If sum < 0, we need a larger sum, so move left pointer right (increase value).',
                'Step 7: If sum > 0, we need a smaller sum, so move right pointer left (decrease value).',
                'Step 8: CRITICAL: Skip duplicates! Skip same value at i, and after finding a triplet, skip duplicate left/right values.',
                'Step 9: Time: O(n²) because we have outer loop O(n) and inner two-pointer O(n).',
                'Example: [-1,0,1,2,-1,-4] → sorted:[-4,-1,-1,0,1,2] → triplets:[[-1,-1,2],[-1,0,1]]',
            ],
            'pseudocode': 'def three_sum(nums):\\n    # Step 1: Sort the array\\n    nums.sort()\\n    res = []\\n    \\n    # Step 2: Fix first element\\n    for i, x in enumerate(nums):\\n        # Skip duplicates for first element\\n        if i > 0 and nums[i] == nums[i-1]:\\n            continue\\n        \\n        # Step 3: Two pointers for remaining elements\\n        l, r = i+1, len(nums)-1\\n        \\n        while l < r:\\n            s = x + nums[l] + nums[r]\\n            \\n            if s == 0:\\n                # Found triplet!\\n                res.append([x, nums[l], nums[r]])\\n                l += 1\\n                r -= 1\\n                # Skip duplicate left values\\n                while l < r and nums[l] == nums[l-1]:\\n                    l += 1\\n                # Skip duplicate right values\\n                while l < r and nums[r] == nums[r+1]:\\n                    r -= 1\\n            elif s < 0:\\n                l += 1  # Need larger sum\\n            else:\\n                r -= 1  # Need smaller sum\\n    \\n    return res\\n'
        },
        'javascript': {
            'bullets': [
                'Sort and use two-pointer technique.',
            ],
            'pseudocode': 'function threeSum(nums) {\\n    nums.sort((a, b) => a - b);\\n    const res = [];\\n    for (let i = 0; i < nums.length; i++) {\\n        if (i && nums[i] == nums[i-1]) continue;\\n        let l = i+1, r = nums.length-1;\\n        while (l < r) {\\n            const s = nums[i] + nums[l] + nums[r];\\n            if (s == 0) {\\n                res.push([nums[i], nums[l], nums[r]]);\\n                l++; r--;\\n                while (l < r && nums[l] == nums[l-1]) l++;\\n                while (l < r && nums[r] == nums[r+1]) r--;\\n            } else if (s < 0) l++;\\n            else r--;\\n        }\\n    }\\n    return res;\\n}\\n'
        },
        'java': {
            'bullets': [
                'Sort and two-pointer approach.',
            ],
            'pseudocode': 'List<List<Integer>> threeSum(int[] nums) {\\n    Arrays.sort(nums);\\n    List<List<Integer>> res = new ArrayList<>();\\n    for (int i = 0; i < nums.length; i++) {\\n        if (i > 0 && nums[i] == nums[i-1]) continue;\\n        int l = i+1, r = nums.length-1;\\n        while (l < r) {\\n            int s = nums[i] + nums[l] + nums[r];\\n            if (s == 0) {\\n                res.add(Arrays.asList(nums[i], nums[l], nums[r]));\\n                l++; r--;\\n                while (l < r && nums[l] == nums[l-1]) l++;\\n                while (l < r && nums[r] == nums[r+1]) r--;\\n            } else if (s < 0) l++;\\n            else r--;\\n        }\\n    }\\n    return res;\\n}\\n'
        },
        'cpp': {
            'bullets': [
                'Sort and two-pointer approach.',
            ],
            'pseudocode': 'vector<vector<int>> threeSum(vector<int>& nums) {\\n    sort(nums.begin(), nums.end());\\n    vector<vector<int>> res;\\n    for (int i = 0; i < nums.size(); ++i) {\\n        if (i && nums[i] == nums[i-1]) continue;\\n        int l = i+1, r = nums.size()-1;\\n        while (l < r) {\\n            int s = nums[i] + nums[l] + nums[r];\\n            if (s == 0) {\\n                res.push_back({nums[i], nums[l], nums[r]});\\n                l++; r--;\\n                while (l < r && nums[l] == nums[l-1]) l++;\\n                while (l < r && nums[r] == nums[r+1]) r--;\\n            } else if (s < 0) l++;\\n            else r--;\\n        }\\n    }\\n    return res;\\n}\\n'
        },
    },
    'two_sum_sorted': {
        'bullets': [
            'Step 1: This is Two Sum II - the array is ALREADY SORTED, so we can use two pointers (no hashmap needed!).',
            'Step 2: Initialize left pointer at 0 (smallest element) and right pointer at len(nums)-1 (largest element).',
            'Step 3: Calculate sum = nums[left] + nums[right].',
            'Step 4: If sum == target, we found the pair! Return [left, right].',
            'Step 5: If sum < target, we need a larger sum. Move left pointer right (left += 1) to get a bigger number.',
            'Step 6: If sum > target, we need a smaller sum. Move right pointer left (right -= 1) to get a smaller number.',
            'Step 7: Continue until left >= right. If no pair found, return [-1, -1].',
            'Step 8: Time: O(n) because each pointer moves at most n times. Space: O(1) - just two pointers!',
            'Example: [2,7,11,15], target=9 → l=0,r=3: sum=17>9 → r=2: sum=13>9 → r=1: sum=9! → [0,1]',
        ],
        'pseudocode': 'def two_sum_sorted(nums, target):\\n    # Step 1: Initialize two pointers\\n    left, right = 0, len(nums) - 1\\n    \\n    # Step 2: Search while pointers haven\'t crossed\\n    while left < right:\\n        # Step 3: Calculate current sum\\n        s = nums[left] + nums[right]\\n        \\n        # Step 4: Check if found\\n        if s == target:\\n            return [left, right]\\n        \\n        # Step 5: Adjust pointers based on sum\\n        if s < target:\\n            left += 1  # Need larger sum\\n        else:\\n            right -= 1  # Need smaller sum\\n    \\n    # Step 6: No pair found\\n    return [-1, -1]\\n'
    },
    'longest_substring_without_repeating_characters': {
        'bullets': [
            'Step 1: Find the longest substring with all unique characters (no repeats). Example: "abcabcbb" → "abc" length 3.',
            'Step 2: Use sliding window technique with a hashmap to track the last seen position of each character.',
            'Step 3: Initialize: last={} (empty dict), left=0 (window start), best=0 (max length found).',
            'Step 4: Iterate through string with enumerate() to get both index i and character c.',
            'Step 5: If character c was seen before AND is in current window, move left pointer to exclude the duplicate.',
            'Step 6: Update left = max(left, last[c]+1). The max ensures left never moves backward.',
            'Step 7: Update last[c] = i to record the current position of character c.',
            'Step 8: Calculate current window length: i - left + 1. Update best = max(best, current length).',
            'Step 9: Time: O(n) single pass. Space: O(min(n, charset)) for the hashmap.',
            'Example: "abcabcbb" → i=3,c=\'a\': left=1 → i=4,c=\'b\': left=2 → i=5,c=\'c\': left=3 → best=3',
        ],
        'pseudocode': 'def longest_substring_without_repeating_characters(s):\\n    # Step 1: Initialize tracking variables\\n    last = {}  # Character to last seen index\\n    left = 0   # Window start\\n    best = 0   # Maximum length\\n    \\n    # Step 2: Process each character\\n    for i, c in enumerate(s):\\n        # Step 3: If duplicate found in window, shrink from left\\n        if c in last:\\n            left = max(left, last[c] + 1)\\n        \\n        # Step 4: Update last seen position\\n        last[c] = i\\n        \\n        # Step 5: Update maximum length\\n        best = max(best, i - left + 1)\\n    \\n    return best\\n'
    },
    'group_anagrams': {
        'bullets': [
            'Step 1: Anagrams are words with the same letters rearranged (e.g., "eat", "tea", "ate").',
            'Step 2: Key insight: Anagrams will have the same sorted letters. "eat"→"aet", "tea"→"aet", "ate"→"aet".',
            'Step 3: Use a dictionary (hashmap) to group words. The key is the sorted version of the word.',
            'Step 4: Import defaultdict(list) from collections to automatically create empty lists for new keys.',
            'Step 5: For each word, sort its characters with sorted(w), then join with "".join() to create the key.',
            'Step 6: Append the original word to the list at mp[key]. All anagrams will map to the same key.',
            'Step 7: Extract all the groups with mp.values(). Each group is a list of anagrams.',
            'Step 8: For deterministic output, sort each group internally and sort the groups themselves.',
            'Step 9: Time: O(n*k*log k) where n=number of words, k=max word length (for sorting each word).',
            'Example: ["eat","tea","tan","ate","nat","bat"] → groups: [["ate","eat","tea"], ["nat","tan"], ["bat"]]',
        ],
        'pseudocode': 'from collections import defaultdict\\n\\ndef group_anagrams(strs):\\n    # Step 1: Create hashmap with lists as default values\\n    mp = defaultdict(list)\\n    \\n    # Step 2: Process each word\\n    for w in strs:\\n        # Step 3: Create key by sorting characters\\n        key = "".join(sorted(w))\\n        \\n        # Step 4: Add word to its anagram group\\n        mp[key].append(w)\\n    \\n    # Step 5: Sort groups for deterministic output\\n    return [sorted(v) for v in sorted(mp.values(), key=lambda x: (len(x), x))]\\n'
    },
    'top_k_frequent': {
        'bullets': [
            'Step 1: Find the k most frequent elements in an array. If frequencies tie, sort lexicographically.',
            'Step 2: Import Counter from collections module - it counts element frequencies automatically.',
            'Step 3: Use Counter(nums) to get a dictionary of element→frequency mappings.',
            'Step 4: Convert to list of (element, frequency) tuples with counts.items().',
            'Step 5: Sort using a lambda function with tuple key: (-frequency, element).',
            'Step 6: Negative frequency ensures descending order (highest frequency first).',
            'Step 7: Element in tuple ensures lexicographical order for ties (ascending).',
            'Step 8: Use list comprehension to extract just the elements: [x for x,_ in items[:k]].',
            'Step 9: Time: O(n log n) for sorting. Could use heap for O(n log k) but sorting is simpler.',
            'Example: [1,1,1,2,2,3], k=2 → Counter:{1:3,2:2,3:1} → sorted:[(1,3),(2,2)] → [1,2]',
        ],
        'pseudocode': 'from collections import Counter\\n\\ndef top_k_frequent(nums, k):\\n    # Step 1: Count frequencies\\n    counts = Counter(nums)\\n    \\n    # Step 2: Sort by frequency (desc), then value (asc)\\n    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))\\n    \\n    # Step 3: Extract top k elements\\n    return [x for x, _ in items[:k]]\\n'
    },
    'kth_largest': {
        'bullets': ['Quickselect or heap; quickselect is average O(n).'],
        'pseudocode': '# quickselect partition around pivot to find index n-k\n'
    },
    'binary_search': {
        'bullets': [
            'Step 1: Binary search works ONLY on sorted arrays. It finds a target in O(log n) time by halving the search space.',
            'Step 2: Initialize two pointers: left=0 (start) and right=len(nums)-1 (end).',
            'Step 3: While left <= right (search space not empty), calculate middle index: mid = (left+right)//2.',
            'Step 4: Check nums[mid]. If it equals target, we found it! Return mid.',
            'Step 5: If nums[mid] < target, the target must be in the right half. Update left = mid+1.',
            'Step 6: If nums[mid] > target, the target must be in the left half. Update right = mid-1.',
            'Step 7: Repeat until left > right. If we exit the loop, target not found - return -1.',
            'Step 8: Why it works: Each comparison eliminates half the remaining elements.',
            'Example: [1,3,5,7,9], target=7 → mid=5(not match), 7>5 so left half → mid=7(match!) → return 3',
        ],
        'pseudocode': 'def binary_search(nums, target):\\n    # Step 1: Initialize pointers\\n    left, right = 0, len(nums) - 1\\n    \\n    # Step 2: Search while space exists\\n    while left <= right:\\n        # Step 3: Calculate middle\\n        mid = (left + right) // 2\\n        \\n        # Step 4: Check if found\\n        if nums[mid] == target:\\n            return mid\\n        \\n        # Step 5: Narrow search space\\n        if nums[mid] < target:\\n            left = mid + 1  # Search right half\\n        else:\\n            right = mid - 1  # Search left half\\n    \\n    # Step 6: Not found\\n    return -1\\n'
    },
    'search_rotated_sorted_array': {
        'bullets': ['One half is sorted at each step.', 'Check which half target lies in and adjust.'],
        'pseudocode': 'l,r=0,len(nums)-1\nwhile l<=r:\n  m=(l+r)//2\n  if nums[m]==target: return m\n  if nums[l]<=nums[m]:\n    if nums[l]<=target<nums[m]: r=m-1\n    else: l=m+1\n  else:\n    if nums[m]<target<=nums[r]: l=m+1\n    else: r=m-1\nreturn -1\n'
    },
    'max_product_subarray': {
        'bullets': ['Track both max and min due to negatives.', 'Swap when x<0.'],
        'pseudocode': 'best=hi=lo=nums[0]\nfor x in nums[1:]:\n  if x<0: hi,lo=lo,hi\n  hi=max(x, hi*x); lo=min(x, lo*x)\n  best=max(best, hi)\nreturn best\n'
    },
    'coin_change': {
        'bullets': ['Bottom-up DP: dp[a]=min(dp[a], dp[a-c]+1).', 'Initialize dp with inf and dp[0]=0.'],
        'pseudocode': 'dp=[10**9]*(amount+1); dp[0]=0\nfor c in coins:\n  for a in range(c, amount+1):\n    dp[a]=min(dp[a], dp[a-c]+1)\nreturn dp[amount] if dp[amount]<10**9 else -1\n'
    },
    'climb_stairs': {
        'python': {
            'bullets': ['Fibonacci: f(n)=f(n-1)+f(n-2).', 'Iterative O(1) space.'],
            'pseudocode': 'a,b=1,1\\nfor _ in range(n-1): a,b=b,a+b\\nreturn b if n>0 else 1\\n'
        },
        'javascript': {
            'bullets': ['Fibonacci: f(n)=f(n-1)+f(n-2).', 'Iterative O(1) space.'],
            'pseudocode': 'function climb_stairs(n) {\\n    let a=1,b=1; for (let i=0;i<n-1;i++){ [a,b]=[b,a+b]; } return n>0?b:1; }\\n'
        },
        'java': {
            'bullets': ['Fibonacci relation; iterative approach preferred to recursion.', 'Use int/long depending on n.'],
            'pseudocode': 'public int climb_stairs(int n) {\\n    int a=1,b=1; for (int i=0;i<n-1;i++){ int t=b; b=a+b; a=t; } return n>0?b:1; }\\n'
        },
        'cpp': {
            'bullets': ['Fibonacci relation; iterative approach preferred to recursion.', 'Use int/long depending on n.'],
            'pseudocode': 'int climb_stairs(int n) {\\n    int a=1,b=1; for (int i=0;i<n-1;i++){ int t=b; b=a+b; a=t; } return n>0?b:1; }\\n'
        },
    },
    'min_window_substring': {
        'bullets': ['Sliding window with need/have counts.', 'Expand right until valid, then shrink left.'],
        'pseudocode': '# Use Counter for t; track formed == required distinct chars.\n'
    },
    'longest_palindromic_substring': {
        'bullets': ['Expand-around-center for each i (odd and even).'],
        'pseudocode': 'def expand(l,r):\n  while l>=0 and r<len(s) and s[l]==s[r]: l-=1; r+=1\n  return l+1,r-1\n# track best window\n'
    },
    'rotate_matrix': {
        'bullets': ['Transpose then reverse each row (in-place) or build new using zip.'],
        'pseudocode': 'return [list(row)[::-1] for row in zip(*matrix)]\n'
    },
    'number_of_islands': {
        'python': {
            'bullets': ['Scan grid; when you see "1", DFS/BFS to mark all connected land to "0".', 'Use bounds checks and 4-direction neighbors.'],
            'pseudocode': 'def dfs(r,c):\\n  if out_of_bounds or grid[r][c]!="1": return\\n  grid[r][c]="0"\\n  for dr,dc in [(1,0),(-1,0),(0,1),(0,-1)]: dfs(r+dr,c+dc)\\ncount=0\\nfor r in range(R):\\n  for c in range(C):\\n    if grid[r][c]=="1": count+=1; dfs(r,c)\\nreturn count\\n'
        },
        'javascript': {
            'bullets': ['Scan grid; use DFS/BFS to mark visited cells.', 'Be careful with in-place modification vs copying.'],
            'pseudocode': 'function numIslands(grid) {\\n    const R=grid.length, C=grid[0].length; function dfs(r,c){ if(r<0||c<0||r>=R||c>=C||grid[r][c]==="0") return; grid[r][c]="0"; [[1,0],[-1,0],[0,1],[0,-1]].forEach(([dr,dc])=>dfs(r+dr,c+dc)); } let count=0; for(let r=0;r<R;r++) for(let c=0;c<C;c++) if(grid[r][c]==="1"){count++; dfs(r,c);} return count; }\\n'
        },
        'java': {
            'bullets': ['Scan grid; perform DFS/BFS using recursion or stack.', 'Mark visited cells to avoid recounting.'],
            'pseudocode': 'public int numIslands(char[][] grid) {\\n    int R=grid.length, C=grid[0].length; for(int r=0;r<R;r++) for(int c=0;c<C;c++) if(grid[r][c]==\'1\'){ dfs(grid,r,c); count++; } return count; }\\n'
        },
        'cpp': {
            'bullets': ['Use DFS/BFS and mark visited cells.', 'Watch recursion depth for large grids; consider iterative stack.'],
            'pseudocode': 'int numIslands(vector<vector<char>>& grid) {\\n    int R=grid.size(), C=grid[0].size(); function<void(int,int)> dfs = [&](int r,int c){ if(r<0||c<0||r>=R||c>=C||grid[r][c]==\'0\') return; grid[r][c]=\'0\'; dfs(r+1,c); dfs(r-1,c); dfs(r,c+1); dfs(r,c-1); }; int count=0; for(int r=0;r<R;r++) for(int c=0;c<C;c++) if(grid[r][c]==\'1\'){count++; dfs(r,c);} return count; }\\n'
        },
    },
}


def get_hints_for(problem_name: str, language: str) -> dict:
    """Return hints for a problem adapted to the requested language.
    HINTS entries may be either the old flat format ({'bullets':..., 'pseudocode':...})
    or a per-language mapping (e.g. {'python': {...}, 'java': {...}}).
    This helper returns a dict with keys 'bullets' and 'pseudocode'.
    """
    default = {'bullets': ['No hints available yet.'], 'pseudocode': ''}
    if problem_name not in HINTS:
        return default
    entry = HINTS[problem_name]
    # If entry already in new per-language shape
    if isinstance(entry, dict):
        # If it looks like a language-keyed mapping (contains language keys)
        if language in entry:
            return entry.get(language, default)
        # Backwards-compatible: if entry has 'bullets' treat it as legacy
        if 'bullets' in entry or 'pseudocode' in entry:
            return {
                'bullets': entry.get('bullets', default['bullets']),
                'pseudocode': entry.get('pseudocode', default['pseudocode'])
            }
        # If there's a 'default' key
        if 'default' in entry:
            return entry.get('default', default)
    return default

# Global glossary of common CS/algorithms terms
GLOSSARY = {
    'palindrome': """A string/sequence that reads the same forward and backward.
    - Normalization: often lowercase and strip non-alphanumerics.
    - Examples: "racecar", "A man, a plan, a canal: Panama" (ignoring spaces/punctuation).
    - Typical check: two pointers from ends or compare to reversed string.
    """,
    'two pointers': """Technique with two indices that move based on comparisons.
    - Patterns: opposite ends (palindrome), fast/slow (cycle), left/right window edges.
    - Why: reduces nested loops (O(n^2)) to linear (O(n)) for ordered/structured data.
    """,
    'hash map (dict)': """Key→value structure with average O(1) insert/lookup.
    - Python: dict; Common uses: Two Sum, frequency counts, last-seen indices.
    - Tip: Be careful with mutable keys; use tuples/strings as keys.
    """,
    'stack': """LIFO structure with push/pop in O(1).
    - Common in: balanced parentheses, DFS (iterative), undo operations.
    - Python: use list with append()/pop(), or collections.deque.
    """,
    'sliding window': """Maintain a window [l, r] and adjust by growing/shrinking.
    - Works best on arrays/strings to track counts/constraints (e.g., longest substring without repeats).
    - Tools: hash map for counts, a variable to track satisfaction of constraints.
    """,
    "Kadane's algorithm": """Linear-time algorithm for maximum subarray sum.
    - Idea: cur = max(x, cur+x); best = max(best, cur) as you scan.
    - Works because negative prefixes only hurt future sums.
    """,
    'binary search': """Search in sorted data by halving the interval each step.
    - Complexity: O(log n). Careful with mid calc and loop conditions.
    - Generalize to answer minimization/maximization via predicate (binary search on answer).
    """,
    'anagram': """Two strings with the same multiset of characters.
    - Checks: sort both strings or compare frequency counts.
    - Be mindful of unicode/case if required.
    """,
    'frequency count': """Counting occurrences of items.
    - Python: collections.Counter or dict with increment.
    - Used in: top-k frequent, anagrams, sliding window.
    """,
    'prefix/suffix product': """Cumulative products from left/right to compute product-except-self.
    - Avoids division and handles zeros gracefully.
    - Build prefix array, then multiply by running suffix on a backward pass.
    """,
    'heap': """Priority queue; Python's heapq is a min-heap.
    - Patterns: track top-k, merge k lists, Dijkstra.
    - For max-heap: push negatives or use nlargest.
    """,
    'quickselect': """Average O(n) selection for k-th smallest/largest using partition.
    - Uses a pivot to place elements < pivot to left and > pivot to right.
    - Recurse into the side containing the k-th index.
    """,
    'rotate matrix': """Rotate a matrix 90° clockwise.
    - Methods: transpose + reverse rows (in-place) or zip(*matrix) to build new.
    - In-place requires careful index swapping.
    """,
    'DFS': """Depth-First Search explores branches fully before backtracking.
    - Implement via recursion or an explicit stack.
    - Use to traverse graphs, flood-fill, topological sort (with visited).
    """,
    'BFS': """Breadth-First Search explores level by level using a queue.
    - Shortest path in unweighted graphs, level-order traversal of trees.
    - Python: collections.deque for efficient popleft().
    """,
    'island': """A connected component of '1's in a grid using 4-direction adjacency.
    - Count islands by scanning and flood-filling each discovered land cell.
    - Mark visited by turning to '0' or a visited set.
    """,
    'window': """The current inclusive range [l, r] for a sliding window algorithm.
    - Expand r to include more; shrink l to restore constraints.
    - Track when the window is "valid" to update best answers.
    """,
    'pivot': """A chosen value/index used to partition arrays in quicksort/quickselect.
    - Good pivots balance partitions; randomization reduces worst-case risk.
    """,
    'in-place': """Transforms data using O(1) extra space (ignoring recursion/stack).
    - Often modifies input arrays directly; beware of aliasing and iteration order.
    """,
    'lexicographical': """Lexicographical order is the dictionary order for strings or sequences.
    - Compares elements from left to right, just like words in a dictionary.
    - For example: 'apple' < 'banana' because 'a' < 'b'.
    - Used in sorting strings, permutations, and comparing arrays element-wise.
    """,
    'time complexity': """Asymptotic running time as input size grows.
    - Common: O(1), O(log n), O(n), O(n log n), O(n^2).
    - Prefer linear or n log n when feasible.
    """,
    'dynamic programming': """Optimize recursive problems by storing subproblem results.
    - Two styles: top-down (memoization) and bottom-up (tabulation).
    - Hallmarks: optimal substructure + overlapping subproblems.
    - Examples: coin change, climbing stairs, edit distance.
    """,
}

# Optional mapping of problems to relevant glossary terms
PROBLEM_TERMS = {
    'palindrome': ['palindrome', 'two pointers'],
    'two_sum': ['hash map (dict)'],
    'two_sum_sorted': ['two pointers', 'binary search'],
    'longest_substring_without_repeating_characters': ['sliding window', 'hash map (dict)', 'window'],
    'max_subarray': ["Kadane's algorithm"],
    'product_except_self': ['prefix/suffix product'],
    'group_anagrams': ['anagram', 'frequency count', 'hash map (dict)'],
    'top_k_frequent': ['frequency count', 'heap'],
    'kth_largest': ['quickselect', 'heap', 'pivot'],
    'binary_search': ['binary search'],
    'search_rotated_sorted_array': ['binary search', 'pivot'],
    'max_product_subarray': ['two pointers'],
    'coin_change': ['dynamic programming', 'time complexity'],
    'climb_stairs': ['dynamic programming', 'time complexity'],
    'min_window_substring': ['sliding window', 'window', 'hash map (dict)'],
    'longest_palindromic_substring': ['two pointers'],
    'rotate_matrix': ['rotate matrix', 'in-place'],
    'number_of_islands': ['DFS', 'BFS', 'island'],
    'merge_intervals': ['two pointers', 'time complexity'],
    'frequency_sort': ['frequency count'],
    'balanced_brackets': ['stack'],
}

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/problems', methods=['GET'])
def get_problems():
    """Return list of all problems."""
    return jsonify([{
        'name': p['name'],
        'title': p['title'],
        'description': p['description']
    } for p in PROBLEMS.values()])

@app.route('/api/problem/<name>', methods=['GET'])
def get_problem(name):
    """Return problem details including stub code."""
    if name not in PROBLEMS:
        return jsonify({'error': 'Problem not found'}), 404
    
    problem = PROBLEMS[name]
    language = request.args.get('language', 'python')
    
    # Get language-specific stub from problem definition
    if 'stubs' in problem and language in problem['stubs']:
        stub_code = problem['stubs'][language]
    else:
        # Fallback to Python file if stubs not defined
        stub_path = os.path.join('problems', f'{name}.py')
        try:
            with open(stub_path, 'r') as f:
                stub_code = f.read()
        except FileNotFoundError:
            stub_code = f"{problem.get('signature', '')}\n    # Write your code here\n    pass\n"
    
    return jsonify({
        'name': problem['name'],
        'title': problem['title'],
        'description': problem['description'],
        'signature': problem.get('signature', ''),
        'stub': stub_code,
        'language': language,
        'hints': get_hints_for(name, language),
        'terms': PROBLEM_TERMS.get(name, []),
        'tests': [{'args': str(t['args']), 'expected': str(t['expected'])} for t in problem['tests']]
    })

@app.route('/api/glossary', methods=['GET'])
def get_glossary():
    """Return the global glossary of terms."""
    return jsonify(GLOSSARY)

@app.route('/api/submit', methods=['POST'])
def submit_solution():
    """Execute user code against test cases and return results."""
    data = request.json
    if not data:
        return jsonify({'error': 'Invalid JSON data'}), 400
    
    problem_name = data.get('problem')
    code = data.get('code', '')
    language = data.get('language', 'python')
    
    if problem_name not in PROBLEMS:
        return jsonify({'error': 'Invalid problem'}), 400
    
    if language not in LANGUAGE_EXECUTORS:
        return jsonify({'error': f'Unsupported language: {language}'}), 400
    
    problem = PROBLEMS[problem_name]
    func_name = problem_name if problem_name != 'palindrome' else 'is_palindrome'
    
    results = []
    passed = 0
    failed = 0
    
    executor = LANGUAGE_EXECUTORS[language]
    
    # Run test cases
    for i, test in enumerate(problem['tests']):
        test_result = {
            'test_num': i + 1,
            'args': str(test['args']),
            'expected': str(test['expected']),
            'actual': None,
            'passed': False,
            'error': None
        }
        
        try:
            result, stdout, stderr = executor(code, test['args'], func_name)
            
            test_result['actual'] = str(result)
            test_result['stdout'] = stdout
            test_result['stderr'] = stderr
            
            if result == test['expected']:
                test_result['passed'] = True
                passed += 1
            else:
                failed += 1
        except Exception as e:
            test_result['error'] = f'{type(e).__name__}: {str(e)}'
            test_result['traceback'] = traceback.format_exc()
            failed += 1
        
        results.append(test_result)
    
    return jsonify({
        'passed': passed,
        'failed': failed,
        'total': len(problem['tests']),
        'results': results
    })

def _safe_repr(obj, max_len=200):
    try:
        s = repr(obj)
    except Exception as e:
        s = f'<unreprable {type(obj).__name__}: {e}>'
    if len(s) > max_len:
        s = s[:max_len] + '…'
    return s

@app.route('/api/debug', methods=['POST'])
def debug_solution():
    """Run user code with a simple tracer and return a recorded execution trace.
    Request JSON:
    {
        problem: str,
        code: str,
        testIndex?: int,           # optional: choose problem test cases
        customArgsJson?: str,      # optional: JSON array of args, e.g., ["abc", 2]
        breakpoints?: [int],       # optional: line numbers in user's code (1-based)
        maxSteps?: int             # optional: cap recorded steps (default 500)
    }
    """
    data = request.json or {}
    problem_name = data.get('problem')
    code = data.get('code', '')
    if problem_name not in PROBLEMS:
        return jsonify({'error': 'Invalid problem'}), 400

    problem = PROBLEMS[problem_name]
    func_name = problem_name if problem_name != 'palindrome' else 'is_palindrome'

    # Determine args
    args = None
    if 'testIndex' in data and isinstance(data['testIndex'], int):
        i = data['testIndex']
        try:
            args = problem['tests'][i]['args']
        except Exception:
            return jsonify({'error': 'Invalid testIndex'}), 400
    elif 'customArgsJson' in data and data['customArgsJson']:
        try:
            parsed = json.loads(data['customArgsJson'])
            if not isinstance(parsed, list):
                return jsonify({'error': 'customArgsJson must be a JSON array'}), 400
            args = tuple(parsed)
        except json.JSONDecodeError as e:
            return jsonify({'error': f'Invalid JSON for customArgsJson: {e}'}), 400
    else:
        # Default to first test case if available
        args = problem['tests'][0]['args'] if problem['tests'] else tuple()

    # Prepare tracing
    breakpoints = set(int(b) for b in data.get('breakpoints', []) if isinstance(b, int) or str(b).isdigit())
    max_steps = int(data.get('maxSteps', 500))
    code_lines = code.splitlines()
    trace = []
    truncated = False

    def tracer(frame, event, arg):
        nonlocal truncated
        # Only trace user code submitted via exec (filename will be '<string>')
        if frame.f_code.co_filename != '<string>':
            return tracer
        if event in ('call', 'line', 'return'):
            line_no = frame.f_lineno
            record_this = not breakpoints or (line_no in breakpoints)
            if record_this:
                try:
                    locals_snapshot = {k: _safe_repr(v) for k, v in frame.f_locals.items()}
                except Exception:
                    locals_snapshot = {}
                step = {
                    'event': event,
                    'line': line_no,
                    'code': code_lines[line_no-1] if 1 <= line_no <= len(code_lines) else '',
                    'locals': locals_snapshot,
                }
                if event == 'return':
                    step['return'] = _safe_repr(arg)
                trace.append(step)
                if len(trace) >= max_steps:
                    truncated = True
                    sys.settrace(None)
                    return None
        return tracer

    # Execute code with tracing
    namespace = {}
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()
    try:
        exec(code, namespace)
        if func_name not in namespace:
            return jsonify({'error': f'Function {func_name} not found in submitted code'}), 400

        user_func = namespace[func_name]
        sys.settrace(tracer)
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            retval = user_func(*args)
    except Exception as e:
        # Ensure tracing is disabled in case of error
        sys.settrace(None)
        return jsonify({
            'error': f'{type(e).__name__}: {e}',
            'trace': trace,
            'stdout': stdout_capture.getvalue(),
            'stderr': stderr_capture.getvalue(),
        })
    finally:
        sys.settrace(None)

    return jsonify({
        'trace': trace,
        'truncated': truncated,
        'stdout': stdout_capture.getvalue(),
        'stderr': stderr_capture.getvalue(),
        'return': _safe_repr(retval),
        'argsUsed': _safe_repr(args),
    })

@app.route('/api/ask', methods=['POST'])
def ask_ai():
    """Proxy a question to OpenAI with optional problem context.
    Request JSON:
    {
      prompt: str,
      problem?: str,
      includeDescription?: bool,
      includeCode?: bool,
      includeHints?: bool,
      includeTests?: bool,
      code?: str  # optional current editor code (if includeCode true)
    }
    """
    # Attempt to re-read .env safely before proceeding so changes are picked up at runtime.
    parsed_key, msg = reload_env_if_valid()
    if not parsed_key and not OPENAI_API_KEY:
        # If reload failed and we don't have a key yet, surface the validation message
        return jsonify({'error': f'Missing or invalid OPENAI_API_KEY: {msg}'}), 400
    # Prefer the parsed key if present, otherwise fall back to the previously loaded environment key
    effective_key = parsed_key if parsed_key else OPENAI_API_KEY

    data = request.json or {}
    user_prompt = (data.get('prompt') or '').strip()
    if not user_prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    problem_name = data.get('problem')
    language = data.get('language', 'python')
    include_description = bool(data.get('includeDescription'))
    include_code = bool(data.get('includeCode'))
    include_hints = bool(data.get('includeHints'))
    include_tests = bool(data.get('includeTests'))
    current_code = data.get('code') or ''

    # Add language context
    language_names = {
        'python': 'Python',
        'javascript': 'JavaScript',
        'java': 'Java',
        'cpp': 'C++'
    }
    lang_context = f"The user is working in {language_names.get(language, language)}."

    context_parts = [lang_context]
    if problem_name and problem_name in PROBLEMS:
        p = PROBLEMS[problem_name]
        title = p.get('title', problem_name)
        if include_description:
            context_parts.append(f"Problem: {title}\nDescription: {p.get('description','')}")
        if include_tests and p.get('tests'):
            tests_str = "\n".join([f"- args={t['args']} expected={t['expected']}" for t in p['tests']])
            context_parts.append(f"Sample tests:\n{tests_str}")
        if include_hints:
            h = get_hints_for(problem_name, language)
            bullets = "\n".join([f"• {b}" for b in h.get('bullets', [])])
            pseudo = h.get('pseudocode', '').strip()
            if bullets:
                context_parts.append(f"Hints:\n{bullets}")
            if pseudo:
                context_parts.append(f"Pseudocode:\n{pseudo}")
    if include_code and current_code:
        snippet = current_code.strip()
        if len(snippet) > 4000:
            snippet = snippet[:4000] + "\n# … truncated …"
        context_parts.append("Current code:\n" + snippet)

    full_user = user_prompt
    if context_parts:
        full_user += "\n\n---\nContext:\n" + "\n\n".join(context_parts)

    # Compose Chat Completions request
    language_tutor_names = {
        'python': 'Python',
        'javascript': 'JavaScript',
        'java': 'Java',
        'cpp': 'C++'
    }
    tutor_lang = language_tutor_names.get(language, 'programming')
    
    payload = {
        'model': OPENAI_MODEL,
        'messages': [
            {
                'role': 'system',
                'content': (
                    f'You are a concise, friendly {tutor_lang} algorithms tutor. '
                    'Explain step by step when helpful, and prefer clarity over verbosity. '
                    f'Use short {tutor_lang} code snippets only if explicitly asked or when crucial. '
                    f'Provide language-specific best practices and idioms for {tutor_lang}.'
                )
            },
            {'role': 'user', 'content': full_user}
        ],
        'temperature': 0.3,
        'max_tokens': 700,
    }

    req = urlrequest.Request(
        url='https://api.openai.com/v1/chat/completions',
        data=json.dumps(payload).encode('utf-8'),
        headers={
            'Authorization': f'Bearer {effective_key}',
            'Content-Type': 'application/json'
        },
        method='POST'
    )
    # Tolerate environments with strict SSL
    ctx = ssl.create_default_context()
    try:
        with urlrequest.urlopen(req, context=ctx, timeout=30) as resp:
            body = resp.read().decode('utf-8')
            data = json.loads(body)
            answer = data.get('choices', [{}])[0].get('message', {}).get('content', '').strip()
            if not answer:
                return jsonify({'error': 'Empty response from AI'}), 502
            return jsonify({'answer': answer})
    except HTTPError as e:
        try:
            err_body = e.read().decode('utf-8')
        except Exception:
            err_body = ''
        return jsonify({'error': f'HTTP {e.code}: {err_body or e.reason}'}), 502
    except URLError as e:
        return jsonify({'error': f'Network error: {e.reason}'}), 502
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {e}'}), 500


@app.route('/api/ask/status', methods=['GET'])
def ask_status():
    """Return whether the AI feature is enabled (OPENAI_API_KEY present)."""
    enabled = bool(OPENAI_API_KEY)
    msg = 'enabled' if enabled else 'missing OPENAI_API_KEY in environment/.env'
    return jsonify({'enabled': enabled, 'message': msg})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
