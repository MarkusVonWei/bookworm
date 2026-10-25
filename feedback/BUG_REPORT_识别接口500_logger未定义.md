# Bug 报告：书籍图片识别接口 100% 返回 500（`logger` 未定义）

- **日期**：2026-10-25
- **环境**：生产环境（服务器 `book`，`/home/ubuntu/workspace/bookworm`，端口 8000，nginx 反代 `bookworm.icu`）
- **问题接口**：`POST /api/bookshelf/recognize`（小程序"上传书面照识别书籍"）
- **问题文件**：`src/bookworm/bookshelf/api.py`
- **严重程度**：高（核心功能完全不可用，100% 必现）
- **影响版本**：当前生产版本（迁移自 bookshelf 重构后代码）
- **代码状态**：**未修改**，仅出报告，等负责人修复

---

## 1. 现象

小程序上传书籍封面图片 → 前端收到 **500 Internal Server Error**。

**关键特征**：不是识别失败，而是**识别成功之后**服务端崩溃。

## 2. 日志证据（完整时间线）

```
20:05:46 [VLM] 开始识别: data/uploads/5cdf88f3-....jpg
20:05:46 [VLM] 图片读取成功, base64长度: 55648
20:05:46 [VLM] 调用API: https://token-plan-cn.xiaomimimo.com/v1/chat/completions
20:05:51 [VLM] API响应: status=200, 耗时=5.06s
20:05:51 [VLM] 解析成功: {"title": "亲密关系", "author": "[加]克里斯多福·孟",
                          "isbn": null, "publisher": "湖南文艺出版社", "publish_date": null}
20:05:51 "POST /api/bookshelf/recognize HTTP/1.1" 500 Internal Server Error   ← 识别成功后 500
ERROR:  Exception in ASGI application
```

**异常堆栈（截取关键帧）**：

```
File "/home/ubuntu/workspace/bookworm/src/bookworm/bookshelf/api.py", line 522, in recognize_book
    logger.info(f"[识别] 识别结果: source=...")
    ^^^^^^
NameError: name 'logger' is not defined
```

## 3. 根因

`src/bookworm/bookshelf/api.py` **没有定义或导入 `logger`**，但 `recognize_book()` 函数里 6 处引用了它：

| 行号 | 代码 | 触发时机 |
|---|---|---|
| **522** | `logger.info(f"[识别] 识别结果: ...")` | **识别成功后立刻执行 → 必崩** |
| 528 | `logger.info(f"[识别] 使用 ISBN 查询元数据: ...")` | ISBN 分支 |
| 534 | `logger.info(f"[识别] 使用标题查询元数据: ...")` | 标题分支 |
| 543 | `logger.warning(f"[识别] metadata获取失败/超时: ...")` | except 分支 |
| 547 | `logger.info(f"[识别] 条形码识别到 ISBN: ...")` | 条形码分支 |
| 559 | `logger.info(f"[识别] 最终结果: ...")` | 返回前 |

文件头部 imports（第 3-17 行）只有 `os/uuid/typing/asyncio/fastapi/pydantic/sqlalchemy/datetime/pathlib` 及项目内部模块，**没有 `import logging`，也没有 logger 赋值语句**。

对照项目内其他模块的规范写法（均已正常工作）：

```python
# recognition.py:23
logger = logging.getLogger("bookworm.recognition")
# barcode.py:17
logger = logging.getLogger("bookworm.barcode")
```

`api.py` 缺少同类语句。

### 3.1 为什么是"现在"爆出来？（回归分析）

老代码 `bookshelf/bookworm/bookshelf/api.py` **同样没有定义 logger**，但只在第 538 行的 `except` 分支用过 1 次：

```python
# 老代码：只有 metadata 查询抛异常时才会踩中 NameError（潜伏 bug，还会掩盖原始异常）
except Exception as e:
    logger.warning(f"[识别] metadata获取失败/超时: {e}, 使用VLM结果")
```

重构时在**正常路径**新增了 5 处 `logger.info(...)`，第一处（522 行）紧跟识别成功之后 → 把潜伏 bug 变成了 **100% 必现**。

### 3.2 复现条件

`recognize_book_from_image()` 成功返回即触发（VLM 成功、或条形码识别到 ISBN）。无任何环境依赖，**必现**。

## 4. 附带代价（为什么建议尽快修）

每次重试都在白白消耗资源：

1. **VLM 调用已计费**：每次失败请求都完整调用了 MiMo VL 模型（本次 5.06s，completion=175 + reasoning=128 tokens），结果被丢弃，用户重试就重复计费。
2. **上传文件残留**：图片已写入 `data/uploads/5cdf88f3-....jpg`，500 后没有清理。
3. **回归盲区**：该接口显然没有覆盖"识别成功"路径的测试。

## 5. 修复建议（供负责人参考）

### 5.1 最小修复

`src/bookworm/bookshelf/api.py` 头部按项目惯例补上：

```python
import logging
logger = logging.getLogger("bookworm.api")
```

### 5.2 建议顺手做的

1. **全项目排查**：`grep -rn 'logger\.' src/` 核对每个模块都有 logger 定义（本次 6 处全在 `api.py`，但建议扫一遍）。
2. **补一条冒烟测试**：mock `recognize_book_from_image` 返回成功结果，断言接口 200。这条测试能在 CI 里拦住此类"正常路径未覆盖"问题。
3. **异常兜底**：`recognize_book` 内部建议整体 try/except 转 500 JSON，避免 Python 异常直接冒泡成 ASGI 500（现在用户只看到"服务器 500"，无任何提示）。

## 6. 次要发现（本次日志顺带暴露，非 500 原因）

**条形码识别功能实际不可用**：

```
[条形码] pyzbar 不可用: No module named 'pyzbar'
[条形码] opencv 不可用: No module named 'cv2'
[条形码] 所有方法均未识别到条形码, 耗时 0.00s
```

生产 venv（`/home/ubuntu/workspace/book_venv`）缺 `pyzbar`/`opencv-python` 依赖（`requirements.txt` 可能未声明，或未安装），当前所有识别都只能走 VLM 慢路径（5 秒/次）。如果条形码是预期功能，需要：
- `requirements.txt` 补依赖：`pyzbar`（还需系统库 `libzbar0`）、`opencv-python-headless`
- 或明确产品上放弃条形码路径，删掉相关代码避免误解

## 7. 复现与验证方法

```bash
# 复现（任意图片即可，识别成功后必 500）
curl -X POST https://bookworm.icu/api/bookshelf/recognize \
  -H 'Host: bookworm.icu' -H 'X-User-Id: 1' \
  -F 'file=@任意书籍封面.jpg'

# 修复后验证
# 1) 期望 200，返回 {"title": ..., "author": ..., ...}
# 2) all.log 中出现 "[识别] 识别结果: ..." 且无 Traceback
```
