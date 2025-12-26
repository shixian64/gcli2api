# 调试日志使用指南

## 快速开始

### 1. 启用调试日志

已在 `.env` 文件中添加以下配置:

```bash
# 启用 Anthropic 路由调试日志
ANTHROPIC_DEBUG=1

# 启用请求体详细日志 (包含完整请求和响应)
ANTHROPIC_DEBUG_BODY=1

# 单个字符串字段最大输出长度 (避免 base64 图片打爆日志)
ANTHROPIC_DEBUG_MAX_CHARS=2000
```

### 2. 重启服务

```bash
# 停止当前服务 (Ctrl+C)
# 重新启动
python web.py
```

### 3. 查看日志输出

调试日志会输出到 `log.txt` 文件中,包含以下内容:

## 日志内容说明

### 基础请求日志 (ANTHROPIC_DEBUG=1)

```
[ANTHROPIC] /messages 收到请求: client=127.0.0.1:49738, model=claude-haiku-4-5-20251001, stream=True, messages=1, thinking_present=False, thinking=None, ua=claude-cli/2.0.76
[ANTHROPIC] /messages 模型映射: upstream=claude-haiku-4-5-20251001 -> downstream=gemini-2.5-flash
```

### 详细请求体日志 (ANTHROPIC_DEBUG_BODY=1)

#### 1. 上游请求头和请求体

```
[ANTHROPIC][DEBUG] headers={"anthropic-version":"2023-06-01","content-length":"1234","content-type":"application/json","user-agent":"claude-cli/2.0.76"}
[ANTHROPIC][DEBUG] payload={"max_tokens":4096,"messages":[{"content":"Hello","role":"user"}],"model":"claude-haiku-4-5-20251001","stream":true,"tools":[...]}
```

**包含信息**:
- `headers`: 请求头 (已脱敏,不包含 API key)
- `payload`: 完整的 Anthropic 格式请求体
  - `model`: 上游模型名称
  - `messages`: 对话消息列表
  - `tools`: 工具定义 (如果有)
  - `thinking`: 思维链配置 (如果有)
  - `max_tokens`: 最大 token 数

#### 2. 下游请求体 (转换后)

```
[ANTHROPIC][DEBUG] downstream_request_body={"contents":[{"parts":[{"text":"Hello"}],"role":"user"}],"generationConfig":{"maxOutputTokens":4096},"model":"gemini-2.5-flash","systemInstruction":{"parts":[{"text":"..."}]},"tools":[...]}
```

**包含信息**:
- `contents`: 转换后的 Gemini 格式消息
- `model`: 下游模型名称 (映射后)
- `tools`: 转换后的工具定义
- `systemInstruction`: 系统指令
- `generationConfig`: 生成配置

## 日志脱敏说明

为保护隐私,日志会自动脱敏以下字段:

- `authorization` → `<REDACTED>`
- `x-api-key` → `<REDACTED>`
- `api_key` → `<REDACTED>`
- `access_token` → `<REDACTED>`
- `password` → `<REDACTED>`
- `secret` → `<REDACTED>`

超长字符串会被截断:

```
"long_text": "前1000字符...<...省略 5000 字符...>...后1000字符"
```

Base64 图片数据会被替换:

```
"data": "<base64 len=123456>"
```

## 分析工具调用错误

### 问题: "Multiple tools are supported only when they are all search tools"

查看日志中的 `tools` 字段:

```json
[ANTHROPIC][DEBUG] payload={
  "tools": [
    {"name": "web_search", "type": "..."},
    {"name": "code_execution", "type": "..."}  // ← 非搜索工具
  ]
}
```

**原因**: Gemini API 不支持同时使用多个非搜索类工具

**解决方案**:
1. 只保留第一个工具
2. 过滤掉非搜索类工具
3. 使用 Claude 模型而非 Gemini 模型

## 关闭调试日志

调试完成后,建议关闭详细日志以减少磁盘占用:

```bash
# .env 文件中修改
ANTHROPIC_DEBUG=0
ANTHROPIC_DEBUG_BODY=0
```

或者只保留基础日志:

```bash
ANTHROPIC_DEBUG=1
ANTHROPIC_DEBUG_BODY=0  # 关闭请求体详细日志
```

## 日志文件管理

### 清空日志

```bash
# 清空 log.txt
> log.txt

# 或者删除后重新创建
rm log.txt
touch log.txt
```

### 日志轮转 (可选)

如果日志文件过大,可以手动轮转:

```bash
# 备份当前日志
mv log.txt log.txt.$(date +%Y%m%d_%H%M%S)

# 服务会自动创建新的 log.txt
```

## 常见调试场景

### 场景 1: 分析请求转换问题

1. 开启 `ANTHROPIC_DEBUG_BODY=1`
2. 发送测试请求
3. 对比 `payload` (上游) 和 `downstream_request_body` (下游)
4. 检查字段映射是否正确

### 场景 2: 分析工具调用失败

1. 查看 `payload.tools` 的完整定义
2. 查看 `downstream_request_body.tools` 的转换结果
3. 检查工具数量和类型是否符合下游 API 限制

### 场景 3: 分析 Token 计数问题

1. 查看 `[ANTHROPIC][DEBUG]` 日志中的 token 估算
2. 对比上游请求和下游响应的 token 数量
3. 检查 `usageMetadata` 字段

## 性能影响

- `ANTHROPIC_DEBUG=1`: 性能影响极小 (仅额外日志输出)
- `ANTHROPIC_DEBUG_BODY=1`: 中等性能影响 (需要序列化完整请求体)
- 建议仅在调试时开启,生产环境关闭

## 示例: 完整调试流程

```bash
# 1. 开启调试
vim .env  # 设置 ANTHROPIC_DEBUG=1, ANTHROPIC_DEBUG_BODY=1

# 2. 重启服务
python web.py

# 3. 发送测试请求 (使用 claude-cli 或 curl)
# ...

# 4. 查看日志
tail -f log.txt | grep "\[ANTHROPIC\]\[DEBUG\]"

# 5. 分析问题
# - 检查 payload 中的 tools 定义
# - 检查 downstream_request_body 中的转换结果
# - 对比上下游差异

# 6. 关闭调试
vim .env  # 设置 ANTHROPIC_DEBUG_BODY=0
```

## 技术细节

### 日志函数位置

- `_debug_log_request_payload()`: src/antigravity_anthropic_router.py:136
- `_debug_log_downstream_request_body()`: src/antigravity_anthropic_router.py:157
- `_redact_for_log()`: src/antigravity_anthropic_router.py:94

### 环境变量检查

- `_anthropic_debug_enabled()`: src/antigravity_anthropic_router.py:81
- `_anthropic_debug_body_enabled()`: src/antigravity_anthropic_router.py:85
- `_anthropic_debug_max_chars()`: src/antigravity_anthropic_router.py:68
