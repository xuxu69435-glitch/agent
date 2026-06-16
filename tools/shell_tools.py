import subprocess



from .command_policy import truncate_output, validate_command

from .sandbox import require_workspace, resolve_safe



COMMAND_TIMEOUT_SECONDS = 60





def run_command(command: str, cwd: str = ".") -> str:

    """在工作区内执行受限命令（白名单 + 无 shell）。"""

    try:

        workspace_root = require_workspace()

    except RuntimeError as exc:

        return f"错误：{exc}"



    try:

        work_dir = resolve_safe(cwd)

    except PermissionError as exc:

        return f"错误：{exc}"



    argv, error = validate_command(command, work_dir, workspace_root)

    if error:

        return f"错误：{error}"



    try:

        result = subprocess.run(

            argv,

            shell=False,

            cwd=work_dir,

            capture_output=True,

            text=True,

            timeout=COMMAND_TIMEOUT_SECONDS,

        )

        output = (result.stdout + result.stderr).strip() or "（无输出）"

        output = truncate_output(output)

        return f"退出码: {result.returncode}\n{output}"

    except subprocess.TimeoutExpired:

        return f"错误：命令执行超时（{COMMAND_TIMEOUT_SECONDS}秒）"

    except FileNotFoundError:

        return f"错误：未找到命令 - {argv[0]}"

    except Exception as exc:

        return f"错误：{exc}"





SCHEMAS = [

    {

        "type": "function",

        "function": {

            "name": "run_command",

            "description": (

                "在工作区内执行受限命令。"

                "仅支持白名单内可执行文件（如 pytest、python、npm、cargo、go 等），"

                "禁止使用 shell 操作符（; | & > < 等）。"

            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "command": {

                        "type": "string",

                        "description": "要执行的命令，例如 pytest 或 python -m pytest",

                    },

                    "cwd": {"type": "string", "description": "工作目录，相对于工作区根"},

                },

                "required": ["command"],

            },

        },

    },

]



HANDLERS = {

    "run_command": run_command,

}

