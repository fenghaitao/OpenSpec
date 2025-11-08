"""Helper for running CLI commands in tests."""

import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Union
from dataclasses import dataclass


@dataclass
class RunCLIResult:
    """Result of running a CLI command."""
    exit_code: int
    stdout: str
    stderr: str
    command: str


class CLIRunner:
    """Helper for running OpenSpec CLI commands in tests."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        
    def run_cli(
        self,
        args: List[str],
        cwd: Optional[Union[str, Path]] = None,
        env: Optional[Dict[str, str]] = None,
        input_data: Optional[str] = None,
        timeout: float = 30.0
    ) -> RunCLIResult:
        """Run the OpenSpec CLI with given arguments."""
        
        # Use openspec command directly (assumes it's installed in development mode)
        cmd = ["openspec"] + args
        
        # Set up environment
        final_env = dict(os.environ) if env is None else {**os.environ, **env}
        final_env["OPENSPEC_NON_INTERACTIVE"] = "1"  # Disable interactive prompts
        
        # Set working directory
        if cwd is None:
            cwd = self.project_root
        elif isinstance(cwd, str):
            cwd = Path(cwd)
            
        try:
            result = subprocess.run(
                cmd,
                cwd=cwd,
                env=final_env,
                input=input_data,
                text=True,
                capture_output=True,
                timeout=timeout
            )
            
            return RunCLIResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                command=" ".join(cmd)
            )
            
        except subprocess.TimeoutExpired as e:
            return RunCLIResult(
                exit_code=-1,
                stdout=e.stdout or "",
                stderr=f"Command timed out after {timeout}s: {e.stderr or ''}",
                command=" ".join(cmd)
            )
        except Exception as e:
            return RunCLIResult(
                exit_code=-1,
                stdout="",
                stderr=f"Command failed: {str(e)}",
                command=" ".join(cmd)
            )