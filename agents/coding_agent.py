#!/usr/bin/env python3
"""
Coding Agent
Handles software development, code generation, and project creation
"""

import os
import subprocess
import tempfile
from typing import Dict, Any
from datetime import datetime

from .base_agent import BaseAgent, AgentTask

class CodingAgent(BaseAgent):
    """Agent responsible for coding and software development tasks"""
    
    def __init__(self, services: Dict[str, Any]):
        super().__init__("coding", services)
        
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process coding-related tasks"""
        try:
            task_type = task.type
            description = task.description.lower()
            
            if task_type == "create_project" or "create project" in description:
                return await self._create_project(task)
            elif "code" in description or "program" in description:
                return await self._generate_code(task)
            elif "build" in description or "compile" in description:
                return await self._build_project(task)
            elif "test" in description:
                return await self._run_tests(task)
            else:
                return await self._general_coding_task(task)
                
        except Exception as e:
            self.logger.error(f"Coding task failed: {e}")
            return {"error": str(e)}
    
    async def _create_project(self, task: AgentTask) -> Dict[str, Any]:
        """Create a new project"""
        try:
            # Extract project details from task
            description = task.description
            data = task.data
            
            # Determine project type and name
            if "python" in description:
                project_type = "python"
            elif "web" in description or "html" in description:
                project_type = "web"
            elif "api" in description:
                project_type = "api"
            else:
                project_type = "python"  # default
            
            # Extract project name
            project_name = data.get("project_name", "new_project")
            
            # Create project directory
            projects_dir = self.file_manager.base_path / "data" / "projects"
            project_dir = projects_dir / project_name
            project_dir.mkdir(parents=True, exist_ok=True)
            
            # Create project files based on type
            if project_type == "python":
                await self._create_python_project(project_dir)
            elif project_type == "web":
                await self._create_web_project(project_dir)
            elif project_type == "api":
                await self._create_api_project(project_dir)
            
            return {
                "success": True,
                "project_name": project_name,
                "project_type": project_type,
                "project_path": str(project_dir),
                "files_created": list(project_dir.glob("*"))
            }
            
        except Exception as e:
            return {"error": f"Project creation failed: {e}"}
    
    async def _create_python_project(self, project_dir):
        """Create a Python project structure"""
        files = {
            "main.py": "#!/usr/bin/env python3\n\nif __name__ == '__main__':\n    print('Hello, World!')\n",
            "requirements.txt": "# Add your requirements here\n",
            "README.md": f"# {project_dir.name}\n\nPython project created by World AI Agent System.\n",
            "src/__init__.py": "",
            "tests/__init__.py": "",
            "tests/test_main.py": "import unittest\n\nclass TestMain(unittest.TestCase):\n    def test_example(self):\n        self.assertTrue(True)\n"
        }
        
        for file_path, content in files.items():
            full_path = project_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
    
    async def _create_web_project(self, project_dir):
        """Create a web project structure"""
        files = {
            "index.html": """<!DOCTYPE html>
<html>
<head>
    <title>Web App</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <h1>Hello, World!</h1>
    <p>Created by World AI Agent System</p>
    <script src="script.js"></script>
</body>
</html>""",
            "style.css": """body { 
    font-family: Arial, sans-serif; 
    margin: 40px;
    background-color: #f5f5f5;
}
h1 {
    color: #333;
}""",
            "script.js": "console.log('Hello, World!');\nconsole.log('Created by World AI Agent System');",
            "README.md": f"# {project_dir.name}\n\nWeb application created by World AI Agent System.\n"
        }
        
        for file_path, content in files.items():
            full_path = project_dir / file_path
            full_path.write_text(content)
    
    async def _create_api_project(self, project_dir):
        """Create an API project structure"""
        files = {
            "app.py": """from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return jsonify({
        'message': 'Hello, API!',
        'created_by': 'World AI Agent System'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)""",
            "requirements.txt": "flask==2.3.3\n",
            "README.md": f"# {project_dir.name}\n\nAPI project created by World AI Agent System.\n"
        }
        
        for file_path, content in files.items():
            full_path = project_dir / file_path
            full_path.write_text(content)
    
    async def _generate_code(self, task: AgentTask) -> Dict[str, Any]:
        """Generate code based on description"""
        try:
            description = task.description
            
            # Simple code generation based on keywords
            if "web scraper" in description:
                code = self._generate_web_scraper_code()
            elif "api" in description:
                code = self._generate_api_code()
            elif "data analysis" in description:
                code = self._generate_data_analysis_code()
            else:
                code = self._generate_general_code(description)
            
            # Save generated code
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            code_file = self.file_manager.base_path / "data" / f"generated_code_{timestamp}.py"
            code_file.write_text(code)
            
            return {
                "success": True,
                "code": code,
                "file_path": str(code_file),
                "description": "Code generated successfully"
            }
            
        except Exception as e:
            return {"error": f"Code generation failed: {e}"}
    
    def _generate_web_scraper_code(self) -> str:
        """Generate web scraper code"""
        return '''#!/usr/bin/env python3
"""
Web Scraper - Generated by World AI Agent System
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict

class WebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_url(self, url: str) -> Dict:
        """Scrape a single URL"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract basic information
            data = {
                'url': url,
                'title': soup.title.string if soup.title else '',
                'headings': [h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])],
                'links': [a.get('href') for a in soup.find_all('a', href=True)],
                'images': [img.get('src') for img in soup.find_all('img', src=True)]
            }
            
            return data
            
        except Exception as e:
            return {'error': str(e), 'url': url}
    
    def scrape_multiple(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple URLs"""
        results = []
        for url in urls:
            result = self.scrape_url(url)
            results.append(result)
        return results

if __name__ == '__main__':
    scraper = WebScraper()
    
    # Example usage
    urls = ['https://example.com']
    results = scraper.scrape_multiple(urls)
    
    # Save results
    with open('scraped_data.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Scraping completed!")
'''
    
    def _generate_api_code(self) -> str:
        """Generate API code"""
        return '''#!/usr/bin/env python3
"""
REST API - Generated by World AI Agent System
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

# Sample data
data = {
    'users': [],
    'items': []
}

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'API is running'})

@app.route('/api/users', methods=['GET'])
def get_users():
    """Get all users"""
    return jsonify(data['users'])

@app.route('/api/users', methods=['POST'])
def create_user():
    """Create a new user"""
    user_data = request.get_json()
    user_data['id'] = len(data['users']) + 1
    data['users'].append(user_data)
    return jsonify(user_data), 201

@app.route('/api/items', methods=['GET'])
def get_items():
    """Get all items"""
    return jsonify(data['items'])

@app.route('/api/items', methods=['POST'])
def create_item():
    """Create a new item"""
    item_data = request.get_json()
    item_data['id'] = len(data['items']) + 1
    data['items'].append(item_data)
    return jsonify(item_data), 201

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
'''
    
    def _generate_data_analysis_code(self) -> str:
        """Generate data analysis code"""
        return '''#!/usr/bin/env python3
"""
Data Analysis - Generated by World AI Agent System
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any

class DataAnalyzer:
    def __init__(self, data_path: str = None):
        self.data = None
        if data_path:
            self.load_data(data_path)
    
    def load_data(self, path: str):
        """Load data from file"""
        if path.endswith('.csv'):
            self.data = pd.read_csv(path)
        elif path.endswith('.json'):
            self.data = pd.read_json(path)
        else:
            raise ValueError("Unsupported file format")
    
    def basic_stats(self) -> Dict[str, Any]:
        """Get basic statistics"""
        if self.data is None:
            return {'error': 'No data loaded'}
        
        return {
            'shape': self.data.shape,
            'columns': list(self.data.columns),
            'dtypes': self.data.dtypes.to_dict(),
            'missing_values': self.data.isnull().sum().to_dict(),
            'basic_stats': self.data.describe().to_dict()
        }
    
    def visualize(self, column: str = None):
        """Create visualizations"""
        if self.data is None:
            print("No data loaded")
            return
        
        plt.figure(figsize=(12, 8))
        
        if column and column in self.data.columns:
            if self.data[column].dtype in ['int64', 'float64']:
                plt.subplot(2, 2, 1)
                self.data[column].hist()
                plt.title(f'Distribution of {column}')
                
                plt.subplot(2, 2, 2)
                self.data[column].plot(kind='box')
                plt.title(f'Box plot of {column}')
        else:
            # Show correlation matrix for numeric columns
            numeric_data = self.data.select_dtypes(include=[np.number])
            if not numeric_data.empty:
                plt.subplot(2, 2, 1)
                sns.heatmap(numeric_data.corr(), annot=True, cmap='coolwarm')
                plt.title('Correlation Matrix')
        
        plt.tight_layout()
        plt.show()
    
    def export_report(self, filename: str = 'analysis_report.txt'):
        """Export analysis report"""
        stats = self.basic_stats()
        
        with open(filename, 'w') as f:
            f.write("Data Analysis Report\\n")
            f.write("=" * 50 + "\\n\\n")
            f.write(f"Dataset shape: {stats['shape']}\\n")
            f.write(f"Columns: {', '.join(stats['columns'])}\\n\\n")
            f.write("Missing values:\\n")
            for col, missing in stats['missing_values'].items():
                f.write(f"  {col}: {missing}\\n")
        
        print(f"Report exported to {filename}")

if __name__ == '__main__':
    # Example usage
    analyzer = DataAnalyzer()
    print("Data analyzer ready!")
    print("Use analyzer.load_data('your_file.csv') to load data")
'''
    
    def _generate_general_code(self, description: str) -> str:
        """Generate general code based on description"""
        return f'''#!/usr/bin/env python3
"""
Generated Code - Created by World AI Agent System
Description: {description}
"""

def main():
    """Main function"""
    print("Hello, World!")
    print("This code was generated by World AI Agent System")
    print(f"Task: {description}")

if __name__ == '__main__':
    main()
'''
    
    async def _build_project(self, task: AgentTask) -> Dict[str, Any]:
        """Build a project"""
        return {"message": "Build functionality not yet implemented"}
    
    async def _run_tests(self, task: AgentTask) -> Dict[str, Any]:
        """Run tests for a project"""
        return {"message": "Test functionality not yet implemented"}
    
    async def _general_coding_task(self, task: AgentTask) -> Dict[str, Any]:
        """Handle general coding tasks"""
        return {
            "message": f"Coding agent received task: {task.description}",
            "status": "processed"
        }
