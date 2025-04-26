# 仕様メモ

## コールバック関数の例

```python
def custom_content_callback(module: str, func: str | None, pos: Literal["pre", "post"]) -> str:
    if pos == "pre":
        if func == "Function1":
            return "Function1 custom pre-content"
        elif not func:
            return f"{module} custom pre-content"
    elif pos == "post":
        if func == "Function1":
            return "Function1 custom post-content"
        elif not func:
            return f"{module} custom post-content"
    return ""
```
