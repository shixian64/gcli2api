#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Anthropic builtin tools to Gemini tools conversion"""

from src.anthropic_converter import convert_tools


def test_web_search_conversion():
    """测试 web_search 转换为 googleSearch"""
    tools = [{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}]
    result = convert_tools(tools)
    assert result == [{"googleSearch": {}}], f"Expected googleSearch, got {result}"
    print("✓ test_web_search_conversion passed")


def test_code_execution_conversion():
    """测试 code_execution 转换为 codeExecution"""
    tools = [{"type": "code_execution_20250522", "name": "code_execution"}]
    result = convert_tools(tools)
    assert result == [{"codeExecution": {}}], f"Expected codeExecution, got {result}"
    print("✓ test_code_execution_conversion passed")


def test_mixed_tools():
    """测试混合工具 (内置 + 自定义)"""
    tools = [
        {"type": "web_search_20250305", "name": "web_search"},
        {
            "name": "get_weather",
            "description": "Get weather",
            "input_schema": {"type": "object", "properties": {"city": {"type": "string"}}},
        },
    ]
    result = convert_tools(tools)
    assert len(result) == 2, f"Expected 2 tool groups, got {len(result)}"
    assert "googleSearch" in result[0], f"Expected googleSearch in first tool"
    assert "functionDeclarations" in result[1], f"Expected functionDeclarations in second tool"
    print("✓ test_mixed_tools passed")


def test_unsupported_tools_skipped():
    """测试不支持的工具被跳过"""
    tools = [{"type": "computer_20250124", "name": "computer"}]
    result = convert_tools(tools)
    assert result is None, f"Expected None for unsupported tool, got {result}"
    print("✓ test_unsupported_tools_skipped passed")


def test_empty_input_schema_gets_type():
    """测试空 input_schema 自动添加 type"""
    tools = [{"name": "test_tool", "description": "Test", "input_schema": {}}]
    result = convert_tools(tools)
    params = result[0]["functionDeclarations"][0]["parameters"]
    assert params.get("type") == "object", f"Expected type=object, got {params}"
    print("✓ test_empty_input_schema_gets_type passed")


def test_no_duplicate_builtin_tools():
    """测试不会重复添加相同的内置工具"""
    tools = [
        {"type": "web_search_20250305", "name": "web_search"},
        {"type": "web_search_20250305", "name": "web_search"},  # 重复
    ]
    result = convert_tools(tools)
    google_search_count = sum(1 for t in result if "googleSearch" in t)
    assert google_search_count == 1, f"Expected 1 googleSearch, got {google_search_count}"
    print("✓ test_no_duplicate_builtin_tools passed")


def test_all_builtin_tools():
    """测试同时使用多个内置工具"""
    tools = [
        {"type": "web_search_20250305", "name": "web_search"},
        {"type": "code_execution_20250522", "name": "code_execution"},
    ]
    result = convert_tools(tools)
    assert len(result) == 2, f"Expected 2 tools, got {len(result)}"
    has_google_search = any("googleSearch" in t for t in result)
    has_code_execution = any("codeExecution" in t for t in result)
    assert has_google_search, "Expected googleSearch"
    assert has_code_execution, "Expected codeExecution"
    print("✓ test_all_builtin_tools passed")


if __name__ == "__main__":
    test_web_search_conversion()
    test_code_execution_conversion()
    test_mixed_tools()
    test_unsupported_tools_skipped()
    test_empty_input_schema_gets_type()
    test_no_duplicate_builtin_tools()
    test_all_builtin_tools()
    print("\n所有测试通过!")
