# 🚀 AI Coder System - Complete Usage Guide

Let me show you exactly how to use this AI Coder system with step-by-step examples and tests!

## 📋 Quick Setup

1. **Save the code** as `main.py` in any folder
2. **Open terminal/command prompt** in that folder
3. **Run the system**

## 🎯 Testing Methods

### **Method 1: Interactive Mode (Recommended for beginners)**

```bash
python main.py
```

You'll see:
```
🤖 AI Coder System - Interactive Mode
==================================================
Commands:
  create <name> <type> - Create project
  advanced <name> <features> - Create advanced project
  write <project> <filename> <type> - Write code file
  execute <code> - Execute Python code
  run <project> - Run project
  list - List projects
  info <project> - Get project info
  exit - Quit
--------------------------------------------------

🔧 AI Coder>
```

### **Method 2: Command Line (Quick operations)**

```bash
# Create projects directly
python main.py create myapp python_app
python main.py run myapp
python main.py list
```

## 🧪 Step-by-Step Testing

### **Test 1: Create Your First Project**

**Interactive Mode:**
```bash
python main.py
🔧 AI Coder> create hello python_app "My first AI-generated app"
```

**Command Line:**
```bash
python main.py create hello python_app "My first AI-generated app"
```

**Expected Output:**
```
Project hello created successfully at /path/to/your/folder/projects/hello
```

**What it creates:**
```
projects/hello/
├── main.py           # Ready-to-run Python app
├── config.py         # Configuration file
├── requirements.txt  # Dependencies
├── README.md         # Documentation
├── src/              # Source directory
└── tests/           # Test directory
```

### **Test 2: Run the Generated Project**

```bash
🔧 AI Coder> run hello
```

**Expected Output:**
```
Project executed successfully:
Hello, World!
```

### **Test 3: Create Different Project Types**

```bash
# Web Application
🔧 AI Coder> create webapp web_app "Interactive web application"

# API Server
🔧 AI Coder> create api api_project "REST API server"

# Data Science Project
🔧 AI Coder> create analyzer data_science "Data analysis tool"
```

### **Test 4: Execute Code Directly**

```bash
🔧 AI Coder> execute print("Hello from AI Coder!")
```

**Expected Output:**
```
Execution successful:
Hello from AI Coder!
```

**Try more complex code:**
```bash
🔧 AI Coder> execute
Enter Python code: 
import math
for i in range(5):
    print(f"Square root of {i}: {math.sqrt(i) if i > 0 else 0}")
```

### **Test 5: Advanced Project with Features**

```bash
🔧 AI Coder> advanced scraper web_scraping,data_analysis "Advanced web scraper with analytics"
```

This creates a project with:
- Web scraping capabilities
- Data analysis tools
- Complete project structure

### **Test 6: Add Custom Code Files**

```bash
🔧 AI Coder> write hello utils.py basic_app "Utility functions for the project"
```

## 🔍 Real-World Testing Scenarios

### **Scenario 1: Build a Web Scraper**

```bash
# Step 1: Create project
🔧 AI Coder> create webscraper python_app "Scrape website data"

# Step 2: Add scraper functionality
🔧 AI Coder> write webscraper scraper.py web_scraper "Main scraping logic"

# Step 3: Check what was created
🔧 AI Coder> info webscraper

# Step 4: Run the project
🔧 AI Coder> run webscraper
```

### **Scenario 2: Create a REST API**

```bash
# Create API project
🔧 AI Coder> create myapi api_project "User management API"

# Run the API server
🔧 AI Coder> run myapi
```

The API will start on `http://localhost:5000` with endpoints:
- `GET /` - API info
- `GET /health` - Health check
- `GET/POST /data` - Data management

**Test the API:**
```bash
# In another terminal
curl http://localhost:5000/
curl http://localhost:5000/health
```

### **Scenario 3: Data Analysis Project**

```bash
# Create data science project
🔧 AI Coder> create sales_analysis data_science "Sales data analyzer"

# Check project structure
🔧 AI Coder> info sales_analysis

# Run analysis
🔧 AI Coder> run sales_analysis
```

## 📁 Understanding Generated Files

### **Python App Structure**
After creating a Python app, you'll find:

**main.py:**
```python
#!/usr/bin/env python3
'''
My first AI-generated app
Created by AI Coder on 2025-01-XX
'''

def main():
    print("Hello, World!")
    pass

if __name__ == "__main__":
    main()
```

**config.py:**
```python
# Configuration settings
DEBUG = True
VERSION = '1.0.0'
```

### **Web App Structure**
**index.html:** Complete HTML page with CSS and JavaScript
**style.css:** Professional styling
**script.js:** Interactive functionality

## 🐛 Troubleshooting Common Issues

### **Issue 1: "Project already exists"**
```bash
🔧 AI Coder> create test python_app
# Error: Project test already exists

# Solution: Use different name or delete existing project
rm -rf projects/test  # Linux/Mac
rmdir /s projects\test  # Windows
```

### **Issue 2: "No main file found"**
This happens if project structure is corrupted.
```bash
# Check project info
🔧 AI Coder> info myproject

# Recreate main file
🔧 AI Coder> write myproject main.py basic_app "Main application file"
```

### **Issue 3: Execution timeout**
For long-running code:
```python
# The system has a 30-second timeout for safety
# For longer operations, break them into smaller chunks
```

## 📊 Testing Checklist

- [ ] **Basic Setup**: Can run `python main.py`
- [ ] **Project Creation**: Can create different project types
- [ ] **Code Execution**: Can execute simple Python code
- [ ] **Project Running**: Can run generated projects
- [ ] **File System**: Projects appear in `projects/` folder
- [ ] **Advanced Features**: Can create projects with multiple features
- [ ] **Error Handling**: System handles errors gracefully

## 🎮 Fun Tests to Try

### **1. Create a Calculator**
```bash
🔧 AI Coder> create calculator python_app "Simple calculator application"
🔧 AI Coder> execute
Enter Python code:
def add(a, b): return a + b
def multiply(a, b): return a * b
print(f"5 + 3 = {add(5, 3)}")
print(f"4 * 7 = {multiply(4, 7)}")
```

### **2. Generate Multiple Projects Quickly**
```bash
🔧 AI Coder> create app1 python_app
🔧 AI Coder> create app2 web_app
🔧 AI Coder> create app3 api_project
🔧 AI Coder> list
```

### **3. Test Code Validation**
```bash
🔧 AI Coder> execute
Enter Python code: print("missing quote)
# Should show syntax error

🔧 AI Coder> execute print("correct syntax")
# Should execute successfully
```

## 🔧 Advanced Usage Tips

1. **Batch Operations**: Create multiple projects in sequence
2. **Custom Templates**: Modify the code to add your own templates
3. **Integration**: Use generated projects as starting points
4. **Learning**: Examine generated code to learn patterns

## 🎯 Success Indicators

You know it's working when:
- ✅ Projects folder is created with subfolders
- ✅ Generated projects run without errors
- ✅ Code execution works for simple scripts
- ✅ Different project types create appropriate structures
- ✅ API projects start web servers successfully

Start with the interactive mode (`python main.py`) and try creating a simple project first. The system will guide you through everything!