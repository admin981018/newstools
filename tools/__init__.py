# tools/__init__.py
from typing import Callable, List, Tuple
import flet as ft

# 工具注册表：[(name, icon, page_builder)]
TOOL_REGISTRY: List[Tuple[str, str, Callable[[ft.Page], ft.Control]]] = []

def register_tool(name: str, icon: str, page_builder: Callable[[ft.Page], ft.Control]):
    """注册一个工具"""
    TOOL_REGISTRY.append((name, icon, page_builder))

def get_tools():
    return TOOL_REGISTRY