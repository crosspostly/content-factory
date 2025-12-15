#!/usr/bin/env python3
"""
File Manager for AI Agent Code Changes

This script provides utilities for the AI agent to:
- Read files from the repository
- Write/modify files in the PR branch  
- Validate file changes
- Report on modifications

Used by: GitHub Actions workflow + Gemini CLI agent
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class FileManager:
    """Manages file operations for AI agent modifications"""

    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root).absolute()
        self.changes: Dict[str, Dict] = {}

    def read_file(self, path: str) -> str:
        """Read a file and return its content"""
        file_path = self._get_safe_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def write_file(self, path: str, content: str) -> Dict:
        """Write or create a file with content"""
        file_path = self._get_safe_path(path)
        
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if file exists to track as modification or creation
        is_new = not file_path.exists()
        
        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Track change
        self.changes[path] = {
            'type': 'created' if is_new else 'modified',
            'path': path,
            'status': 'success'
        }
        
        return {'status': 'success', 'path': path, 'is_new': is_new}

    def modify_file(self, path: str, replacements: List[Dict]) -> Dict:
        """
        Modify a file by replacing specific sections.
        
        replacements: [
            {
                'find': 'text to find',
                'replace': 'replacement text',
                'count': 1  # how many occurrences to replace (0 = all)
            }
        ]
        """
        file_path = self._get_safe_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        content = self.read_file(path)
        original_content = content
        
        for replacement in replacements:
            find = replacement['find']
            replace = replacement['replace']
            count = replacement.get('count', 1)
            
            if count == 0:
                content = content.replace(find, replace)
            else:
                content = content.replace(find, replace, count)
        
        # Check if anything changed
        if content == original_content:
            return {
                'status': 'no_changes',
                'path': path,
                'message': 'No text matched for replacement'
            }
        
        # Write modified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.changes[path] = {
            'type': 'modified',
            'path': path,
            'status': 'success'
        }
        
        return {'status': 'success', 'path': path, 'changes_count': len(replacements)}

    def append_to_file(self, path: str, content: str) -> Dict:
        """Append content to the end of a file"""
        file_path = self._get_safe_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write(content)
        
        self.changes[path] = {
            'type': 'modified',
            'path': path,
            'status': 'success'
        }
        
        return {'status': 'success', 'path': path}

    def get_file_section(self, path: str, start_line: int, end_line: int) -> str:
        """Get a specific section of a file (by line numbers)"""
        content = self.read_file(path)
        lines = content.split('\n')
        
        # Convert to 0-based indexing
        section = lines[start_line-1:end_line]
        return '\n'.join(section)

    def replace_in_section(self, path: str, start_line: int, end_line: int, new_content: str) -> Dict:
        """Replace a section of a file with new content"""
        content = self.read_file(path)
        lines = content.split('\n')
        
        # Build new content
        new_lines = (
            lines[:start_line-1] +
            new_content.split('\n') +
            lines[end_line:]
        )
        
        new_content_str = '\n'.join(new_lines)
        
        # Write back
        with open(self._get_safe_path(path), 'w', encoding='utf-8') as f:
            f.write(new_content_str)
        
        self.changes[path] = {
            'type': 'modified',
            'path': path,
            'status': 'success'
        }
        
        return {'status': 'success', 'path': path}

    def list_changes(self) -> Dict:
        """Return summary of all changes made"""
        return {
            'total_changes': len(self.changes),
            'created': sum(1 for c in self.changes.values() if c['type'] == 'created'),
            'modified': sum(1 for c in self.changes.values() if c['type'] == 'modified'),
            'files': list(self.changes.keys()),
            'details': self.changes
        }

    def validate_python_file(self, path: str) -> Tuple[bool, Optional[str]]:
        """Validate that a Python file has correct syntax"""
        try:
            import ast
            content = self.read_file(path)
            ast.parse(content)
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {e.msg} at line {e.lineno}"

    def _get_safe_path(self, path: str) -> Path:
        """Get a safe absolute path (prevent directory traversal)"""
        # Normalize path
        path = path.lstrip('./')
        
        # Get absolute path
        file_path = (self.repo_root / path).resolve()
        
        # Verify it's within repo
        try:
            file_path.relative_to(self.repo_root)
        except ValueError:
            raise ValueError(f"Path {path} is outside repository root")
        
        return file_path

    def save_changes_manifest(self, output_file: str = '/tmp/ai_changes_manifest.json'):
        """Save a manifest of all changes made"""
        manifest = {
            'timestamp': str(Path(__file__).stat().st_mtime),
            'changes_summary': self.list_changes(),
            'files': {}
        }
        
        # Add file details
        for path in self.changes.keys():
            file_path = self._get_safe_path(path)
            if file_path.exists():
                with open(file_path, 'r') as f:
                    content = f.read()
                manifest['files'][path] = {
                    'size': len(content),
                    'lines': len(content.split('\n')),
                    'type': self.changes[path]['type']
                }
        
        with open(output_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return output_file


def main():
    """CLI interface for file manager"""
    if len(sys.argv) < 2:
        print("Usage: file-manager.py <command> [args]")
        print("Commands:")
        print("  read <path>")
        print("  write <path> <content>")
        print("  validate <path>")
        print("  manifest")
        sys.exit(1)
    
    fm = FileManager()
    command = sys.argv[1]
    
    try:
        if command == 'read' and len(sys.argv) > 2:
            path = sys.argv[2]
            content = fm.read_file(path)
            print(content)
        
        elif command == 'write' and len(sys.argv) > 3:
            path = sys.argv[2]
            content = sys.argv[3]
            result = fm.write_file(path, content)
            print(json.dumps(result))
        
        elif command == 'validate' and len(sys.argv) > 2:
            path = sys.argv[2]
            is_valid, error = fm.validate_python_file(path)
            result = {
                'path': path,
                'valid': is_valid,
                'error': error
            }
            print(json.dumps(result))
        
        elif command == 'manifest':
            fm.save_changes_manifest()
            print(json.dumps(fm.list_changes()))
        
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
    
    except Exception as e:
        print(json.dumps({
            'status': 'error',
            'error': str(e)
        }), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
