import os
import subprocess
from typing import Dict, Optional, Tuple

RunCmdResult = Tuple[str, str, int]


def is_command_available(command: str) -> bool:
    cmd_check = f"command -v {command} >/dev/null 2>&1"
    result_code = os.system(cmd_check)
    return result_code == 0


def run_simple_cmd(command: str) -> None:
    print(command)

    command = 'source ~/.bashrc; ' + command
    subprocess.call(['/bin/bash', '-c', command])


def run_cmd(command: str,
            timeout: Optional[int] = None,
            discard_output: bool = False,
            cwd: Optional[str] = None,
            env: Optional[Dict[str, str]] = None) -> RunCmdResult:
    print(command)

    command = 'source ~/.bashrc; ' + command
    env_str = ""
    if env is not None and len(env) > 0:
        env_str = "env "
        for key, value in env.items():
            env_str += f"{key}={value} "

    if discard_output:
        output_file = subprocess.DEVNULL
    else:
        output_file = subprocess.PIPE

    command_with_env = f"{env_str}{command}"
    process = subprocess.run(['/bin/bash', '-c', command_with_env], stdout=output_file, stderr=output_file,
                             timeout=timeout, encoding="utf-8", cwd=cwd)

    return process.stdout, process.stderr, process.returncode
