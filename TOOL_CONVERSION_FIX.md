# 工具转换修复说明

## 修复时间
2025-12-26

## 问题描述
当使用 `claude-haiku-4-5-20251001` 模型(映射到 `gemini-2.5-flash`)时,出现错误:
```
Multiple tools are supported only when they are all search tools.
```

## 根本原因

### 错误的转换方式 (修复前)
```python
# 每个工具创建一个独立的工具组
gemini_tools.append({
    "functionDeclarations": [
        {"name": name, "description": description, "parameters": parameters}
    ]
})
```

**结果**:
```json
[
  {"functionDeclarations": [{"name": "Glob"}]},
  {"functionDeclarations": [{"name": "Grep"}]},
  {"functionDeclarations": [{"name": "Read"}]},
  {"functionDeclarations": [{"name": "WebFetch"}]},
  {"functionDeclarations": [{"name": "WebSearch"}]}
]
```
❌ **5 个工具组** → 违反 Gemini API 限制!

### 正确的转换方式 (修复后)
```python
# 所有工具放在一个工具组的 functionDeclarations 数组中
all_function_declarations.append({
    "name": name,
    "description": description,
    "parameters": parameters,
})

return [{"functionDeclarations": all_function_declarations}]
```

**结果**:
```json
[
  {
    "functionDeclarations": [
      {"name": "Glob"},
      {"name": "Grep"},
      {"name": "Read"},
      {"name": "WebFetch"},
      {"name": "WebSearch"}
    ]
  }
]
```
✅ **1 个工具组,包含 5 个函数** → 符合 Gemini API 规范!

## 修改的文件

### src/anthropic_converter.py
- **函数**: `convert_tools()` (第 225-258 行)
- **修改内容**: 将所有函数声明合并到一个 `functionDeclarations` 数组中

## 测试验证

### 单元测试
```bash
python3 test_tool_conversion.py
```

**测试结果**:
```
✅ 正确: 所有工具合并到一个工具组中
✅ 工具组包含 5 个函数声明
✅ 所有工具都被正确转换
```

### 实际 API 测试
重启服务后,使用 Claude Code CLI 发送请求:
```bash
# 重启服务 (uvicorn 会自动检测文件变化)
# 或手动重启:
unset ALL_PROXY all_proxy && uvicorn web:app --reload --host 0.0.0.0 --port 7861
```

## 预期效果

### 修复前
```
[ANTIGRAVITY] API error (400): {
  "error": {
    "code": 400,
    "message": "Multiple tools are supported only when they are all search tools.",
    "status": "INVALID_ARGUMENT"
  }
}
```

### 修复后
```
[ANTIGRAVITY] Request successful with credential: ag_main-spring-qpvm6-1766469473.json
```

## 影响范围

### 受益的场景
1. ✅ Claude Haiku → Gemini Flash (多工具调用)
2. ✅ Claude Code CLI 使用 (默认传递所有工具)
3. ✅ 任何包含 2+ 个工具的 Anthropic 格式请求

### 不受影响的场景
1. ✅ Claude Sonnet/Opus → Claude API (本来就支持多工具)
2. ✅ 单工具请求 (无论什么模型)

## 技术细节

### Gemini API 规范
根据 [Google Gemini API 文档](https://ai.google.dev/gemini-api/docs/function-calling):

```json
{
  "tools": [
    {
      "functionDeclarations": [
        {"name": "function1"},
        {"name": "function2"}
      ]
    }
  ]
}
```

**关键点**:
- `tools` 是一个数组,包含工具组
- 每个工具组是一个对象,包含 `functionDeclarations` 数组
- **所有函数应该在同一个 `functionDeclarations` 数组中**
- 多个工具组仅用于特殊场景(如多个搜索工具)

### 为什么之前的方式错误?

之前的实现为每个工具创建了独立的工具组:
```python
for tool in anthropic_tools:
    gemini_tools.append({
        "functionDeclarations": [single_tool]  # ❌ 每个工具一个组
    })
```

这导致 Gemini API 认为有多个工具组,触发了限制:
- 如果有多个工具组,它们必须都是搜索工具
- 但我们的工具组包含 Glob, Grep, Read 等非搜索工具

### 为什么新方式正确?

新的实现将所有工具放在一个工具组中:
```python
all_declarations = []
for tool in anthropic_tools:
    all_declarations.append(single_tool)

return [{"functionDeclarations": all_declarations}]  # ✅ 一个组包含所有工具
```

这样 Gemini API 只看到一个工具组,不会触发多工具组的限制。

## 回滚方案

如果修复后出现问题,可以回滚到之前的版本:

```bash
git diff src/anthropic_converter.py
git checkout src/anthropic_converter.py  # 回滚
```

## 相关文档

- [LOG_ANALYSIS_REPORT.md](./LOG_ANALYSIS_REPORT.md) - 详细的日志分析
- [DEBUG_GUIDE.md](./DEBUG_GUIDE.md) - 调试日志使用指南
- [Google Gemini API - Function Calling](https://ai.google.dev/gemini-api/docs/function-calling)

## 总结

这个修复通过正确理解 Gemini API 的工具格式要求,将所有函数声明合并到一个 `functionDeclarations` 数组中,从而解决了 "Multiple tools are supported only when they are all search tools" 错误。

修复后:
- ✅ 保留所有工具功能
- ✅ 符合 Gemini API 规范
- ✅ 不影响 Claude API 调用
- ✅ 代码更简洁清晰
