#!/usr/bin/env python3
"""
VLM 书籍封面识别测试脚本
逐条记录每一步的输入/输出，便于人工验证。

用法:
  cd /Users/marvin/workspace/life_project/bookworm
  ./venv/bin/python tests/test_vlm_recognition.py
"""

import sys
import base64
import json
import time
import httpx
from pathlib import Path

# ── 从项目配置读取，不 hardcode ────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
from config.settings import MIMO_API_KEY, MIMO_API_BASE, LLM_MODEL

# ── 路径 ──────────────────────────────────────────────
IMGS_DIR = PROJECT_ROOT / "imgs"
OUTPUT_DIR = PROJECT_ROOT / "tests" / "vlm_test_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

API_BASE = MIMO_API_BASE
API_KEY = MIMO_API_KEY
MODEL = LLM_MODEL
TIMEOUT = 60.0

PROMPT = """请识别这张书籍封面图片，提取以下信息并以JSON格式返回：
{
    "title": "书名",
    "author": "作者",
    "publisher": "出版社",
    "publish_date": "出版日期",
    "isbn": "ISBN号（如果能看到）",
    "category": "分类/类型"
}

如果某个字段无法识别，请返回null。只返回JSON，不要其他内容。"""


def log_step(step: int, title: str, detail: str):
    line = f"\n{'='*60}\n[Step {step}] {title}\n{'='*60}\n{detail}"
    print(line)
    return line


def image_to_base64(image_path: Path) -> str:
    return base64.b64encode(image_path.read_bytes()).decode("utf-8")


def parse_llm_json(raw: str) -> dict:
    """从 LLM 返回文本中提取 JSON"""
    text = raw.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return json.loads(text.strip())


def recognize_book(image_path: Path) -> dict:
    """调用 MiMo VL API 识别封面，返回完整调试信息"""
    b64 = image_to_base64(image_path)
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
        "max_tokens": 4096,
    }

    with httpx.Client(timeout=TIMEOUT) as client:
        resp = client.post(
            f"{API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    return {
        "status_code": resp.status_code,
        "response_json": resp.json() if resp.status_code == 200 else resp.text,
    }


async def async_recognize_book(image_path: Path) -> dict:
    """异步版本，供 recognition.py 内部函数直接调用测试"""
    b64 = image_to_base64(image_path)
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                    },
                    {"type": "text", "text": PROMPT},
                ],
            }
        ],
        "max_tokens": 4096,
    }

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.post(
            f"{API_BASE}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
        )

    return {
        "status_code": resp.status_code,
        "response_json": resp.json() if resp.status_code == 200 else resp.text,
    }


async def test_async():
    """异步入口：直接调用 recognition.py 的函数验证集成"""
    from src.bookworm.bookshelf.recognition import recognize_book_from_image

    print("\n" + "#"*60)
    print("# Part B: 异步集成测试 (recognize_book_from_image)")
    print("#"*60)

    for img_file in sorted(IMGS_DIR.glob("*.jpg")):
        log = []
        log.append(log_step(1, "图片路径", str(img_file)))
        log.append(log_step(2, "base64 长度", str(len(image_to_base64(img_file)))))

        t0 = time.time()
        result = await recognize_book_from_image(str(img_file))
        elapsed = time.time() - t0

        log.append(log_step(3, "识别结果", json.dumps(result, ensure_ascii=False, indent=2)))
        log.append(log_step(4, "耗时", f"{elapsed:.2f}s"))

        out_file = OUTPUT_DIR / f"async_{img_file.stem}.log"
        out_file.write_text("\n".join(log), encoding="utf-8")
        print(f"\n  → 日志已保存: {out_file}")


def main():
    print("=" * 60)
    print("VLM Book Cover Recognition Test")
    print("=" * 60)

    # ── Part A: 同步逐条测试 ─────────────────────────
    print("\n" + "#"*60)
    print("# Part A: 同步逐张测试")
    print("#"*60)

    all_logs = []

    for idx, img_file in enumerate(sorted(IMGS_DIR.glob("*.jpg")), 1):
        log = []

        log.append(log_step(1, "输入图片", str(img_file)))
        log.append(log_step(2, "图片大小", f"{img_file.stat().st_size:,} bytes"))

        b64 = image_to_base64(img_file)
        log.append(log_step(3, "Base64 编码", f"长度 = {len(b64)} 字符 (前60字符: {b64[:60]}...)"))

        log.append(log_step(4, "API 端点", f"{API_BASE}/chat/completions"))
        log.append(log_step(5, "模型", MODEL))
        log.append(log_step(6, "Prompt", PROMPT))

        print(f"\n--- 正在识别: {img_file.name} ---")
        t0 = time.time()
        result = recognize_book(img_file)
        elapsed = time.time() - t0

        log.append(log_step(7, "HTTP 状态码", str(result["status_code"])))

        if result["status_code"] == 200:
            resp_body = result["response_json"]
            # 始终记录完整响应（含 finish_reason、usage 等）
            log.append(log_step(8, "完整 API 响应", json.dumps(resp_body, ensure_ascii=False, indent=2)))

            raw_content = resp_body["choices"][0]["message"]["content"]
            log.append(log_step(9, "LLM content 字段", repr(raw_content)))

            try:
                parsed = parse_llm_json(raw_content)
                log.append(log_step(10, "解析后 JSON", json.dumps(parsed, ensure_ascii=False, indent=2)))
            except Exception as e:
                log.append(log_step(10, "JSON 解析失败", str(e)))
                parsed = {"error": str(e)}
        else:
            log.append(log_step(8, "API 错误", json.dumps(result["response_json"], ensure_ascii=False, indent=2)))
            parsed = {"error": result["response_json"]}

        log.append(log_step(11, "耗时", f"{elapsed:.2f}s"))

        # 保存日志
        out_file = OUTPUT_DIR / f"sync_{img_file.stem}.log"
        out_file.write_text("\n".join(log), encoding="utf-8")
        print(f"  → 日志已保存: {out_file}")

        all_logs.append({
            "file": img_file.name,
            "result": parsed,
            "elapsed": f"{elapsed:.2f}s",
        })
        break

    # ── 汇总 ─────────────────────────────────────────
    summary_file = OUTPUT_DIR / "summary.json"
    summary_file.write_text(
        json.dumps(all_logs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\n{'='*60}")
    print(f"汇总结果已保存: {summary_file}")
    print(f"{'='*60}")

    for item in all_logs:
        print(f"\n  📖 {item['file']}")
        if "error" in item["result"]:
            print(f"     ❌ 错误: {item['result']['error']}")
        else:
            r = item["result"]
            print(f"     书名: {r.get('title', '-')}")
            print(f"     作者: {r.get('author', '-')}")
            print(f"     出版社: {r.get('publisher', '-')}")
            print(f"     ISBN: {r.get('isbn', '-')}")
            print(f"     耗时: {item['elapsed']}")

    # ── Part B: 异步集成测试 ─────────────────────────
    import asyncio
    asyncio.run(test_async())


if __name__ == "__main__":
    main()
