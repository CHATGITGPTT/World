#!/usr/bin/env python3
"""
AI Coding Agent System
A powerful AI agent that can build software, reason, and manage its own data structures.
"""

import os
import sys
import json
import time
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import threading
import queue
import ast
import importlib.util
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

# Core System Configuration
@dataclass
class SystemConfig:
    """Configuration for the AI Coding Agent System"""
    base_path: str = "."
    api_key: str = ""
    model: str = "claude-sonnet-4-20250514"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    auto_refine: bool = True
    backup_enabled: bool = True
    debug_mode: bool = False
    memory_limit: int = 1000  # Max memories to keep
    
class Logger:
    """Enhanced logging system"""
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.log_dir = self.base_path / "logs"
        self.log_dir.mkdir(exist_ok=True)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / "system.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("AIAgent")
    
    def info(self, msg: str): self.logger.info(msg)
    def error(self, msg: str): self.logger.error(msg)
    def warning(self, msg: str): self.logger.warning(msg)
    def debug(self, msg: str): self.logger.debug(msg)

class FileManager:
    """Manages all file operations with recursive access"""
    def __init__(self, base_path: str, logger: Logger):
        self.base_path = Path(base_path).resolve()
        self.logger = logger
        self.ensure_directory_structure()
    
    def ensure_directory_structure(self):
        """Create essential directories"""
        dirs = [
            "agents", "memory", "projects", "data", "logs", "backups",
            "templates", "knowledge", "tools", "cache", "outputs"
        ]
        for dir_name in dirs:
            (self.base_path / dir_name).mkdir(exist_ok=True)
    
    def scan_all_files(self) -> List[Path]:
        """Recursively scan all files in the system"""
        files = []
        for root, dirs, filenames in os.walk(self.base_path):
            for filename in filenames:
                files.append(Path(root) / filename)
        return files
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Read file with error handling"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
                self.logger.warning(f"File {path} too large, skipping")
                return None
            
            return path.read_text(encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return None
    
    def write_file(self, file_path: str, content: str, backup: bool = True) -> bool:
        """Write file with backup option"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            # Create backup if file exists
            if backup and path.exists():
                backup_path = self.base_path / "backups" / f"{path.name}.{int(time.time())}"
                shutil.copy2(path, backup_path)
            
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            path.write_text(content, encoding='utf-8')
            self.logger.info(f"File written: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing {file_path}: {e}")
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file safely"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if path.exists():
                path.unlink()
                self.logger.info(f"File deleted: {path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error deleting {file_path}: {e}")
            return False

class Memory:
    """Self-refining memory system"""
    def __init__(self, file_manager: FileManager, logger: Logger):
        self.file_manager = file_manager
        self.logger = logger
        self.memory_file = "memory/core_memory.json"
        self.memories = self.load_memories()
        
    def load_memories(self) -> Dict[str, Any]:
        """Load memories from file"""
        content = self.file_manager.read_file(self.memory_file)
        if content:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                self.logger.error("Corrupted memory file, starting fresh")
        return {
            "experiences": [],
            "patterns": {},
            "knowledge": {},
            "skills": {},
            "preferences": {},
            "metadata": {"created": datetime.now().isoformat(), "version": "1.0"}
        }
    
    def save_memories(self):
        """Save memories to file"""
        self.file_manager.write_file(self.memory_file, json.dumps(self.memories, indent=2))
    
    def add_experience(self, experience: Dict[str, Any]):
        """Add new experience and refine"""
        self.memories["experiences"].append({
            **experience,
            "timestamp": datetime.now().isoformat()
        })
        self.refine_memories()
    
    def refine_memories(self):
        """Refine and optimize memories"""
        # Keep only recent experiences
        max_experiences = 1000
        if len(self.memories["experiences"]) > max_experiences:
            # Keep most recent and most important
            self.memories["experiences"] = self.memories["experiences"][-max_experiences:]
        
        # Extract patterns
        self.extract_patterns()
        
        # Update knowledge base
        self.update_knowledge()
        
        # Save refined memories
        self.save_memories()
        self.logger.info("Memories refined and saved")
    
    def extract_patterns(self):
        """Extract patterns from experiences"""
        for exp in self.memories["experiences"]:
            if "pattern" in exp:
                pattern_type = exp.get("type", "general")
                if pattern_type not in self.memories["patterns"]:
                    self.memories["patterns"][pattern_type] = []
                self.memories["patterns"][pattern_type].append(exp["pattern"])
    
    def update_knowledge(self):
        """Update knowledge base from experiences"""
        for exp in self.memories["experiences"]:
            if "knowledge" in exp:
                for topic, info in exp["knowledge"].items():
                    if topic not in self.memories["knowledge"]:
                        self.memories["knowledge"][topic] = []
                    self.memories["knowledge"][topic].append(info)

class CodeExecutor:
    """Execute and manage code safely"""
    def __init__(self, file_manager: FileManager, logger: Logger):
        self.file_manager = file_manager
        self.logger = logger
        self.execution_dir = file_manager.base_path / "execution"
        self.execution_dir.mkdir(exist_ok=True)
    
    def execute_python(self, code: str, timeout: int = 30) -> Tuple[bool, str]:
        """Execute Python code safely"""
        try:
            # Create temporary file
            temp_file = self.execution_dir / f"temp_{int(time.time())}.py"
            temp_file.write_text(code)
            
            # Execute with timeout
            result = subprocess.run(
                [sys.executable, str(temp_file)],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.execution_dir
            )
            
            # Clean up
            temp_file.unlink()
            
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stderr
        except subprocess.TimeoutExpired:
            return False, "Code execution timed out"
        except Exception as e:
            return False, f"Execution error: {str(e)}"
    
    def validate_code(self, code: str) -> Tuple[bool, str]:
        """Validate Python code syntax"""
        try:
            ast.parse(code)
            return True, "Code is valid"
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"

class ProjectManager:
    """Manages software projects"""
    def __init__(self, file_manager: FileManager, logger: Logger):
        self.file_manager = file_manager
        self.logger = logger
        self.projects_dir = file_manager.base_path / "projects"
        self.templates_dir = file_manager.base_path / "templates"
    
    def create_project(self, name: str, project_type: str = "python") -> bool:
        """Create a new project"""
        project_dir = self.projects_dir / name
        if project_dir.exists():
            self.logger.warning(f"Project {name} already exists")
            return False
        
        project_dir.mkdir(parents=True)
        
        # Create basic structure based on type
        if project_type == "python":
            self.create_python_project(project_dir)
        elif project_type == "web":
            self.create_web_project(project_dir)
        elif project_type == "api":
            self.create_api_project(project_dir)
        
        self.logger.info(f"Project {name} created successfully")
        return True
    
    def create_python_project(self, project_dir: Path):
        """Create Python project structure"""
        files = {
            "main.py": "#!/usr/bin/env python3\n\nif __name__ == '__main__':\n    print('Hello, World!')\n",
            "requirements.txt": "# Add your requirements here\n",
            "README.md": f"# {project_dir.name}\n\nProject description here.\n",
            "src/__init__.py": "",
            "tests/__init__.py": "",
            "tests/test_main.py": "import unittest\n\nclass TestMain(unittest.TestCase):\n    def test_example(self):\n        self.assertTrue(True)\n"
        }
        
        for file_path, content in files.items():
            self.file_manager.write_file(str(project_dir / file_path), content)
    
    def create_web_project(self, project_dir: Path):
        """Create web project structure"""
        files = {
            "index.html": "<!DOCTYPE html>\n<html>\n<head>\n    <title>Web App</title>\n</head>\n<body>\n    <h1>Hello, World!</h1>\n</body>\n</html>",
            "style.css": "body { font-family: Arial, sans-serif; }",
            "script.js": "console.log('Hello, World!');",
            "README.md": f"# {project_dir.name}\n\nWeb application project.\n"
        }
        
        for file_path, content in files.items():
            self.file_manager.write_file(str(project_dir / file_path), content)
    
    def create_api_project(self, project_dir: Path):
        """Create API project structure"""
        files = {
            "app.py": "from flask import Flask\n\napp = Flask(__name__)\n\n@app.route('/')\ndef hello():\n    return 'Hello, API!'\n\nif __name__ == '__main__':\n    app.run(debug=True)",
            "requirements.txt": "flask==2.3.3\n",
            "README.md": f"# {project_dir.name}\n\nAPI project.\n"
        }
        
        for file_path, content in files.items():
            self.file_manager.write_file(str(project_dir / file_path), content)

class CommandProcessor:
    """Process and understand user commands"""
    def __init__(self, file_manager: FileManager, memory: Memory, logger: Logger):
        self.file_manager = file_manager
        self.memory = memory
        self.logger = logger
        self.project_manager = ProjectManager(file_manager, logger)
        self.code_executor = CodeExecutor(file_manager, logger)
    
    def process_command(self, command: str) -> str:
        """Process user command and return response"""
        command = command.strip().lower()
        
        # Log the command
        self.memory.add_experience({
            "type": "command",
            "command": command,
            "timestamp": datetime.now().isoformat()
        })
        
        # Basic command routing
        if command.startswith("create project"):
            return self.handle_create_project(command)
        elif command.startswith("list") or command.startswith("show"):
            return self.handle_list_command(command)
        elif command.startswith("build") or command.startswith("make"):
            return self.handle_build_command(command)
        elif command.startswith("run") or command.startswith("execute"):
            return self.handle_run_command(command)
        elif command.startswith("analyze"):
            return self.handle_analyze_command(command)
        elif command.startswith("help"):
            return self.show_help()
        else:
            return self.handle_general_command(command)
    
    def handle_create_project(self, command: str) -> str:
        """Handle project creation commands"""
        parts = command.split()
        if len(parts) < 3:
            return "Usage: create project <name> [type]"
        
        name = parts[2]
        project_type = parts[3] if len(parts) > 3 else "python"
        
        if self.project_manager.create_project(name, project_type):
            return f"Project '{name}' created successfully as {project_type} project"
        else:
            return f"Failed to create project '{name}'"
    
    def handle_list_command(self, command: str) -> str:
        """Handle list/show commands"""
        if "projects" in command:
            projects = [p.name for p in self.file_manager.base_path.glob("projects/*") if p.is_dir()]
            return f"Projects: {', '.join(projects) if projects else 'None'}"
        elif "files" in command:
            files = self.file_manager.scan_all_files()
            return f"Found {len(files)} files in system"
        elif "memory" in command:
            exp_count = len(self.memory.memories["experiences"])
            return f"Memory: {exp_count} experiences stored"
        else:
            return "Available items: projects, files, memory"
    
    def handle_build_command(self, command: str) -> str:
        """Handle build/make commands"""
        return "Build system ready. Specify what you want to build."
    
    def handle_run_command(self, command: str) -> str:
        """Handle run/execute commands"""
        return "Execution system ready. Provide code to execute."
    
    def handle_analyze_command(self, command: str) -> str:
        """Handle analyze commands"""
        files = self.file_manager.scan_all_files()
        python_files = [f for f in files if f.suffix == '.py']
        total_size = sum(f.stat().st_size for f in files)
        
        analysis = f"""
System Analysis:
- Total files: {len(files)}
- Python files: {len(python_files)}
- Total size: {total_size / 1024:.2f} KB
- Projects: {len(list(self.file_manager.base_path.glob('projects/*')))}
- Memories: {len(self.memory.memories['experiences'])}
"""
        return analysis.strip()
    
    def handle_general_command(self, command: str) -> str:
        """Handle general commands with reasoning"""
        # This is where you'd integrate with Claude API
        # For now, provide a basic response
        return f"I understand you want to: {command}. I'm ready to help build this system."
    
    def show_help(self) -> str:
        """Show available commands"""
        return """
Available Commands:
- create project <name> [type] - Create a new project
- list projects/files/memory - Show system information
- build <description> - Build something
- run <code> - Execute code
- analyze - Analyze system
- help - Show this help

I can understand natural language commands and build any software you need.
"""

class AIAgent:
    """Main AI Agent class"""
    def __init__(self, config: SystemConfig):
        self.config = config
        self.base_path = Path(config.base_path).resolve()
        
        # Initialize core systems
        self.logger = Logger(str(self.base_path))
        self.file_manager = FileManager(str(self.base_path), self.logger)
        self.memory = Memory(self.file_manager, self.logger)
        self.command_processor = CommandProcessor(self.file_manager, self.memory, self.logger)
        
        # Start background processes
        self.running = True
        self.start_background_tasks()
        
        self.logger.info("AI Agent System initialized successfully")
    
    def start_background_tasks(self):
        """Start background maintenance tasks"""
        def background_worker():
            while self.running:
                try:
                    # Auto-refine memories every 5 minutes
                    if self.config.auto_refine:
                        self.memory.refine_memories()
                    
                    # Clean up old temporary files
                    self.cleanup_temp_files()
                    
                    time.sleep(300)  # 5 minutes
                except Exception as e:
                    self.logger.error(f"Background task error: {e}")
        
        thread = threading.Thread(target=background_worker, daemon=True)
        thread.start()
    
    def cleanup_temp_files(self):
        """Clean up temporary files"""
        temp_dirs = ["cache", "execution"]
        for temp_dir in temp_dirs:
            temp_path = self.base_path / temp_dir
            if temp_path.exists():
                for file in temp_path.glob("temp_*"):
                    if file.stat().st_mtime < time.time() - 3600:  # 1 hour old
                        file.unlink()
    
    def process_command(self, command: str) -> str:
        """Process user command"""
        try:
            return self.command_processor.process_command(command)
        except Exception as e:
            self.logger.error(f"Command processing error: {e}")
            return f"Error processing command: {str(e)}"
    
    def interactive_mode(self):
        """Run in interactive mode"""
        print("AI Coding Agent System - Interactive Mode")
        print("Type 'help' for available commands or 'exit' to quit")
        print("-" * 50)
        
        while True:
            try:
                command = input("Agent> ").strip()
                if command.lower() in ['exit', 'quit']:
                    break
                elif command:
                    response = self.process_command(command)
                    print(response)
                    print()
            except KeyboardInterrupt:
                print("\nShutting down...")
                break
        
        self.shutdown()
    
    def shutdown(self):
        """Graceful shutdown"""
        self.running = False
        self.memory.save_memories()
        self.logger.info("AI Agent System shut down")

def main():
    """Main entry point"""
    print("Initializing AI Coding Agent System...")
    
    # Load configuration
    config = SystemConfig()
    
    # Initialize agent
    agent = AIAgent(config)
    
    # Check if running with command line arguments
    if len(sys.argv) > 1:
        command = ' '.join(sys.argv[1:])
        response = agent.process_command(command)
        print(response)
    else:
        # Run in interactive mode
        agent.interactive_mode()

if __name__ == "__main__":
    main()
