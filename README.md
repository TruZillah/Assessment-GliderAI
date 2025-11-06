<div align="center">

# 💎 Multi-Language Assessment Practice

### _Master coding interviews with an interactive, feature-rich practice environment_

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)

[Features](#-features) • [Screenshots](#-screenshots) • [Quick Start](#-quick-start) • [Problems](#-problem-library) • [Tech Stack](#-tech-stack)

</div>

---

## ✨ Overview

A comprehensive **practice assessment platform** designed to mirror real-world coding interviews (JPMC/Glider-style). Features a beautiful modern UI with integrated learning tools, time tracking, AI assistance, and instant code testing across multiple programming languages.

Perfect for interview prep, algorithm practice, and developing systematic problem-solving skills.

---

## 🎯 Features

### 🔥 Core Functionality
- **24 Curated Problems** — Easy to Hard difficulty spanning essential algorithms and data structures
- **Multi-Language Support** — Write solutions in Python, JavaScript, Java, C++, and more
- **Instant Testing** — Run test cases with immediate feedback and detailed results
- **Code Editor** — Syntax highlighting, line numbers, and auto-indentation
- **Test Debugger** — Set breakpoints, step through code, inspect custom test cases

### 📚 Learning Tools
- **🎓 Problem-Solving Lecture** — UMPIRE framework and systematic thinking methodology
- **📖 Language Cheat Sheets** — Quick reference guides for Python, JavaScript, Java, C++, Rust
- **💡 Enhanced Hints** — Step-by-step breakdowns with traced examples and complexity analysis
- **📝 Problem-Solving Notepad** — Structured template for the UMPIRE method
- **🔍 Glossary** — Searchable definitions for algorithm terms and patterns
- **🤖 AI Assistant** — Context-aware help with your code and problem descriptions

### ⏱️ Progress Tracking
- **Session Timer** — Track time spent per problem
- **History Dashboard** — View all attempts with timestamps and duration
- **Statistics** — Total time, problems solved, average time per problem
- **Persistent State** — LocalStorage saves your code, preferences, and progress

### 🎨 Modern UI/UX
- **Gradient Design** — Beautiful blue-to-purple gradient with glassmorphism effects
- **Collapsible Sections** — Expandable notepad, cheat sheets, lecture, hints, and debugger
- **Responsive Layout** — Optimized for desktop and laptop screens
- **Dark Theme** — Eye-friendly code editor with syntax highlighting
- **Interactive Tour** — 10-step guided walkthrough for new users
- **Keyboard Shortcuts** — Ctrl+Enter to run tests, quick navigation

---

## 📸 Screenshots

<div align="center">

### 🖥️ Main Dashboard
![Dashboard](docs/screenshots/dashboard.png)
*Problem list with difficulty badges, timer, and statistics*

### ⌨️ Code Editor & Tools
![Editor](docs/screenshots/editor.png)
*Integrated code editor with debugger, hints, and AI assistant*

### 🎓 Learning Resources
![Learning Tools](docs/screenshots/tools.png)
*Lecture section, cheat sheets, notepad, and glossary in action*

### 📋 Problem Selection & Interface
![Problem Interface](docs/screenshots/Screenshot%202025-11-05%20092913.png)
*Clean problem selection interface with sidebar navigation*

### 💡 Hints & Guidance System
![Hints System](docs/screenshots/Screenshot%202025-11-05%20093648.png)
*Step-by-step hints with complexity analysis and examples*

### 🧪 Test Results & Debugging
![Test Results](docs/screenshots/Screenshot%202025-11-06%20004724.png)
*Detailed test case results with pass/fail indicators*

### 🔍 Code Debugging Features
![Debugger](docs/screenshots/Screenshot%202025-11-06%20004819.png)
*Interactive debugger with breakpoints and variable inspection*

### 📚 Language Cheat Sheets
![Cheat Sheets](docs/screenshots/Screenshot%202025-11-06%20004843.png)
*Quick reference guides for multiple programming languages*

### 🎓 UMPIRE Framework Lecture
![Lecture](docs/screenshots/Screenshot%202025-11-06%20004912.png)
*Comprehensive problem-solving methodology and best practices*

### 📝 Problem-Solving Notepad
![Notepad](docs/screenshots/Screenshot%202025-11-06%20005027.png)
*Structured notepad for applying the UMPIRE method*

### 🔤 Algorithm Glossary
![Glossary](docs/screenshots/Screenshot%202025-11-06%20005126.png)
*Searchable glossary of common algorithms and data structures*

</div>

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Flask 3.0+
- Modern web browser (Chrome, Firefox, Edge)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/TruZillah/Assessment-GliderAI.git
   cd Assessment-GliderAI
   ```

2. **Install dependencies**
   ```bash
   pip install flask
   ```

3. **Start the Flask server**
   ```bash
   python app.py
   # or on WSL:
   wsl python3 app.py
   ```

4. **Open in browser**
   ```
   http://127.0.0.1:5000
   ```

5. **Start practicing!** 🎉
   - Select a problem from the sidebar
   - Write your solution in the code editor
   - Click "Run Tests" or press Ctrl+Enter
   - Use hints, cheat sheets, and the lecture for guidance

### AI Assistant — OpenAI configuration

This project includes an optional AI assistant that uses the OpenAI API. The app loads a `.env` file at startup (and a small loader will also pick up valid keys and set them in the environment). To enable the assistant you need to provide a valid OpenAI API key.

How to get an OpenAI API key (for beginners)

1. Create an OpenAI account

   - Open your browser and go to the sign-up page: [platform.openai.com/signup](https://platform.openai.com/signup). Follow the sign-up and email verification steps.

2. Visit the API keys page

   - After signing in, open the API keys page: [platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys). This is where you create and manage secret API keys.

3. Create a new secret key

   - Click **Create new secret key** (or similar). Copy the key immediately and store it somewhere safe — you won't be able to view the full key again from the dashboard.

4. Billing and model access

   - New accounts may need to add a payment method to use paid models (for example, gpt-4). OpenAI sometimes provides free trial credits for new users; check the dashboard for any available credits.
   - If you don't have access to gpt-4 via the API, use `gpt-3.5-turbo` as the `OPENAI_MODEL` value (it is lower-cost and widely available).

5. Important security notes

   - Treat API keys like passwords. Do not share them, paste them in public forums, or commit them to git. The repo already excludes `.env` in `.gitignore`.
   - If a key is leaked, revoke it immediately from the OpenAI dashboard and create a new one.

Note: the ChatGPT web UI (chat.openai.com) does not provide an API key you can use here — you must create an API key on the OpenAI platform.

Where to put the key

- Create a file named `.env` in the project root (the same folder as `app.py`). The repository already ignores `.env` in `.gitignore` so your key won't be accidentally committed.

Example `.env` content

```text
OPENAI_API_KEY=sk-<your-secret-key-here>
# Optional: switch model (default: gpt-4)
OPENAI_MODEL=gpt-4
```

Windows (cmd.exe) quick options

- Create the file using Notepad (recommended to avoid shell quoting issues):

```cmd
notepad .env
# paste the OPENAI_API_KEY line and save
```

- Or set it temporarily in the current shell (effective until you close the terminal):

```cmd
set OPENAI_API_KEY=sk-<your-secret-key-here>
python app.py
```

PowerShell (optional)

```powershell
$env:OPENAI_API_KEY = 'sk-<your-secret-key-here>'
python app.py
```

Important notes

- To pick up changes in `.env` you must restart the Flask server — the app reads `.env` on startup. The repository includes a small loader and validator in `app.py` that checks for a key starting with `sk-` and will load `OPENAI_API_KEY` if valid.
- Keep your API key secret. Do not paste it into public places or share it in commits. The repo already contains `.gitignore` with `.env` listed.
- If you don't set a key the UI will show the AI controls disabled and the app will continue to work for running problems and tests without the assistant.

Verify it's loaded

- In cmd:

```cmd
echo %OPENAI_API_KEY%
```

- In PowerShell:

```powershell
echo $env:OPENAI_API_KEY
```

### 🎛️ Admin Settings Panel (New!)

The app now includes a web-based admin panel for easy configuration without editing files.

Access the admin panel

1. Start the Flask server as usual
2. Open your browser and navigate to: `http://127.0.0.1:5000/admin.html`
3. Login with your admin password (default: `admin123`)

Features

- ✅ Add/update OpenAI API key through the web interface
- ✅ Test API key validity before saving
- ✅ Switch between different OpenAI models (GPT-4, GPT-3.5-Turbo, etc.)
- ✅ View current configuration status
- ✅ Automatic persistence to `.env` file
- 🔒 Password-protected access

Security notes

- **Change the default admin password!** Set `ADMIN_PASSWORD` environment variable or in `.env`:
  ```text
  ADMIN_PASSWORD=your-secure-password-here
  ```
- The admin panel is password-protected but does not use HTTPS by default. For production, always use HTTPS (see deployment section below).
- Admin password is stored in environment variables, not in the database.

Alternative: Command line testing

Run all tests without the web interface:

```bash
python run_tests.py
```

---

## 🚀 Production Deployment

### Quick Start with Docker (Recommended)

The easiest way to deploy for production is using Docker Compose:

1. **Copy environment template**
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY and ADMIN_PASSWORD
   ```

2. **Build and run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - App: `http://localhost:8000`
   - Admin Panel: `http://localhost:8000/admin.html`
   - With Nginx (if enabled): `http://localhost`

4. **View logs**
   ```bash
   docker-compose logs -f app
   ```

5. **Stop the application**
   ```bash
   docker-compose down
   ```

### Docker (without Compose)

1. **Build the Docker image**
   ```bash
   docker build -t assessment-gliderai .
   ```

2. **Run the container**
   ```bash
   docker run -d \
     --name assessment-app \
     -p 8000:8000 \
     -e OPENAI_API_KEY=sk-your-key-here \
     -e ADMIN_PASSWORD=your-secure-password \
     -v $(pwd)/.env:/app/.env \
     assessment-gliderai
   ```

3. **Check container status**
   ```bash
   docker ps
   docker logs assessment-app
   ```

### Linux/WSL with systemd

For Linux servers or WSL, use systemd for process management:

1. **Install dependencies**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create log directory**
   ```bash
   sudo mkdir -p /var/log/assessment
   sudo chown $USER:$USER /var/log/assessment
   ```

3. **Copy and edit the service file**
   ```bash
   sudo cp assessment.service /etc/systemd/system/
   sudo nano /etc/systemd/system/assessment.service
   # Update paths and environment variables
   ```

4. **Enable and start the service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable assessment
   sudo systemctl start assessment
   sudo systemctl status assessment
   ```

5. **View logs**
   ```bash
   sudo journalctl -u assessment -f
   ```

### Windows with Waitress

For Windows production deployments:

1. **Install Waitress**
   ```cmd
   pip install -r requirements.txt
   ```

2. **Create a start script** (`start-production.bat`)
   ```batch
   @echo off
   set OPENAI_API_KEY=sk-your-key-here
   set ADMIN_PASSWORD=your-secure-password
   set FLASK_ENV=production
   waitress-serve --listen=*:8000 app:app
   ```

3. **Run the server**
   ```cmd
   start-production.bat
   ```

4. **Optional: Install as Windows Service using NSSM**
   ```cmd
   # Download NSSM from https://nssm.cc/download
   nssm install AssessmentApp "C:\Python\python.exe" "-m waitress --listen=*:8000 app:app"
   nssm set AssessmentApp AppDirectory "C:\path\to\Assessment-GliderAI"
   nssm set AssessmentApp AppEnvironmentExtra OPENAI_API_KEY=sk-xxx ADMIN_PASSWORD=xxx
   nssm start AssessmentApp
   ```

### Nginx Reverse Proxy (Optional but Recommended)

For production with SSL/TLS:

1. **Install Nginx**
   ```bash
   sudo apt install nginx  # Ubuntu/Debian
   sudo yum install nginx  # RHEL/CentOS
   ```

2. **Copy nginx configuration**
   ```bash
   sudo cp nginx.conf /etc/nginx/sites-available/assessment
   sudo ln -s /etc/nginx/sites-available/assessment /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **Setup SSL with Let's Encrypt**
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d your-domain.com
   ```

### Environment Variables for Production

Required environment variables:

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | - | No (but needed for AI features) |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4` | No |
| `ADMIN_PASSWORD` | Admin panel password | `admin123` | **Yes (change in production!)** |
| `FLASK_ENV` | Flask environment | `development` | No |

### Production Checklist

Before deploying to production:

- [ ] Change `ADMIN_PASSWORD` from default
- [ ] Set `OPENAI_API_KEY` via environment variables or admin panel
- [ ] Use a production WSGI server (Waitress, Gunicorn, or Docker)
- [ ] Enable HTTPS/SSL via Nginx or cloud load balancer
- [ ] Set `FLASK_ENV=production`
- [ ] Configure proper logging and log rotation
- [ ] Set up monitoring and health checks
- [ ] Backup `.env` file securely (contains API keys)
- [ ] Configure firewall to allow only necessary ports
- [ ] Set up automated backups if storing user data

### Cloud Deployment

**AWS (Elastic Beanstalk)**
```bash
# Initialize EB
eb init -p docker assessment-gliderai

# Create environment
eb create production-env

# Set environment variables
eb setenv OPENAI_API_KEY=sk-xxx ADMIN_PASSWORD=xxx

# Deploy
eb deploy
```

**Heroku**
```bash
# Create app
heroku create assessment-gliderai

# Set environment variables
heroku config:set OPENAI_API_KEY=sk-xxx
heroku config:set ADMIN_PASSWORD=xxx

# Deploy
git push heroku main
```

**DigitalOcean App Platform**
- Upload repo to GitHub
- Connect to DigitalOcean App Platform
- Set environment variables in the dashboard
- Deploy automatically from git

---

## 📚 Problem Library

### 🟢 Easy (8 problems)
| Problem | Description | Key Concepts |
|---------|-------------|--------------|
| **Sum of Two Integers** | Return the sum of two integers | Basic arithmetic |
| **Is Palindrome** | Check if string is palindrome (ignore case/non-alphanumeric) | Two pointers, string manipulation |
| **Second Largest** | Find second largest distinct value | Array traversal, duplicates |
| **Two Sum** | Find indices of two numbers that sum to target | Hash map, complement search |
| **Balanced Brackets** | Validate balanced parentheses/brackets | Stack, matching pairs |
| **Climbing Stairs** | Count ways to climb n stairs (1 or 2 steps) | Dynamic programming, Fibonacci |
| **Binary Search** | Search for target in sorted array | Divide and conquer, binary search |
| **Two Sum II (Sorted)** | Two sum variant on sorted array | Two pointers on sorted data |

### 🟡 Medium (10 problems)
| Problem | Description | Key Concepts |
|---------|-------------|--------------|
| **Frequency Sort** | Sort characters by frequency, then lexicographically | Hash map, custom sorting, Counter |
| **Merge Intervals** | Merge overlapping intervals | Sorting, interval merging |
| **Maximum Subarray Sum** | Find max sum of contiguous subarray | Kadane's algorithm, DP |
| **Product Except Self** | Array of products excluding self (no division) | Prefix/suffix products |
| **3Sum** | Find all unique triplets summing to zero | Sorting, two pointers, duplicates |
| **Longest Substring w/o Repeats** | Longest substring with unique characters | Sliding window, hash set |
| **Group Anagrams** | Group words that are anagrams | Hash map with sorted keys |
| **Top K Frequent Elements** | Find k most frequent elements | Counter, heap, bucket sort |
| **Kth Largest Element** | Find kth largest in array | Quick select, heap |
| **Search in Rotated Array** | Binary search in rotated sorted array | Modified binary search |

### 🔴 Hard (6 problems)
| Problem | Description | Key Concepts |
|---------|-------------|--------------|
| **Coin Change (Min Coins)** | Minimum coins to make amount | Dynamic programming, BFS |
| **Minimum Window Substring** | Smallest window containing all target chars | Sliding window, two pointers |
| **Longest Palindromic Substring** | Find longest palindromic substring | Expand around center, DP |
| **Maximum Product Subarray** | Max product of contiguous subarray | DP with min/max tracking |
| **Rotate Matrix 90°** | Rotate n×n matrix in-place | Matrix transposition, reflection |
| **Number of Islands** | Count islands in 2D grid | DFS, BFS, union-find |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Flask** | Python web framework for backend API |
| **JavaScript** | Interactive UI, code editor, state management |
| **HTML/CSS** | Modern gradient UI with glassmorphism |
| **LocalStorage** | Persistent client-side data storage |
| **CodeMirror-style Editor** | Syntax highlighting and code editing |

---

## 🎯 Use Cases

- ✅ **Interview Preparation** — Practice problems similar to JPMC, Google, Amazon interviews
- ✅ **Algorithm Learning** — Systematic approach with UMPIRE framework
- ✅ **Coding Bootcamps** — Teaching resource with built-in learning tools
- ✅ **Personal Skill Development** — Track progress and improve problem-solving
- ✅ **Mock Assessments** — Timed practice sessions with statistics

---

## 📖 Documentation

- [FEATURES.md](FEATURES.md) — Complete feature list and detailed descriptions
- [MULTI_LANGUAGE.md](MULTI_LANGUAGE.md) — Multi-language support documentation
- [CONTRIBUTING.md](CONTRIBUTING.md) — Contribution guidelines (coming soon)

---

## 🤝 Contributing

Contributions are welcome! Whether it's bug reports, feature requests, or new problem submissions:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

**Built with ❤️ for developers preparing for coding interviews**

[⬆ Back to Top](#-multi-language-assessment-practice)

</div>
