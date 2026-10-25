# 条形码识别功能

## 功能概述

新增书籍条形码识别能力，支持识别书籍背面的 ISBN 条形码，自动提取 ISBN 号用于查询书籍元数据。

## 支持的条形码类型

| 类型 | 说明 | ISBN 支持 |
|------|------|-----------|
| EAN-13 | 13 位国际标准书号 | ✅ 直接识别 |
| EAN-8 | 8 位条形码 | ✅ 尝试转换 |
| UPCA | 12 位通用产品代码 | ✅ 转换为 ISBN-13 |
| UPCE | 6 位通用产品代码 | ✅ 尝试转换 |
| CODE128 | 通用条形码 | ✅ 提取数字部分 |
| CODE39 | 通用条形码 | ✅ 提取数字部分 |

## 功能特性

### 1. 条形码识别
- 使用 `pyzbar` 库进行高速识别
- 备选 `opencv` 方案（当 pyzbar 不可用时）
- 支持灰度处理提高识别率

### 2. ISBN 提取
- 自动识别 978/979 开头的 ISBN-13
- 支持 ISBN-10 转 ISBN-13
- 支持 UPCA 转 ISBN-13

### 3. ISBN 验证
- ISBN-13 校验位验证
- ISBN-10 校验位验证

## API 使用

### 识别条形码

```python
from bookworm.bookshelf.barcode import recognize_barcode

result = recognize_barcode("path/to/image.jpg")
if result:
    print(f"ISBN: {result.get('isbn')}")
    print(f"条形码类型: {result.get('barcode_type')}")
    print(f"条形码数据: {result.get('barcode_data')}")
```

### 验证 ISBN

```python
from bookworm.bookshelf.barcode import validate_isbn13, validate_isbn10

is_valid = validate_isbn13("9787020024759")  # True
is_valid = validate_isbn10("0131103628")     # True
```

### 格式转换

```python
from bookworm.bookshelf.barcode import _isbn10_to_isbn13, _upca_to_isbn13

isbn13 = _isbn10_to_isbn13("0131103628")  # "9780131103627"
isbn13 = _upca_to_isbn13("978702002475")  # "9787020024759"
```

## 集成到识别流程

条形码识别已集成到 `recognize_book_from_image` 函数中：

1. **优先级 1**: 条形码识别（快速，优先使用）
2. **优先级 2**: VLM 识别（当条形码识别失败时）

```python
async def recognize_book_from_image(image_path: str) -> Dict[str, Any]:
    # 步骤0: 尝试条形码识别
    barcode_result = _try_barcode_recognition(image_path)
    if barcode_result and barcode_result.get("isbn"):
        return {"isbn": barcode_result["isbn"], "source": "barcode"}
    
    # 步骤1: VLM 识别
    # ... VLM 识别逻辑
```

## 测试

运行测试脚本：

```bash
python tests/test_barcode.py
```

测试内容：
- ISBN 提取逻辑
- ISBN 格式转换
- ISBN 校验位验证
- 图片条形码识别

## 依赖

### 系统依赖（可选，用于 pyzbar）
```bash
# macOS
brew install zbar

# Ubuntu/Debian
sudo apt-get install libzbar0
```

### Python 依赖
```bash
pip install pyzbar opencv-python-headless Pillow
```

## 注意事项

1. **图片质量**: 条形码图片需要清晰、完整
2. **系统库**: pyzbar 需要 zbar 系统库，如不可用会使用 opencv 备选方案
3. **ISBN 格式**: 只有 978/979 开头的 EAN-13 才会被识别为 ISBN
4. **测试图片**: `imgs/strip_code_test.jpg` 可能不包含标准条形码，测试结果显示模块功能正常

## 相关文件

- `src/bookworm/bookshelf/barcode.py` - 条形码识别模块
- `src/bookworm/bookshelf/recognition.py` - 集成到主识别流程
- `tests/test_barcode.py` - 测试脚本
