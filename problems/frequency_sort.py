"""
Problem 4: frequency_sort(s) -> str
Return a string with characters sorted by frequency (descending), then by character (ascending).

Examples:
- frequency_sort("tree") -> "eert" or "eetr" (e twice, then r and t)
- frequency_sort("cccaaa") -> "aaaccc" or "cccaaa" (both valid depending on tie-break)

Tie-break rule for this practice:
- Primary: higher frequency first
- Secondary: lexicographically smaller character first
"""

# TODO: Implement the function below.

def frequency_sort(s):
    """Sort characters by frequency desc, then by char asc."""
    # Write your code here
    raise NotImplementedError("Use a Counter and sorted with custom key")
