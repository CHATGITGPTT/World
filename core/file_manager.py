#!/usr/bin/env python3
"""
World File Manager
File management system for the World AI Agent System
"""

import os
import shutil
import tempfile
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

class WorldFileManager:
    """File management system for World"""

    def __init__(self, base_path: Path, logger: logging.Logger | None = None):
        self.base_path = Path(base_path)
        self.temp_dir = self.base_path / "temp"
        self.cache_dir = self.base_path / "cache"
        self.backup_dir = self.base_path / "backups"
        self.log = logger or logging.getLogger("file_manager")
        
        # Create directories
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def read_file(self, file_path: str) -> Optional[str]:
        """Read file content"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if not path.exists():
                return None
            
            # Check file size (10MB limit)
            if path.stat().st_size > 10 * 1024 * 1024:
                return None
            
            return path.read_text(encoding='utf-8')
        except Exception:
            self.log.exception("read_file failed: %s", file_path)
            return None
    
    def write_file(self, file_path: str, content: str, backup: bool = True) -> bool:
        """Write file content"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            # Create backup if file exists
            if backup and path.exists():
                self._create_backup(path)
            
            # Ensure parent directory exists
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content
            path.write_text(content, encoding='utf-8')
            return True
        except Exception:
            self.log.exception("write_file failed: %s", file_path)
            return False
    
    def delete_file(self, file_path: str) -> bool:
        """Delete file"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def list_files(self, directory: str = "", pattern: str = "*") -> List[Path]:
        """List files in directory"""
        try:
            if directory:
                dir_path = self.base_path / directory
            else:
                dir_path = self.base_path
            
            if not dir_path.exists():
                return []
            
            return list(dir_path.glob(pattern))
        except Exception:
            return []
    
    def scan_all_files(self) -> List[Path]:
        """Scan all files in the system"""
        files = []
        try:
            for root, dirs, filenames in os.walk(self.base_path):
                # Skip certain directories
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'node_modules']]
                
                for filename in filenames:
                    files.append(Path(root) / filename)
        except Exception:
            pass
        
        return files
    
    def _create_backup(self, file_path: Path):
        """Create backup of file"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.name}.{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            shutil.copy2(file_path, backup_path)
        except Exception:
            pass
    
    async def cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            current_time = datetime.now().timestamp()
            
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    # Delete files older than 1 hour
                    if current_time - file_path.stat().st_mtime > 3600:
                        file_path.unlink()
        except Exception:
            pass
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get file information"""
        try:
            path = Path(file_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            if not path.exists():
                return None
            
            stat = path.stat()
            return {
                "name": path.name,
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "extension": path.suffix,
                "is_file": path.is_file(),
                "is_dir": path.is_dir()
            }
        except Exception:
            return None
    
    def create_directory(self, dir_path: str) -> bool:
        """Create directory"""
        try:
            path = Path(dir_path)
            if not path.is_absolute():
                path = self.base_path / path
            
            path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False
    
    def copy_file(self, src: str, dst: str) -> bool:
        """Copy file"""
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.is_absolute():
                src_path = self.base_path / src_path
            
            if not dst_path.is_absolute():
                dst_path = self.base_path / dst_path
            
            shutil.copy2(src_path, dst_path)
            return True
        except Exception:
            return False
    
    def move_file(self, src: str, dst: str) -> bool:
        """Move file"""
        try:
            src_path = Path(src)
            dst_path = Path(dst)
            
            if not src_path.is_absolute():
                src_path = self.base_path / src_path
            
            if not dst_path.is_absolute():
                dst_path = self.base_path / dst_path
            
            shutil.move(str(src_path), str(dst_path))
            return True
        except Exception:
            return False
