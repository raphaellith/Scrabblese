from typing import Any


class Stack:
    def __init__(self):
        self._stack = []

    def push(self, item: Any):
        self._stack.append(item)

    def pop(self) -> Any:
        return self._stack.pop()

    def peek(self) -> Any:
        return self._stack[-1]

    def as_list(self) -> list:
        return self._stack[:]