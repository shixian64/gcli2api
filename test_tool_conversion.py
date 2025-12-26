#!/usr/bin/env python3
"""
测试工具转换修复
验证 convert_tools 函数是否正确地将所有工具合并到一个 functionDeclarations 数组中
"""

import sys
sys.path.insert(0, '/home/hmt/disk_2T/share/project/gcli2api')

from src.anthropic_converter import convert_tools

# 模拟 Anthropic 格式的工具列表
anthropic_tools = [
    {
        "name": "Glob",
        "description": "Fast file pattern matching",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string"}
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "Grep",
        "description": "Search tool built on ripgrep",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {"type": "string"}
            },
            "required": ["pattern"]
        }
    },
    {
        "name": "Read",
        "description": "Reads a file from filesystem",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "WebFetch",
        "description": "Fetches content from URL",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string"}
            },
            "required": ["url"]
        }
    },
    {
        "name": "WebSearch",
        "description": "Search the web",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        }
    }
]

print("=" * 60)
print("测试工具转换修复")
print("=" * 60)

# 转换工具
result = convert_tools(anthropic_tools)

print(f"\n输入: {len(anthropic_tools)} 个 Anthropic 工具")
print(f"输出: {len(result)} 个工具组")

if len(result) == 1:
    print("✅ 正确: 所有工具合并到一个工具组中")

    function_declarations = result[0].get("functionDeclarations", [])
    print(f"✅ 工具组包含 {len(function_declarations)} 个函数声明")

    print("\n函数列表:")
    for i, func in enumerate(function_declarations, 1):
        print(f"  {i}. {func['name']}")

    # 验证所有工具都被包含
    expected_names = {"Glob", "Grep", "Read", "WebFetch", "WebSearch"}
    actual_names = {func["name"] for func in function_declarations}

    if expected_names == actual_names:
        print("\n✅ 所有工具都被正确转换")
    else:
        print(f"\n❌ 工具缺失: {expected_names - actual_names}")
        print(f"❌ 多余工具: {actual_names - expected_names}")

    print("\n" + "=" * 60)
    print("结论: 修复成功! 符合 Gemini API 规范")
    print("=" * 60)

else:
    print(f"❌ 错误: 应该返回 1 个工具组,实际返回 {len(result)} 个")
    print("\n工具组详情:")
    for i, tool_group in enumerate(result, 1):
        funcs = tool_group.get("functionDeclarations", [])
        print(f"  工具组 {i}: {len(funcs)} 个函数")
        for func in funcs:
            print(f"    - {func['name']}")

    print("\n" + "=" * 60)
    print("结论: 修复失败! 仍然是多个工具组")
    print("=" * 60)

# 显示转换后的结构示例
import json
print("\n转换后的结构 (简化):")
simplified = [{
    "functionDeclarations": [
        {"name": func["name"], "description": func["description"][:40] + "..."}
        for func in result[0]["functionDeclarations"]
    ]
}]
print(json.dumps(simplified, indent=2, ensure_ascii=False))
