# tools/__init__.py
import os
import importlib
from pathlib import Path

_REGISTERED_TOOLS = []

def register_tool(name, icon, builder):
    _REGISTERED_TOOLS.append((name, icon, builder))

def get_tools():
    if not _REGISTERED_TOOLS:
        _discover_tools()
    return _REGISTERED_TOOLS

def _discover_tools():
    """自动导入 tools/ 下所有 .py 模块并注册"""
    tools_dir = Path(__file__).parent
    for file in tools_dir.glob("*.py"):
        if file.name == "__init__.py":
            continue
        module_name = f"tools.{file.stem}"
        try:
            module = importlib.import_module(module_name)
            if (hasattr(module, 'TOOL_NAME') and
                hasattr(module, 'TOOL_ICON') and
                hasattr(module, 'build_ui')):
                register_tool(
                    getattr(module, 'TOOL_NAME'),
                    getattr(module, 'TOOL_ICON'),
                    getattr(module, 'build_ui')
                )
        except Exception as e:
            print(f"⚠️ 无法加载工具 {module_name}: {e}")