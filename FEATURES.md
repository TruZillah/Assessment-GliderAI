# Practice Assessment Features

## New Enhancements ✨

### 1. Copy Pseudocode Button 📋
- **Location**: Inside the Hints section, next to "Pseudocode"
- **Function**: One-click copy of pseudocode to clipboard
- **Feedback**: Button changes to "✓ Copied!" for 2 seconds
- **Fallback**: Works even in older browsers with execCommand fallback

### 2. Difficulty Badges 🎯
Each problem now displays a color-coded difficulty badge:
- **Easy** (Green): `summation`, `palindrome`, `second_largest`, `two_sum`, `balanced_brackets`, `binary_search`, `climb_stairs`
- **Medium** (Yellow): Most algorithmic problems requiring DS knowledge
- **Hard** (Red): `three_sum`, `min_window_substring`, `longest_palindromic_substring`, `number_of_islands`, `coin_change`, `product_except_self`

### 3. Problem Timer ⏱️
- **Location**: Top right of problem title
- **Function**: Tracks time spent on current problem
- **Format**: MM:SS
- **Reset**: Automatically resets when switching problems

### 4. Hint Visibility Memory 💾
- **Function**: Remembers if you had hints open/closed per problem
- **Behavior**: When you return to a problem, hints state is preserved
- **Scope**: Session-based (resets on page reload)

### 5. Keyboard Shortcuts ⌨️
- **Ctrl+Enter** (or **Cmd+Enter** on Mac): Run tests
- **Tab** in editor: Insert 4 spaces (proper Python indentation)

### 6. Enhanced UI/UX
- **Icons**: Added emojis for better visual clarity
  - ▶ Run Tests
  - ↺ Reset Code
  - 💡 Hints
  - 📋 Copy
  - ⏱️ Timer
- **Hover effects**: Copy button has visual feedback
- **Color transitions**: Smooth state changes

## Usage Tips 💡

### For Quick Practice
1. Click a problem (starts timer)
2. Read description and test cases
3. Code your solution
4. Press **Ctrl+Enter** to run tests
5. Check results and iterate

### When You Need Help
1. Click "Show hints" in the Hints section
2. Review bullet-point tips
3. If needed, read the pseudocode
4. Click **📋 Copy** to copy pseudocode
5. Adapt pseudocode to your solution
6. Click "Hide hints" to test yourself

### To Track Progress
- Use difficulty badges to pick appropriate challenges
- Watch the timer to practice time management
- Start with Easy problems to warm up
- Progress to Medium/Hard as you improve

## Browser Compatibility ✅
- Modern browsers: Uses Clipboard API
- Older browsers: Falls back to execCommand
- All features work in Edge, Chrome, Firefox, Safari

## Coming Soon 🚀
- Progress tracking (problems solved per difficulty)
- Code snippets library
- Export solutions to files
- Dark mode toggle
- Performance metrics

---

**Pro Tip**: Use Ctrl+Enter frequently to test incrementally. Don't wait until your solution is "perfect"!
