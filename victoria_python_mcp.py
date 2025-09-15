#!/usr/bin/env python3
"""
Victoria Python MCP Server
A Model Context Protocol server for Python execution with virtual environment management.
Allows AI agents to create, manage, and execute code in isolated Python environments.
"""

import argparse
import asyncio
import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Victoria Python MCP Server")

# Global configuration
DEFAULT_VENV_PATH = Path.home() / "Victoria" / "venvs" / "adtech"
DEFAULT_WORKSPACE = Path.home() / "Victoria" / "workspace"

class VirtualEnvironmentManager:
    """Manages Python virtual environments for AI agents."""
    
    def __init__(self, venv_path: Path):
        self.venv_path = Path(venv_path)
        self.python_executable = self.venv_path / "bin" / "python"
        self.pip_executable = self.venv_path / "bin" / "pip"
        
        # Windows compatibility
        if sys.platform == "win32":
            self.python_executable = self.venv_path / "Scripts" / "python.exe"
            self.pip_executable = self.venv_path / "Scripts" / "pip.exe"
    
    async def ensure_venv_exists(self) -> bool:
        """Ensure virtual environment exists, create if it doesn't."""
        if self.venv_path.exists() and self.python_executable.exists():
            return True
        
        try:
            # Create parent directories
            self.venv_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create virtual environment
            result = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "venv", str(self.venv_path),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode != 0:
                logger.error(f"Failed to create venv: {stderr.decode()}")
                return False
            
            # Install essential packages
            essential_packages = [
                "pandas", "numpy", "matplotlib", "seaborn", "plotly",
                "openpyxl", "xlsxwriter", "xlrd", "scikit-learn", 
                "scipy", "statsmodels", "jupyter", "ipython",
                "requests", "beautifulsoup4"
            ]
            
            for package in essential_packages:
                await self.install_package(package)
            
            logger.info(f"Virtual environment created at {self.venv_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating virtual environment: {e}")
            return False
    
    async def install_package(self, package: str, dev: bool = False) -> Dict[str, Any]:
        """Install a package in the virtual environment."""
        await self.ensure_venv_exists()
        
        try:
            cmd = [str(self.pip_executable), "install", package]
            if dev:
                cmd.append("--dev")
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            return {
                "success": result.returncode == 0,
                "package": package,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "returncode": result.returncode
            }
            
        except Exception as e:
            return {
                "success": False,
                "package": package,
                "error": str(e)
            }
    
    async def uninstall_package(self, package: str) -> Dict[str, Any]:
        """Uninstall a package from the virtual environment."""
        await self.ensure_venv_exists()
        
        try:
            result = await asyncio.create_subprocess_exec(
                str(self.pip_executable), "uninstall", "-y", package,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            return {
                "success": result.returncode == 0,
                "package": package,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "returncode": result.returncode
            }
            
        except Exception as e:
            return {
                "success": False,
                "package": package,
                "error": str(e)
            }
    
    async def list_packages(self) -> Dict[str, Any]:
        """List installed packages in the virtual environment."""
        await self.ensure_venv_exists()
        
        try:
            result = await asyncio.create_subprocess_exec(
                str(self.pip_executable), "list", "--format=json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            
            if result.returncode == 0:
                import json
                packages = json.loads(stdout.decode())
                return {
                    "success": True,
                    "packages": packages
                }
            else:
                return {
                    "success": False,
                    "error": stderr.decode()
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def execute_python(self, code: str, working_dir: Optional[str] = None) -> Dict[str, Any]:
        """Execute Python code in the virtual environment."""
        await self.ensure_venv_exists()
        
        # Create temporary file for the code
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Set working directory
            cwd = working_dir or str(DEFAULT_WORKSPACE)
            Path(cwd).mkdir(parents=True, exist_ok=True)
            
            # Execute the code
            result = await asyncio.create_subprocess_exec(
                str(self.python_executable), temp_file,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            stdout, stderr = await result.communicate()
            
            return {
                "success": result.returncode == 0,
                "stdout": stdout.decode(),
                "stderr": stderr.decode(),
                "returncode": result.returncode,
                "working_directory": cwd
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_file)
            except:
                pass

# Initialize virtual environment manager
venv_manager = VirtualEnvironmentManager(DEFAULT_VENV_PATH)

@mcp.tool()
async def python_execute(code: str, working_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute Python code in the managed virtual environment.
    
    Args:
        code: Python code to execute
        working_dir: Optional working directory for execution
    
    Returns:
        Dictionary with execution results including stdout, stderr, and success status
    """
    return await venv_manager.execute_python(code, working_dir)

@mcp.tool()
async def python_install_package(package: str, dev: bool = False) -> Dict[str, Any]:
    """
    Install a Python package in the virtual environment.
    
    Args:
        package: Package name to install (e.g., 'pandas', 'numpy==1.21.0')
        dev: Whether to install as development dependency
    
    Returns:
        Dictionary with installation results
    """
    return await venv_manager.install_package(package, dev)

@mcp.tool()
async def python_uninstall_package(package: str) -> Dict[str, Any]:
    """
    Uninstall a Python package from the virtual environment.
    
    Args:
        package: Package name to uninstall
    
    Returns:
        Dictionary with uninstallation results
    """
    return await venv_manager.uninstall_package(package)

@mcp.tool()
async def python_list_packages() -> Dict[str, Any]:
    """
    List all installed packages in the virtual environment.
    
    Returns:
        Dictionary with list of installed packages
    """
    return await venv_manager.list_packages()

@mcp.tool()
async def python_create_script(filename: str, code: str, working_dir: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a Python script file in the workspace.
    
    Args:
        filename: Name of the script file (should end with .py)
        code: Python code content
        working_dir: Optional directory to create the script in
    
    Returns:
        Dictionary with creation results
    """
    try:
        # Set working directory
        cwd = Path(working_dir) if working_dir else DEFAULT_WORKSPACE
        cwd.mkdir(parents=True, exist_ok=True)
        
        # Create the script file
        script_path = cwd / filename
        script_path.write_text(code)
        
        return {
            "success": True,
            "filename": filename,
            "path": str(script_path),
            "working_directory": str(cwd)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def python_run_script(filename: str, working_dir: Optional[str] = None, args: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Run a Python script file in the virtual environment.
    
    Args:
        filename: Name of the script file to run
        working_dir: Optional directory containing the script
        args: Optional command line arguments for the script
    
    Returns:
        Dictionary with execution results
    """
    await venv_manager.ensure_venv_exists()
    
    try:
        # Set working directory
        cwd = Path(working_dir) if working_dir else DEFAULT_WORKSPACE
        script_path = cwd / filename
        
        if not script_path.exists():
            return {
                "success": False,
                "error": f"Script file {filename} not found in {cwd}"
            }
        
        # Build command
        cmd = [str(venv_manager.python_executable), str(script_path)]
        if args:
            cmd.extend(args)
        
        # Execute the script
        result = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(cwd)
        )
        stdout, stderr = await result.communicate()
        
        return {
            "success": result.returncode == 0,
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "returncode": result.returncode,
            "script_path": str(script_path)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@mcp.tool()
async def python_get_environment_info() -> Dict[str, Any]:
    """
    Get information about the Python virtual environment.
    
    Returns:
        Dictionary with environment information
    """
    await venv_manager.ensure_venv_exists()
    
    try:
        # Get Python version
        result = await asyncio.create_subprocess_exec(
            str(venv_manager.python_executable), "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await result.communicate()
        python_version = stdout.decode().strip()
        
        # Get pip version
        result = await asyncio.create_subprocess_exec(
            str(venv_manager.pip_executable), "--version",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await result.communicate()
        pip_version = stdout.decode().strip()
        
        return {
            "success": True,
            "venv_path": str(venv_manager.venv_path),
            "python_executable": str(venv_manager.python_executable),
            "pip_executable": str(venv_manager.pip_executable),
            "python_version": python_version,
            "pip_version": pip_version,
            "workspace": str(DEFAULT_WORKSPACE)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def main():
    """Main entry point for the MCP server."""
    parser = argparse.ArgumentParser(description="Victoria Python MCP Server")
    parser.add_argument("--venv-path", type=str, default=str(DEFAULT_VENV_PATH),
                       help="Path to the virtual environment")
    parser.add_argument("--workspace", type=str, default=str(DEFAULT_WORKSPACE),
                       help="Path to the workspace directory")
    
    args = parser.parse_args()
    
    # Update global configuration
    global venv_manager, DEFAULT_WORKSPACE
    venv_manager = VirtualEnvironmentManager(Path(args.venv_path))
    DEFAULT_WORKSPACE = Path(args.workspace)
    
    # Run the server
    mcp.run()

if __name__ == "__main__":
    main()

