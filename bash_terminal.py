"""
Bash Terminal Module - Real Shell Execution
Provides secure bash terminal interface for testing and deployment
"""

import subprocess
import os
import json
import logging
import time
import signal
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import tempfile
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BashTerminal:
    """
    Real bash terminal with shell execution capabilities.
    Provides secure command execution with safety measures.
    """
    
    # Whitelist of allowed commands
    ALLOWED_COMMANDS = {
        # File operations
        'ls', 'cd', 'pwd', 'cat', 'head', 'tail', 'grep', 'find', 'wc',
        # File manipulation
        'cp', 'mv', 'rm', 'mkdir', 'rmdir', 'touch', 'chmod', 'chown',
        # Text processing
        'sed', 'awk', 'sort', 'uniq', 'cut', 'tr',
        # System info
        'ps', 'top', 'df', 'du', 'free', 'uname', 'whoami', 'date',
        # Network
        'ping', 'curl', 'wget', 'nslookup', 'dig', 'netstat',
        # Development
        'git', 'python', 'python3', 'pip', 'pip3', 'npm', 'node',
        'docker', 'docker-compose',
        # Testing
        'pytest', 'unittest', 'coverage',
        # Deployment
        'rsync', 'scp', 'ssh',
        # Archive
        'tar', 'zip', 'unzip', 'gzip',
        # Other safe commands
        'echo', 'printf', 'history', 'clear', 'exit'
    }
    
    # Blacklisted commands (never allowed)
    BLACKLISTED_COMMANDS = {
        'rm', 'rmdir', 'dd', 'mkfs', 'fdisk', 'format',
        'sudo', 'su', 'passwd', 'chroot',
        'reboot', 'shutdown', 'halt', 'poweroff',
        'systemctl', 'service', 'init'
    }
    
    def __init__(self, working_dir: str = None, timeout: int = 30):
        """
        Initialize bash terminal.
        
        Args:
            working_dir: Working directory for terminal
            timeout: Command execution timeout in seconds
        """
        self.working_dir = working_dir or os.getcwd()
        self.timeout = timeout
        self.history = []
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.env = os.environ.copy()
        
        # Set safe environment
        self.env['PATH'] = '/usr/local/bin:/usr/bin:/bin'
        self.env['TERM'] = 'xterm-256color'
        
        logger.info(f"Terminal session {self.session_id} initialized in {self.working_dir}")
    
    def execute_command(
        self,
        command: str,
        capture_output: bool = True,
        timeout: int = None
    ) -> Dict[str, any]:
        """
        Execute a bash command safely.
        
        Args:
            command: Command to execute
            capture_output: Whether to capture stdout/stderr
            timeout: Override default timeout
        
        Returns:
            Dictionary with execution results
        """
        # Validate command
        validation = self._validate_command(command)
        if not validation['valid']:
            return {
                'success': False,
                'error': validation['error'],
                'command': command
            }
        
        # Set timeout
        cmd_timeout = timeout or self.timeout
        
        try:
            # Execute command
            start_time = time.time()
            
            if capture_output:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.working_dir,
                    env=self.env,
                    capture_output=True,
                    text=True,
                    timeout=cmd_timeout,
                    executable='/bin/bash'
                )
                
                execution_time = time.time() - start_time
                
                # Add to history
                self.history.append({
                    'command': command,
                    'return_code': result.returncode,
                    'execution_time': execution_time,
                    'timestamp': datetime.now().isoformat()
                })
                
                return {
                    'success': result.returncode == 0,
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode,
                    'execution_time': execution_time,
                    'command': command
                }
            else:
                # Interactive mode (not recommended for web)
                subprocess.run(
                    command,
                    shell=True,
                    cwd=self.working_dir,
                    env=self.env,
                    timeout=cmd_timeout,
                    executable='/bin/bash'
                )
                
                return {
                    'success': True,
                    'command': command,
                    'message': 'Command executed (interactive mode)'
                }
                
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': f'Command timed out after {cmd_timeout} seconds',
                'command': command
            }
        except subprocess.CalledProcessError as e:
            return {
                'success': False,
                'error': str(e),
                'return_code': e.returncode,
                'command': command
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'command': command
            }
    
    def _validate_command(self, command: str) -> Dict[str, any]:
        """
        Validate command for safety.
        
        Args:
            command: Command to validate
        
        Returns:
            Validation result
        """
        # Check for empty command
        if not command or not command.strip():
            return {'valid': False, 'error': 'Empty command'}
        
        # Get base command
        base_command = command.split()[0].strip()
        
        # Check for blacklisted commands
        if base_command in self.BLACKLISTED_COMMANDS:
            return {'valid': False, 'error': f'Command {base_command} is not allowed'}
        
        # Check for dangerous patterns
        dangerous_patterns = [
            'rm -rf /',
            'rm -rf /*',
            'dd if=',
            ':(){:|:&};:',
            'chmod 777',
            'chown root',
            'sudo',
            'su ',
            'passwd',
            'reboot',
            'shutdown',
            'mkfs',
            'fdisk',
            'format',
            'del /f',
            'format c:',
            '> /dev/sd',
            'dd of=/dev/sd'
        ]
        
        for pattern in dangerous_patterns:
            if pattern in command.lower():
                return {'valid': False, 'error': f'Dangerous pattern detected: {pattern}'}
        
        # Check for command chaining with dangerous commands
        if '&&' in command or ';' in command or '|' in command:
            parts = command.replace('&&', ';').replace('|', ';').split(';')
            for part in parts:
                part = part.strip()
                if part:
                    base = part.split()[0].strip()
                    if base in self.BLACKLISTED_COMMANDS:
                        return {'valid': False, 'error': f'Chained command {base} is not allowed'}
        
        # If whitelist is enforced, check against it
        if base_command not in self.ALLOWED_COMMANDS:
            # For now, allow unknown commands but log warning
            logger.warning(f"Command {base_command} not in whitelist, allowing with caution")
        
        return {'valid': True}
    
    def execute_script(
        self,
        script_content: str,
        script_name: str = None
    ) -> Dict[str, any]:
        """
        Execute a bash script.
        
        Args:
            script_content: Script content to execute
            script_name: Optional script name
        
        Returns:
            Execution result
        """
        # Create temporary script file
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.sh',
            prefix='terminal_script_',
            delete=False
        ) as f:
            script_path = f.name
            f.write(script_content)
            f.write('\n')
        
        try:
            # Make script executable
            os.chmod(script_path, 0o755)
            
            # Execute script
            result = self.execute_command(f'bash {script_path}')
            
            return result
            
        finally:
            # Clean up
            try:
                os.unlink(script_path)
            except:
                pass
    
    def get_working_directory(self) -> str:
        """Get current working directory."""
        return self.working_dir
    
    def change_directory(self, path: str) -> Dict[str, any]:
        """
        Change working directory.
        
        Args:
            path: New directory path
        
        Returns:
            Result of directory change
        """
        try:
            # Resolve path
            new_path = os.path.abspath(os.path.join(self.working_dir, path))
            
            # Check if directory exists
            if not os.path.exists(new_path):
                return {'success': False, 'error': f'Directory does not exist: {new_path}'}
            
            if not os.path.isdir(new_path):
                return {'success': False, 'error': f'Not a directory: {new_path}'}
            
            # Change directory
            self.working_dir = new_path
            
            return {
                'success': True,
                'working_directory': self.working_dir
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def list_directory(self, path: str = None) -> Dict[str, any]:
        """
        List directory contents.
        
        Args:
            path: Path to list (default: current directory)
        
        Returns:
            Directory listing
        """
        try:
            list_path = path or self.working_dir
            result = self.execute_command(f'ls -la {list_path}')
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_file_info(self, path: str) -> Dict[str, any]:
        """
        Get file information.
        
        Args:
            path: File path
        
        Returns:
            File information
        """
        try:
            full_path = os.path.join(self.working_dir, path)
            
            if not os.path.exists(full_path):
                return {'success': False, 'error': f'File does not exist: {path}'}
            
            stat_info = os.stat(full_path)
            
            return {
                'success': True,
                'path': full_path,
                'size': stat_info.st_size,
                'modified': datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
                'is_file': os.path.isfile(full_path),
                'is_dir': os.path.isdir(full_path),
                'permissions': oct(stat_info.st_mode)[-3:]
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def read_file(self, path: str, max_lines: int = 100) -> Dict[str, any]:
        """
        Read file contents.
        
        Args:
            path: File path
            max_lines: Maximum lines to read
        
        Returns:
            File contents
        """
        try:
            full_path = os.path.join(self.working_dir, path)
            
            if not os.path.exists(full_path):
                return {'success': False, 'error': f'File does not exist: {path}'}
            
            if not os.path.isfile(full_path):
                return {'success': False, 'error': f'Not a file: {path}'}
            
            # Check file size (limit to 1MB)
            file_size = os.path.getsize(full_path)
            if file_size > 1024 * 1024:
                return {'success': False, 'error': f'File too large: {file_size} bytes'}
            
            with open(full_path, 'r') as f:
                lines = f.readlines()
            
            # Limit lines
            if max_lines:
                lines = lines[:max_lines]
            
            return {
                'success': True,
                'path': full_path,
                'content': ''.join(lines),
                'lines_read': len(lines),
                'total_lines': len(lines) if not max_lines else len(lines)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def write_file(
        self,
        path: str,
        content: str,
        overwrite: bool = False
    ) -> Dict[str, any]:
        """
        Write content to file.
        
        Args:
            path: File path
            content: Content to write
            overwrite: Whether to overwrite existing file
        
        Returns:
            Write result
        """
        try:
            full_path = os.path.join(self.working_dir, path)
            
            # Check if file exists
            if os.path.exists(full_path) and not overwrite:
                return {'success': False, 'error': f'File already exists: {path} (use overwrite=True)'}
            
            # Write file
            with open(full_path, 'w') as f:
                f.write(content)
            
            return {
                'success': True,
                'path': full_path,
                'bytes_written': len(content)
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """
        Get command history.
        
        Args:
            limit: Maximum number of history entries
        
        Returns:
            Command history
        """
        return self.history[-limit:]
    
    def clear_history(self) -> Dict[str, any]:
        """Clear command history."""
        self.history = []
        return {'success': True, 'message': 'History cleared'}
    
    def get_system_info(self) -> Dict[str, any]:
        """Get system information."""
        info = {}
        
        try:
            # OS info
            info['os'] = os.uname().sysname
            info['hostname'] = os.uname().nodename
            info['release'] = os.uname().release
            info['version'] = os.uname().version
            info['machine'] = os.uname().machine
            
            # Current user
            info['user'] = os.getenv('USER', os.getenv('USERNAME', 'unknown'))
            
            # Working directory
            info['working_directory'] = self.working_dir
            
            # Python version
            info['python_version'] = os.sys.version
            
            # Disk usage
            disk = self.execute_command('df -h .')
            info['disk_usage'] = disk.get('stdout', '') if disk.get('success') else 'N/A'
            
            # Memory
            mem = self.execute_command('free -h')
            info['memory'] = mem.get('stdout', '') if mem.get('success') else 'N/A'
            
            return {'success': True, 'info': info}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_test_suite(self, test_type: str = "all") -> Dict[str, any]:
        """
        Run test suite for the application.
        
        Args:
            test_type: Type of tests to run (all, unit, integration)
        
        Returns:
            Test results
        """
        try:
            if test_type == "all":
                command = "python -m pytest tests/ -v --tb=short"
            elif test_type == "unit":
                command = "python -m pytest tests/unit/ -v --tb=short"
            elif test_type == "integration":
                command = "python -m pytest tests/integration/ -v --tb=short"
            else:
                return {'success': False, 'error': f'Unknown test type: {test_type}'}
            
            result = self.execute_command(command, timeout=120)
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def deploy_application(
        self,
        environment: str = "production",
        platform: str = "huggingface"
    ) -> Dict[str, any]:
        """
        Deploy application to specified platform.
        
        Args:
            environment: Deployment environment
            platform: Deployment platform (huggingface, github, vercel)
        
        Returns:
            Deployment result
        """
        try:
            if platform == "huggingface":
                # Deploy to Hugging Face Spaces
                commands = [
                    "git add .",
                    "git commit -m 'Deploy to Hugging Face'",
                    "git push huggingface main"
                ]
                
                results = []
                for cmd in commands:
                    result = self.execute_command(cmd)
                    results.append(result)
                    if not result.get('success'):
                        return {
                            'success': False,
                            'error': f'Deployment failed at: {cmd}',
                            'results': results
                        }
                
                return {
                    'success': True,
                    'environment': environment,
                    'platform': platform,
                    'results': results
                }
            
            elif platform == "github":
                # Deploy to GitHub
                commands = [
                    "git add .",
                    "git commit -m 'Deploy to GitHub'",
                    "git push origin main"
                ]
                
                results = []
                for cmd in commands:
                    result = self.execute_command(cmd)
                    results.append(result)
                    if not result.get('success'):
                        return {
                            'success': False,
                            'error': f'Deployment failed at: {cmd}',
                            'results': results
                        }
                
                return {
                    'success': True,
                    'environment': environment,
                    'platform': platform,
                    'results': results
                }
            
            else:
                return {'success': False, 'error': f'Unknown platform: {platform}'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def install_dependencies(self, requirements_file: str = "requirements.txt") -> Dict[str, any]:
        """
        Install Python dependencies.
        
        Args:
            requirements_file: Path to requirements file
        
        Returns:
            Installation result
        """
        try:
            if not os.path.exists(requirements_file):
                return {'success': False, 'error': f'Requirements file not found: {requirements_file}'}
            
            command = f"pip install -r {requirements_file}"
            result = self.execute_command(command, timeout=300)
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_linter(self, path: str = ".") -> Dict[str, any]:
        """
        Run code linter.
        
        Args:
            path: Path to lint
        
        Returns:
            Linting results
        """
        try:
            # Try flake8 first
            result = self.execute_command(f"flake8 {path} --max-line-length=100")
            
            if result.get('success') and not result.get('stdout'):
                return {'success': True, 'message': 'No linting issues found'}
            
            return result
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def run_formatter(self, path: str = ".") -> Dict[str, any]:
        """
        Run code formatter (black).
        
        Args:
            path: Path to format
        
        Returns:
        Formatting result
        """
        try:
            result = self.execute_command(f"black {path}")
            return result
        except Exception as e:
            return {'success': False, 'error': str(e)}


class TerminalSession:
    """
    Manages terminal sessions with isolation.
    """
    
    def __init__(self):
        self.sessions = {}
    
    def create_session(
        self,
        session_id: str = None,
        working_dir: str = None
    ) -> BashTerminal:
        """Create a new terminal session."""
        if session_id is None:
            session_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        
        terminal = BashTerminal(working_dir=working_dir)
        self.sessions[session_id] = terminal
        
        logger.info(f"Created terminal session: {session_id}")
        return terminal
    
    def get_session(self, session_id: str) -> Optional[BashTerminal]:
        """Get existing terminal session."""
        return self.sessions.get(session_id)
    
    def close_session(self, session_id: str) -> bool:
        """Close terminal session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Closed terminal session: {session_id}")
            return True
        return False
    
    def list_sessions(self) -> List[str]:
        """List all active sessions."""
        return list(self.sessions.keys())


# Global session manager
session_manager = TerminalSession()


# Export
__all__ = [
    'BashTerminal',
    'TerminalSession',
    'session_manager'
]
