# Multi-Language Assessment Platform

## 🚀 New Features

### Multi-Language Support
The platform now supports **4 programming languages**:
- **Python 🐍** - Original language with full debugging support
- **JavaScript 📜** - Runs via Node.js  
- **Java ☕** - Compiles with javac, runs with java
- **C++ ⚡** - Compiles with g++ (C++17 standard)

### How It Works

#### Language Selector
- Located in the top-right corner of the header
- Selection persists across sessions via localStorage
- Automatically loads appropriate code stubs when switching languages
- Updates editor placeholder text to match selected language

#### Language-Specific Code Execution
Each language has a dedicated executor:

**Python**: Uses `exec()` in isolated namespace
**JavaScript**: Creates temp .js file, executes with Node.js
**Java**: Creates temp directory, compiles with javac, runs with java
**C++**: Creates temp directory, compiles with g++ -std=c++17, runs executable

All executors:
- ✅ Capture stdout/stderr
- ✅ Support timeouts (5-10 seconds)
- ✅ Return structured results with test outcomes
- ✅ Handle compilation/runtime errors gracefully

#### Multi-Language Problem Stubs
Problems now include language-specific starter code:

```python
# Python
def summation(a, b):
    # Write your code here
    pass
```

```javascript
// JavaScript
function summation(a, b) {
    // Write your code here
}
```

```java
// Java
public class Solution {
    public int summation(int a, int b) {
        // Write your code here
        return 0;
    }
}
```

```cpp
// C++
int summation(int a, int b) {
    // Write your code here
    return 0;
}
```

#### AI Assistant Language Awareness
The AI Assistant now:
- Knows which language you're using
- Provides language-specific best practices
- Uses appropriate syntax in code examples
- Adapts explanations to language idioms

Example: When using Java, the AI will suggest using `HashMap` instead of Python's `dict`.

### Requirements

Make sure you have the required tools installed in WSL:

```bash
# Check Python
python3 --version  # Should be 3.10+

# Check Node.js
node --version     # Should be v14+

# Check Java
javac -version     # Should be 11+
java -version

# Check C++
g++ --version      # Should support C++17
```

If missing, install with:
```bash
# Node.js
sudo apt update
sudo apt install nodejs npm

# Java
sudo apt install default-jdk

# C++
sudo apt install build-essential
```

### Testing

Run `test_langs.py` to verify all language executors work:

```bash
wsl python3 test_langs.py
```

Expected output:
```
✓ Python works!
✓ JavaScript works!
✓ Java works!
✓ C++ works!
```

### Current Coverage

**Full multi-language support (all 4 languages):**
- `summation` - Basic addition
- `palindrome` - String validation
- `two_sum` - Array/hash table problem

**Python-only (21 problems):**
- All other problems default to Python stubs
- Can still be solved in other languages by manually writing appropriate signatures
- Future expansion: add language-specific stubs for more problems

### Known Limitations

1. **Debugger**: Only works for Python (uses `sys.settrace`)
   - Gracefully disabled or shows error for other languages
   - Future: Could add basic stdout-based tracing for other languages

2. **Type Conversion**: Some test assertions may be strict
   - Java may return String "5" vs integer 5
   - C++ may have float vs int precision issues
   - Backend attempts smart comparison

3. **Complex Data Structures**: 
   - Arrays work well across all languages
   - Nested structures (2D arrays, objects) need careful JSON serialization
   - Currently optimized for simple algorithm problems

### Future Enhancements

- [ ] Add Go, Rust, TypeScript support
- [ ] Expand multi-language stubs to all 24 problems
- [ ] Add language-specific test format variations
- [ ] Implement basic debugger for non-Python languages
- [ ] Add code formatter integration (black, prettier, clang-format)
- [ ] Language-specific performance metrics

### Architecture Notes

**Backend** (`app.py`):
- `execute_python()` - Direct exec() in namespace
- `execute_javascript()` - Subprocess with temp file
- `execute_java()` - javac compile + java run in temp dir
- `execute_cpp()` - g++ compile + execute in temp dir
- `LANGUAGE_EXECUTORS` dict maps language → executor function

**Frontend** (`static/index.html`):
- `currentLanguage` - Tracks selected language
- Language selector dropdown with emoji flags
- Auto-updates editor placeholder on language change
- Passes `language` param to all API calls

**API Changes**:
- `GET /api/problem/<name>?language=<lang>` - Returns language-specific stub
- `POST /api/submit` - Accepts `language` field in JSON
- `POST /api/ask` - Accepts `language` field for AI context

### Testing Checklist

- [x] Python execution works
- [x] JavaScript execution works  
- [x] Java execution works (fixed public class issue)
- [x] C++ execution works
- [x] Language selector persists selection
- [x] Stubs load correctly per language
- [x] AI Assistant adapts to language
- [x] Submit endpoint routes to correct executor
- [ ] Full integration test with browser UI
- [ ] Test all 3 multi-language problems end-to-end

---

**Status**: ✅ Core multi-language infrastructure complete and tested
**Next Steps**: Open browser, test language switching, verify all features work correctly
