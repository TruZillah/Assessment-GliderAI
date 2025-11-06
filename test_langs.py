#!/usr/bin/env python3
"""Quick test to verify language executors work"""

import sys

sys.path.insert(0, '.')

from app import execute_cpp, execute_java, execute_javascript, execute_python

print("Testing Python executor...")
py_code = """
def summation(a, b):
    return a + b
"""
result, stdout, stderr = execute_python(py_code, 'summation', (2, 3))
print(f"Python result: {result} (expected 5)")
assert result == 5, f"Python test failed: {result}"
print("✓ Python works!\n")

print("Testing JavaScript executor...")
js_code = """
function summation(a, b) {
    return a + b;
}
"""
try:
    result, stdout, stderr = execute_javascript(js_code, 'summation', (2, 3))
    print(f"JavaScript result: {result} (expected 5)")
    assert result == 5, f"JavaScript test failed: {result}"
    print("✓ JavaScript works!\n")
except Exception as e:
    print(f"⚠ JavaScript test failed: {e}\n")

print("Testing Java executor...")
java_code = """
public class Solution {
    public int summation(int a, int b) {
        return a + b;
    }
}
"""
try:
    result, stdout, stderr = execute_java(java_code, 'summation', (2, 3))
    print(f"Java result: {result} (expected 5)")
    # Java might return string "5"
    assert str(result) == "5" or result == 5, f"Java test failed: {result}"
    print("✓ Java works!\n")
except Exception as e:
    print(f"⚠ Java test failed: {e}\n")

print("Testing C++ executor...")
cpp_code = """
int summation(int a, int b) {
    return a + b;
}
"""
try:
    result, stdout, stderr = execute_cpp(cpp_code, 'summation', (2, 3))
    print(f"C++ result: {result} (expected 5)")
    assert result == 5, f"C++ test failed: {result}"
    print("✓ C++ works!\n")
except Exception as e:
    print(f"⚠ C++ test failed: {e}\n")

print("All basic tests completed!")
print("All basic tests completed!")
