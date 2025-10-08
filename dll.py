# -*- coding: utf-8 -*-
"""
dll.py
- 提供 DLLFunctionRegistry 類別，集中管理「以 Python 定義、可當作 DLL 入口使用」的函式。
- 提供預設的 default_registry 與便捷 decorator：@dllfunc("name")
- 內建示範函式：dll1、dll2（載入本模組時即註冊到 default_registry）
"""

import ctypes
import threading
from typing import Callable, Dict, Optional, Iterable


# 以 Python 函式模擬 DLL 入口的標準介面簽名
# 簽名：(in_ptr, out_ptr) -> int，兩者皆為指向「值類型」的 ctypes 指標，
# 實務上 main.py 會以 pointer(node_value_ctype) 傳入。
DLLFunction = Callable[[ctypes.c_void_p, ctypes.c_void_p], int]


class DLLFunctionRegistry:
    """
    管理以 Python 定義的「DLL 入口」函式：
      - register(name, func): 註冊
      - get(name): 取得 callable
      - has(name): 是否存在
      - names(): 目前所有名稱
    可搭配 decorator 使用，見下方 dllfunc()。
    """
    def __init__(self):
        self._funcs: Dict[str, DLLFunction] = {}
        self._lock = threading.RLock()

    def register(self, name: str, func: DLLFunction) -> DLLFunction:
        if not callable(func):
            raise TypeError(f"func for '{name}' must be callable")
        with self._lock:
            self._funcs[name] = func
        return func  # 便於 decorator 直接回傳

    def get(self, name: str) -> DLLFunction:
        with self._lock:
            if name not in self._funcs:
                raise KeyError(f"Registry 中找不到函式: '{name}'")
            return self._funcs[name]

    def has(self, name: str) -> bool:
        with self._lock:
            return name in self._funcs

    def names(self) -> Iterable[str]:
        with self._lock:
            return tuple(self._funcs.keys())


# 預設全域 registry（大多數情境直接使用它即可）
default_registry = DLLFunctionRegistry()


def dllfunc(name: str, registry: DLLFunctionRegistry = default_registry):
    """
    裝飾器：將函式註冊到指定的 registry（預設為 default_registry）。
    用法：
        @dllfunc("dll1")
        def dll1(in_ptr, out_ptr) -> int: ...
    """
    def deco(f: DLLFunction) -> DLLFunction:
        return registry.register(name, f)
    return deco


# ============================================================================
# 內建示範函式：dll1 / dll2
# 注意：此處未假設特定值類型，只要 in_ptr / out_ptr 的 .contents.value 可讀寫即可。
# ============================================================================
@dllfunc("dll1")
def dll1(in_ptr, out_ptr) -> int:
    print("dll1")
    out_ptr.contents.value = in_ptr.contents.value
    return 0


@dllfunc("dll2")
def dll2(in_ptr, out_ptr) -> int:
    print("dll2")
    out_ptr.contents.value = in_ptr.contents.value
    return 0


__all__ = [
    "DLLFunctionRegistry",
    "default_registry",
    "dllfunc",
    "dll1",
    "dll2",
]
