#!/usr/bin/env python3
"""
AI Coder System - Autonomous Development Agent
A comprehensive AI system that can create projects, write code, and execute programs automatically.
"""

import os
import sys
import json
import time
import shutil
import logging
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
import ast
import re
import tempfile
from dataclasses import dataclass, asdict
import traceback

# Code Templates and Patterns
CODE_TEMPLATES = {
    "python": {
        "basic_app": """#!/usr/bin/env python3
'''
{description}
Created by AI Coder on {timestamp}
'''

def main():
    print("Hello, World!")
    {main_code}

if __name__ == "__main__":
    main()
""",
        "class_template": """class {class_name}:
    '''
    {description}
    '''
    
    def __init__(self{init_params}):
        {init_code}
    
    {methods}
""",
        "web_scraper": """#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin, urlparse

class WebScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_page(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return None
    
    def extract_data(self, soup, selectors):
        data = {}
        for key, selector in selectors.items():
            elements = soup.select(selector)
            data[key] = [elem.get_text().strip() for elem in elements]
        return data

if __name__ == "__main__":
    scraper = WebScraper("https://example.com")
    # Add your scraping logic here
""",
        "api_server": """#!/usr/bin/env python3
from flask import Flask, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)

# In-memory storage
data_store = {}

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "AI Coder API Server",
        "timestamp": datetime.now().isoformat(),
        "endpoints": ["/data", "/health"]
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/data', methods=['GET', 'POST'])
def handle_data():
    if request.method == 'GET':
        return jsonify(data_store)
    elif request.method == 'POST':
        data = request.get_json()
        data_store.update(data)
        return jsonify({"message": "Data updated", "data": data})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
""",
        "data_analyzer": """#!/usr/bin/env python3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class DataAnalyzer:
    def __init__(self, data_file=None):
        self.data = None
        self.results = {}
        if data_file:
            self.load_data(data_file)
    
    def load_data(self, file_path):
        try:
            if file_path.endswith('.csv'):
                self.data = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                self.data = pd.read_json(file_path)
            print(f"Data loaded: {self.data.shape}")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def basic_analysis(self):
        if self.data is None:
            return "No data loaded"
        
        analysis = {
            "shape": self.data.shape,
            "columns": list(self.data.columns),
            "dtypes": self.data.dtypes.to_dict(),
            "null_counts": self.data.isnull().sum().to_dict(),
            "basic_stats": self.data.describe().to_dict()
        }
        
        self.results['basic_analysis'] = analysis
        return analysis
    
    def generate_report(self, output_file="analysis_report.json"):
        if self.results:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            print(f"Report saved to {output_file}")

if __name__ == "__main__":
    analyzer = DataAnalyzer()
    # Add your analysis logic here
"""
    },
    "javascript": {
        "basic_app": """// {description}
// Created by AI Coder on {timestamp}

function main() {{
    console.log("Hello, World!");
    {main_code}
}}

main();
""",
        "web_app": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        button {{ padding: 10px 20px; margin: 10px 0; cursor: pointer; }}
        input {{ padding: 8px; margin: 5px 0; width: 200px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p>{description}</p>
        {html_content}
    </div>
    
    <script>
        {javascript_content}
    </script>
</body>
</html>"""
    }
}

PROJECT_STRUCTURES = {
    "python_app": {
        "main.py": "basic_app",
        "requirements.txt": "# Add dependencies here\n",
        "README.md": "# {project_name}\n\n{description}\n\n## Usage\n\n```bash\npython main.py\n```",
        "config.py": "# Configuration settings\nDEBUG = True\nVERSION = '1.0.0'\n",
        "src/__init__.py": "",
        "tests/test_main.py": "import unittest\nimport sys\nsys.path.append('../')\nfrom main import *\n\nclass TestMain(unittest.TestCase):\n    def test_basic(self):\n        self.assertTrue(True)\n\nif __name__ == '__main__':\n    unittest.main()"
    },
    "web_app": {
        "index.html": "web_app",
        "style.css": "/* Styles for {project_name} */\nbody {{ margin: 0; padding: 20px; font-family: Arial, sans-serif; }}\n.container {{ max-width: 1200px; margin: 0 auto; }}",
        "script.js": "// JavaScript for {project_name}\nconsole.log('App loaded');",
        "README.md": "# {project_name}\n\n{description}\n\n## Setup\n\nOpen index.html in a browser."
    },
    "api_project": {
        "app.py": "api_server",
        "requirements.txt": "flask==2.3.3\nrequests==2.31.0\n",
        "config.py": "class Config:\n    DEBUG = True\n    HOST = '0.0.0.0'\n    PORT = 5000",
        "README.md": "# {project_name} API\n\n{description}\n\n## Run\n\n```bash\npip install -r requirements.txt\npython app.py\n```"
    },
    "data_science": {
        "analyze.py": "data_analyzer",
        "requirements.txt": "pandas==2.0.3\nnumpy==1.24.3\nmatplotlib==3.7.2\nseaborn==0.12.2\n",
        "data/sample.csv": "name,value\nitem1,100\nitem2,200\nitem3,150",
        "notebooks/analysis.ipynb": r'{\n "cells": [],\n "metadata": {},\n "nbformat": 4,\n "nbformat_minor": 4\n}',
        "README.md": "# {project_name}\n\n{description}\n\nData Science Project with analysis tools."
    }
}

@dataclass
class ProjectSpec:
    """Project specification"""
    name: str
    type: str
    description: str
    language: str = "python"
    features: List[str] = None
    custom_code: Dict[str, str] = None

class CodeGenerator:
    """Generate code based on specifications"""
    
    def __init__(self):
        self.templates = CODE_TEMPLATES
    
    def generate_code(self, spec: Dict[str, Any]) -> str:
        """Generate code from specification"""
        language = spec.get('language', 'python')
        code_type = spec.get('type', 'basic_app')
        
        if language not in self.templates:
            return f"# Unsupported language: {language}\npass"
        
        if code_type not in self.templates[language]:
            code_type = 'basic_app'
        
        template = self.templates[language][code_type]
        
        # Fill template variables
        variables = {
            'description': spec.get('description', 'Generated by AI Coder'),
            'timestamp': datetime.now().isoformat(),
            'main_code': spec.get('main_code', 'pass'),
            'class_name': spec.get('class_name', 'GeneratedClass'),
            'init_params': spec.get('init_params', ''),
            'init_code': spec.get('init_code', 'pass'),
            'methods': spec.get('methods', ''),
            'title': spec.get('title', 'AI Generated App'),
            'html_content': spec.get('html_content', '<p>Content goes here</p>'),
            'javascript_content': spec.get('javascript_content', 'console.log("Ready");')
        }
        
        try:
            return template.format(**variables)
        except KeyError as e:
            # Try to handle missing variables gracefully
            missing_key = str(e).strip("'")
            if missing_key in ['project_name', 'title']:
                variables[missing_key] = spec.get('project_name', 'MyProject')
            elif missing_key == 'description':
                variables[missing_key] = spec.get('description', 'Generated by AI Coder')
            else:
                variables[missing_key] = f"[{missing_key}]"
            
            try:
                return template.format(**variables)
            except Exception:
                return f"# Template formatting error\n# {template}"
    
    def generate_function(self, func_name: str, description: str, params: List[str], return_type: str = "None") -> str:
        """Generate a function"""
        param_str = ", ".join(params) if params else ""
        
        if params:
            args_doc = "\n        ".join(f"{param}: Description for {param}" for param in params)
        else:
            args_doc = "None"
            
        code = f'''def {func_name}({param_str}) -> {return_type}:
    """
    {description}
    
    Args:
        {args_doc}
    
    Returns:
        {return_type}: Description of return value
    """
    # TODO: Implement {func_name}
    pass
'''
        return code
    
    def generate_class(self, class_name: str, description: str, methods: List[str]) -> str:
        """Generate a class"""
        method_code = ""
        for method in methods:
            method_code += f"    def {method}(self):\n        '''TODO: Implement {method}'''\n        pass\n\n"
        
        spec = {
            'class_name': class_name,
            'description': description,
            'init_params': '',
            'init_code': 'pass',
            'methods': method_code.rstrip()
        }
        
        return self.generate_code({'language': 'python', 'type': 'class_template', **spec})

class ProjectCreator:
    """Create complete projects"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.projects_dir = self.base_path / "projects"
        self.projects_dir.mkdir(exist_ok=True)
        self.code_generator = CodeGenerator()
    
    def create_project(self, spec: ProjectSpec) -> Tuple[bool, str]:
        """Create a complete project"""
        project_path = self.projects_dir / spec.name
        
        if project_path.exists():
            return False, f"Project {spec.name} already exists"
        
        try:
            project_path.mkdir(parents=True)
            
            # Get project structure
            structure = PROJECT_STRUCTURES.get(spec.type, PROJECT_STRUCTURES['python_app'])
            
            # Create files
            for file_path, template_or_content in structure.items():
                full_path = project_path / file_path
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                if template_or_content in CODE_TEMPLATES.get(spec.language, {}):
                    # Generate from template
                    code_spec = {
                        'language': spec.language,
                        'type': template_or_content,
                        'description': spec.description,
                        'project_name': spec.name
                    }
                    content = self.code_generator.generate_code(code_spec)
                else:
                    # Use content directly
                    try:
                        content = template_or_content.format(
                            project_name=spec.name,
                            description=spec.description
                        )
                    except KeyError as e:
                        # Handle missing variables gracefully
                        missing_key = str(e).strip("'")
                        if missing_key == 'project_name':
                            content = template_or_content.replace('{project_name}', spec.name)
                        elif missing_key == 'description':
                            content = template_or_content.replace('{description}', spec.description)
                        else:
                            content = template_or_content
                
                full_path.write_text(content, encoding='utf-8')
            
            # Add custom code files if specified
            if spec.custom_code:
                for file_name, code in spec.custom_code.items():
                    custom_file = project_path / file_name
                    custom_file.write_text(code, encoding='utf-8')
            
            return True, f"Project {spec.name} created successfully at {project_path}"
        
        except Exception as e:
            return False, f"Error creating project: {str(e)}"

class CodeExecutor:
    """Execute code safely"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.execution_dir = self.base_path / "execution"
        self.execution_dir.mkdir(exist_ok=True)
    
    def execute_python_code(self, code: str, timeout: int = 30) -> Tuple[bool, str, str]:
        """Execute Python code and return success, stdout, stderr"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=self.execution_dir) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute code
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.execution_dir
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return result.returncode == 0, result.stdout, result.stderr
            
        except subprocess.TimeoutExpired:
            return False, "", "Execution timed out"
        except Exception as e:
            return False, "", f"Execution error: {str(e)}"
    
    def execute_project(self, project_name: str) -> Tuple[bool, str]:
        """Execute a project's main file"""
        project_path = self.base_path / "projects" / project_name
        
        if not project_path.exists():
            return False, f"Project {project_name} not found"
        
        # Find main file
        main_files = ['main.py', 'app.py', 'run.py']
        main_file = None
        
        for filename in main_files:
            if (project_path / filename).exists():
                main_file = project_path / filename
                break
        
        if not main_file:
            return False, "No main file found (main.py, app.py, or run.py)"
        
        try:
            # Install requirements if exists
            requirements_file = project_path / "requirements.txt"
            if requirements_file.exists():
                req_result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
                    capture_output=True,
                    text=True
                )
                if req_result.returncode != 0:
                    return False, f"Failed to install requirements: {req_result.stderr}"
            
            # Execute main file
            result = subprocess.run(
                [sys.executable, str(main_file)],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=project_path
            )
            
            if result.returncode == 0:
                return True, f"Project executed successfully:\n{result.stdout}"
            else:
                return False, f"Execution failed:\n{result.stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "Project execution timed out"
        except Exception as e:
            return False, f"Error executing project: {str(e)}"
    
    def validate_python_syntax(self, code: str) -> Tuple[bool, str]:
        """Validate Python code syntax"""
        try:
            ast.parse(code)
            return True, "Code syntax is valid"
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"

class AICoder:
    """Main AI Coder system"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path).resolve()
        self.setup_logging()
        
        # Initialize components
        self.project_creator = ProjectCreator(str(self.base_path))
        self.code_executor = CodeExecutor(str(self.base_path))
        self.code_generator = CodeGenerator()
        
        # Create workspace
        self.create_workspace()
        
        self.logger.info("AI Coder System initialized")
    
    def setup_logging(self):
        """Setup logging system"""
        log_dir = self.base_path / "logs"
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "ai_coder.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("AICoder")
    
    def create_workspace(self):
        """Create workspace directories"""
        dirs = ["projects", "execution", "templates", "outputs", "logs"]
        for dir_name in dirs:
            (self.base_path / dir_name).mkdir(exist_ok=True)
    
    def create_simple_project(self, name: str, project_type: str, description: str) -> str:
        """Create a simple project"""
        spec = ProjectSpec(
            name=name,
            type=project_type,
            description=description,
            language="python"
        )
        
        success, message = self.project_creator.create_project(spec)
        
        if success:
            self.logger.info(f"Project created: {name}")
        else:
            self.logger.error(f"Project creation failed: {message}")
        
        return message
    
    def write_code_file(self, project_name: str, filename: str, code_spec: Dict[str, Any]) -> str:
        """Write a code file to a project"""
        project_path = self.base_path / "projects" / project_name
        
        if not project_path.exists():
            return f"Project {project_name} does not exist"
        
        try:
            # Generate code
            code = self.code_generator.generate_code(code_spec)
            
            # Write file
            file_path = project_path / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(code, encoding='utf-8')
            
            self.logger.info(f"Code file written: {file_path}")
            return f"Code file {filename} written successfully"
        
        except Exception as e:
            error_msg = f"Error writing code file: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
    
    def execute_code(self, code: str) -> str:
        """Execute Python code"""
        # Validate syntax first
        valid, message = self.code_executor.validate_python_syntax(code)
        if not valid:
            return f"Syntax Error: {message}"
        
        # Execute code
        success, stdout, stderr = self.code_executor.execute_python_code(code)
        
        if success:
            return f"Execution successful:\n{stdout}"
        else:
            return f"Execution failed:\n{stderr}"
    
    def run_project(self, project_name: str) -> str:
        """Run a project"""
        success, message = self.code_executor.execute_project(project_name)
        
        if success:
            self.logger.info(f"Project {project_name} executed successfully")
        else:
            self.logger.error(f"Project {project_name} execution failed")
        
        return message
    
    def list_projects(self) -> str:
        """List all projects"""
        projects_dir = self.base_path / "projects"
        projects = [p.name for p in projects_dir.iterdir() if p.is_dir()]
        
        if projects:
            return f"Projects: {', '.join(projects)}"
        else:
            return "No projects found"
    
    def get_project_info(self, project_name: str) -> str:
        """Get information about a project"""
        project_path = self.base_path / "projects" / project_name
        
        if not project_path.exists():
            return f"Project {project_name} not found"
        
        files = list(project_path.rglob("*"))
        file_list = [str(f.relative_to(project_path)) for f in files if f.is_file()]
        
        info = f"""Project: {project_name}
Location: {project_path}
Files: {len(file_list)}
Structure:
"""
        for file in sorted(file_list)[:20]:  # Show first 20 files
            info += f"  - {file}\n"
        
        if len(file_list) > 20:
            info += f"  ... and {len(file_list) - 20} more files"
        
        return info
    
    def generate_advanced_project(self, name: str, description: str, features: List[str]) -> str:
        """Generate an advanced project with specific features"""
        custom_code = {}
        
        # Generate code based on features
        if "web_scraping" in features:
            custom_code["scraper.py"] = self.code_generator.generate_code({
                'language': 'python',
                'type': 'web_scraper',
                'description': f"Web scraper for {name}"
            })
        
        if "api" in features:
            custom_code["api.py"] = self.code_generator.generate_code({
                'language': 'python',
                'type': 'api_server',
                'description': f"API server for {name}"
            })
        
        if "data_analysis" in features:
            custom_code["analyzer.py"] = self.code_generator.generate_code({
                'language': 'python',
                'type': 'data_analyzer',
                'description': f"Data analyzer for {name}"
            })
        
        # Create project with custom code
        spec = ProjectSpec(
            name=name,
            type="python_app",
            description=description,
            features=features,
            custom_code=custom_code
        )
        
        success, message = self.project_creator.create_project(spec)
        return message
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("🤖 AI Coder System - Interactive Mode")
        print("=" * 50)
        print("Commands:")
        print("  create <name> <type> - Create project (types: python_app, web_app, api_project, data_science)")
        print("  advanced <name> <features> - Create advanced project with features")
        print("  write <project> <filename> <type> - Write code file")
        print("  execute <code> - Execute Python code")
        print("  run <project> - Run project")
        print("  list - List projects")
        print("  info <project> - Get project info")
        print("  exit - Quit")
        print("-" * 50)
        
        while True:
            try:
                command = input("\n🔧 AI Coder> ").strip()
                
                if not command:
                    continue
                
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == "exit":
                    break
                
                elif cmd == "create" and len(parts) >= 3:
                    name, project_type = parts[1], parts[2]
                    description = " ".join(parts[3:]) or f"AI Generated {project_type}"
                    result = self.create_simple_project(name, project_type, description)
                    print(result)
                
                elif cmd == "advanced" and len(parts) >= 3:
                    name = parts[1]
                    features = parts[2].split(",")
                    description = " ".join(parts[3:]) or f"Advanced project with {', '.join(features)}"
                    result = self.generate_advanced_project(name, description, features)
                    print(result)
                
                elif cmd == "write" and len(parts) >= 4:
                    project, filename, code_type = parts[1], parts[2], parts[3]
                    description = " ".join(parts[4:]) or f"Generated {code_type}"
                    
                    code_spec = {
                        'language': 'python',
                        'type': code_type,
                        'description': description
                    }
                    result = self.write_code_file(project, filename, code_spec)
                    print(result)
                
                elif cmd == "execute":
                    code = " ".join(parts[1:])
                    if not code:
                        code = input("Enter Python code: ")
                    result = self.execute_code(code)
                    print(result)
                
                elif cmd == "run" and len(parts) >= 2:
                    project = parts[1]
                    result = self.run_project(project)
                    print(result)
                
                elif cmd == "list":
                    result = self.list_projects()
                    print(result)
                
                elif cmd == "info" and len(parts) >= 2:
                    project = parts[1]
                    result = self.get_project_info(project)
                    print(result)
                
                else:
                    print("Unknown command. Type 'exit' to quit.")
            
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")
        
        print("AI Coder System shut down.")

def main():
    """Main entry point"""
    print("Initializing AI Coder System...")
    
    # Initialize AI Coder
    ai_coder = AICoder()
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create" and len(sys.argv) >= 4:
            name, project_type = sys.argv[2], sys.argv[3]
            description = " ".join(sys.argv[4:]) or f"Command line project"
            result = ai_coder.create_simple_project(name, project_type, description)
            print(result)
        
        elif command == "run" and len(sys.argv) >= 3:
            project = sys.argv[2]
            result = ai_coder.run_project(project)
            print(result)
        
        elif command == "list":
            result = ai_coder.list_projects()
            print(result)
        
        elif command == "info" and len(sys.argv) >= 3:
            project = sys.argv[2]
            result = ai_coder.get_project_info(project)
            print(result)
        else:
            print("Usage: python main.py [create <name> <type> | run <project> | list | info <project>]")
    else:
        # Run in interactive mode
        ai_coder.interactive_mode()

if __name__ == "__main__":
    main()
