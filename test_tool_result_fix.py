#!/usr/bin/env python3
"""
测试 tool_result 转换修复
验证 functionResponse.name 是否正确填充
"""

import sys
sys.path.insert(0, '/home/hmt/disk_2T/share/project/gcli2api')

from src.anthropic_converter import convert_messages_to_contents

# 模拟 Anthropic 格式的消息,包含 tool_use 和 tool_result
messages = [
    {
        "role": "user",
        "content": "请使用 WebFetch 工具获取网页内容"
    },
    {
        "role": "assistant",
        "content": [
            {
                "type": "tool_use",
                "id": "toolu_123456",
                "name": "WebFetch",
                "input": {
                    "url": "https://example.com",
                    "prompt": "Get content"
                }
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "tool_result",
                "tool_use_id": "toolu_123456",
                "content": "网页内容: Hello World"
            }
        ]
    }
]

print("=" * 60)
print("测试 tool_result 转换修复")
print("=" * 60)

# 转换消息
contents = convert_messages_to_contents(messages)

print(f"\n输入: {len(messages)} 条消息")
print(f"输出: {len(contents)} 条 contents")

# 查找 functionResponse
found_function_response = False
for content in contents:
    parts = content.get("parts", [])
    for part in parts:
        if "functionResponse" in part:
            found_function_response = True
            fr = part["functionResponse"]
            print("\n找到 functionResponse:")
            print(f"  id: {fr.get('id')}")
            print(f"  name: {fr.get('name')}")
            print(f"  response: {str(fr.get('response', {}))[:50]}...")

            # 验证 name 字段
            if fr.get("name") == "WebFetch":
                print("\n✅ 成功: functionResponse.name 正确填充为 'WebFetch'")
            elif fr.get("name") == "":
                print("\n❌ 失败: functionResponse.name 仍然是空字符串")
            else:
                print(f"\n⚠️  警告: functionResponse.name 是 '{fr.get('name')}', 预期是 'WebFetch'")

if not found_function_response:
    print("\n❌ 错误: 未找到 functionResponse")

print("\n" + "=" * 60)
if found_function_response and contents[2]["parts"][0]["functionResponse"]["name"] == "WebFetch":
    print("结论: 修复成功! functionResponse.name 正确填充")
else:
    print("结论: 修复失败!")
print("=" * 60)
