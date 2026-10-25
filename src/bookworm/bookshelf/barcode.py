"""
条形码/ISBN 识别模块

支持识别书籍背面的条形码（EAN-13/ISBN-13），
提取 ISBN 号用于查询书籍元数据。
"""

import os
# 设置 zbar 库路径 (macOS Homebrew)
os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/lib:' + os.environ.get('DYLD_LIBRARY_PATH', '')
os.environ['LD_LIBRARY_PATH'] = '/opt/homebrew/lib:' + os.environ.get('LD_LIBRARY_PATH', '')

import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger("bookworm.barcode")


def recognize_barcode(image_path: str) -> Optional[Dict[str, Any]]:
    """
    识别图片中的条形码

    优先使用 pyzbar，失败后使用 opencv 作为备选方案

    Args:
        image_path: 图片文件路径

    Returns:
        识别结果字典，包含 isbn、barcode_type 等，失败返回 None
    """
    start_time = __import__("time").time()
    logger.info(f"[条形码] 开始识别: {image_path}")

    # 尝试 pyzbar
    result = _try_pyzbar(image_path)
    if result:
        elapsed = __import__("time").time() - start_time
        logger.info(f"[条形码] pyzbar 识别成功, 耗时 {elapsed:.2f}s")
        return result

    # 尝试 opencv
    result = _try_opencv(image_path)
    if result:
        elapsed = __import__("time").time() - start_time
        logger.info(f"[条形码] opencv 识别成功, 耗时 {elapsed:.2f}s")
        return result

    elapsed = __import__("time").time() - start_time
    logger.warning(f"[条形码] 所有方法均未识别到条形码, 耗时 {elapsed:.2f}s")
    return None


def _try_pyzbar(image_path: str) -> Optional[Dict[str, Any]]:
    """使用 pyzbar 识别条形码"""
    try:
        from pyzbar.pyzbar import decode, ZBarSymbol
        from PIL import Image
    except ImportError as e:
        logger.debug(f"[条形码] pyzbar 不可用: {e}")
        return None

    try:
        image = Image.open(image_path)
        logger.info(f"[条形码] pyzbar: 图片尺寸 {image.size}")

        barcodes = decode(image, symbols=[
            ZBarSymbol.EAN13, ZBarSymbol.EAN8,
            ZBarSymbol.UPCA, ZBarSymbol.UPCE,
            ZBarSymbol.CODE128, ZBarSymbol.CODE39,
        ])

        if not barcodes:
            # 灰度重试
            gray_image = image.convert("L")
            barcodes = decode(gray_image, symbols=[
                ZBarSymbol.EAN13, ZBarSymbol.EAN8,
                ZBarSymbol.UPCA, ZBarSymbol.UPCE,
            ])

        if not barcodes:
            return None

        results = []
        for barcode in barcodes:
            barcode_type = barcode.type
            barcode_data = barcode.data.decode("utf-8")
            logger.info(f"[条形码] pyzbar: type={barcode_type}, data={barcode_data}")

            result = {
                "barcode_type": barcode_type,
                "barcode_data": barcode_data,
                "rect": {
                    "left": barcode.rect.left,
                    "top": barcode.rect.top,
                    "width": barcode.rect.width,
                    "height": barcode.rect.height,
                }
            }
            isbn = _extract_isbn(barcode_data, barcode_type)
            if isbn:
                result["isbn"] = isbn
            results.append(result)

        return results[0] if results else None

    except Exception as e:
        logger.debug(f"[条形码] pyzbar 失败: {e}")
        return None


def _try_opencv(image_path: str) -> Optional[Dict[str, Any]]:
    """使用 opencv 识别条形码"""
    try:
        import cv2
        import numpy as np
    except ImportError as e:
        logger.debug(f"[条形码] opencv 不可用: {e}")
        return None

    try:
        # 读取图片
        img = cv2.imread(image_path)
        if img is None:
            logger.warning("[条形码] opencv: 无法读取图片")
            return None

        logger.info(f"[条形码] opencv: 图片尺寸 {img.shape}")

        # 方法1: 使用 BarcodeDetector (OpenCV 4.5.4+)
        try:
            detector = cv2.barcode.BarcodeDetector()
            ok, decoded_info, decoded_type, points = detector.detectAndDecodeMulti(img)

            if ok and decoded_info:
                for i, (info, btype) in enumerate(zip(decoded_info, decoded_type)):
                    if info:
                        logger.info(f"[条形码] opencv: type={btype}, data={info}")
                        result = {
                            "barcode_type": btype,
                            "barcode_data": info,
                            "rect": {
                                "left": int(points[i][0][0]),
                                "top": int(points[i][0][1]),
                                "width": int(points[i][2][0] - points[i][0][0]),
                                "height": int(points[i][2][1] - points[i][0][1]),
                            }
                        }
                        isbn = _extract_isbn(info, btype)
                        if isbn:
                            result["isbn"] = isbn
                        return result
        except (AttributeError, cv2.error) as e:
            logger.debug(f"[条形码] opencv BarcodeDetector 不可用: {e}")

        # 方法2: 使用简单的图像处理 + 模式匹配
        result = _opencv_simple_detect(img)
        return result

    except Exception as e:
        logger.debug(f"[条形码] opencv 失败: {e}")
        return None


def _opencv_simple_detect(img) -> Optional[Dict[str, Any]]:
    """简单的条形码检测（基于图像处理）"""
    try:
        import cv2
        import numpy as np

        # 转灰度
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 高斯模糊
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # 边缘检测
        edges = cv2.Canny(blurred, 50, 150)

        # 形态学操作
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
        closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

        # 查找轮廓
        contours, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 筛选可能的条形码区域
        barcode_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # 条形码通常是宽矩形
            if w > 100 and h > 20 and w / h > 2:
                barcode_regions.append((x, y, w, h))

        if barcode_regions:
            logger.info(f"[条形码] opencv: 找到 {len(barcode_regions)} 个可能的条形码区域")
            # 返回最大的区域
            largest = max(barcode_regions, key=lambda r: r[2] * r[3])
            x, y, w, h = largest
            logger.info(f"[条形码] opencv: 最大区域 ({x},{y},{w},{h})")

            # 尝试在该区域进行 OCR 或其他识别
            # 这里可以添加更复杂的识别逻辑
            return {
                "barcode_type": "UNKNOWN",
                "barcode_data": "",
                "rect": {"left": x, "top": y, "width": w, "height": h},
                "detected": True,
                "message": "检测到条形码区域，但无法解码"
            }

        return None

    except Exception as e:
        logger.debug(f"[条形码] opencv simple detect 失败: {e}")
        return None


def _extract_isbn(barcode_data: str, barcode_type: str) -> Optional[str]:
    """
    从条形码数据中提取 ISBN

    EAN-13 格式的 ISBN-13 通常以 978 或 979 开头
    """
    # 清理数据
    data = barcode_data.strip()

    # EAN-13 / ISBN-13
    if barcode_type == "EAN13" and len(data) == 13:
        if data.startswith("978") or data.startswith("979"):
            logger.info(f"[条形码] EAN-13 识别为 ISBN-13: {data}")
            return data

    # UPCA 可能是 ISBN-10 的 12 位版本
    if barcode_type == "UPCA" and len(data) == 12:
        # 尝试转换为 ISBN-13
        isbn13 = _upca_to_isbn13(data)
        if isbn13:
            return isbn13

    # CODE128 可能包含 ISBN
    if barcode_type == "CODE128":
        # 提取数字部分
        digits = "".join(c for c in data if c.isdigit())
        if len(digits) == 13 and (digits.startswith("978") or digits.startswith("979")):
            return digits
        if len(digits) == 10:
            return _isbn10_to_isbn13(digits)

    # 尝试从任意数据中提取 ISBN
    digits = "".join(c for c in data if c.isdigit())
    if len(digits) == 13 and (digits.startswith("978") or digits.startswith("979")):
        return digits

    return None


def _upca_to_isbn13(upca: str) -> Optional[str]:
    """UPC-A 转 ISBN-13"""
    if len(upca) != 12:
        return None

    # UPCA 通常是 ISBN-10 去掉校验位的前 9 位
    # 尝试直接作为 ISBN-13 的前 12 位（加校验位）
    isbn13 = upca + "0"  # 临时校验位
    total = 0
    for i, d in enumerate(upca):
        total += int(d) * (1 if i % 2 == 0 else 3)
    check_digit = (10 - (total % 10)) % 10
    return upca + str(check_digit)


def _isbn10_to_isbn13(isbn10: str) -> Optional[str]:
    """ISBN-10 转 ISBN-13"""
    if len(isbn10) != 10:
        return None

    # 提取前 9 位数字
    digits = isbn10[:9]
    if not digits.isdigit():
        return None

    # 计算 ISBN-13 校验位
    prefix = "978" + digits
    total = 0
    for i, d in enumerate(prefix):
        total += int(d) * (1 if i % 2 == 0 else 3)

    check_digit = (10 - (total % 10)) % 10
    return prefix + str(check_digit)


def validate_isbn13(isbn: str) -> bool:
    """验证 ISBN-13 校验位"""
    if len(isbn) != 13 or not isbn.isdigit():
        return False

    total = 0
    for i, d in enumerate(isbn):
        total += int(d) * (1 if i % 2 == 0 else 3)

    return total % 10 == 0


def validate_isbn10(isbn: str) -> bool:
    """验证 ISBN-10 校验位"""
    if len(isbn) != 10:
        return False

    total = 0
    for i, d in enumerate(isbn):
        if d == "X" and i == 9:
            total += 10 * 10
        elif d.isdigit():
            total += int(d) * (10 - i)
        else:
            return False

    return total % 11 == 0


def recognize_barcode_with_crop(image_path: str, crop_regions: list = None) -> Optional[Dict[str, Any]]:
    """
    识别图片中的条形码（支持裁剪优化）

    对于大图片，先裁剪可能包含条形码的区域，再识别

    Args:
        image_path: 图片文件路径
        crop_regions: 裁剪区域列表 [(x1, y1, x2, y2), ...]，None 则自动检测

    Returns:
        识别结果字典，失败返回 None
    """
    try:
        from PIL import Image
    except ImportError:
        return None

    start_time = __import__("time").time()
    logger.info(f"[条形码] 开始识别（裁剪模式）: {image_path}")

    # 直接识别完整图片
    result = _try_pyzbar(image_path)
    if result and result.get('barcode_data'):
        elapsed = __import__("time").time() - start_time
        logger.info(f"[条形码] 完整图片识别成功, 耗时 {elapsed:.2f}s")
        return result

    # 需要裁剪识别
    try:
        img = Image.open(image_path)
        width, height = img.size
        logger.info(f"[条形码] 图片尺寸: {width}x{height}")

        # 如果图片太大，自动裁剪
        if width > 2000 or height > 2000:
            logger.info("[条形码] 图片较大，尝试裁剪识别")

            # 自动检测条形码区域
            if crop_regions is None:
                crop_regions = _auto_detect_barcode_regions(image_path)

            # 尝试每个裁剪区域
            for i, (x1, y1, x2, y2) in enumerate(crop_regions):
                logger.info(f"[条形码] 尝试裁剪区域 {i}: ({x1},{y1})-({x2},{y2})")
                cropped = img.crop((x1, y1, x2, y2))

                # 保存临时文件
                temp_path = f"/tmp/barcode_crop_{i}.jpg"
                cropped.save(temp_path)

                result = _try_pyzbar(temp_path)
                if result and result.get('barcode_data'):
                    elapsed = __import__("time").time() - start_time
                    logger.info(f"[条形码] 裁剪区域 {i} 识别成功, 耗时 {elapsed:.2f}s")
                    # 添加裁剪区域信息
                    result['crop_region'] = (x1, y1, x2, y2)
                    return result

        # 尝试放大后识别
        logger.info("[条形码] 尝试放大图片识别...")
        for scale in [1.5, 2.0, 3.0]:
            new_size = (int(width * scale), int(height * scale))
            resized = img.resize(new_size, Image.Resampling.LANCZOS)
            temp_path = f"/tmp/barcode_resized_{scale}.jpg"
            resized.save(temp_path)

            result = _try_pyzbar(temp_path)
            if result and result.get('barcode_data'):
                elapsed = __import__("time").time() - start_time
                logger.info(f"[条形码] 放大 {scale}x 识别成功, 耗时 {elapsed:.2f}s")
                return result

        elapsed = __import__("time").time() - start_time
        logger.warning(f"[条形码] 所有方法均未识别, 耗时 {elapsed:.2f}s")
        return None

    except Exception as e:
        elapsed = __import__("time").time() - start_time
        logger.error(f"[条形码] 裁剪识别失败: {e}, 耗时 {elapsed:.2f}s")
        return None


def _auto_detect_barcode_regions(image_path: str) -> list:
    """
    自动检测可能的条形码区域

    基于梯度分析找到高对比度区域（条形码特征）
    """
    try:
        import cv2
        import numpy as np

        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape

        # 分块分析梯度
        block_size = 200
        candidates = []

        for y in range(0, height, block_size):
            for x in range(0, width, block_size):
                roi = gray[y:y+block_size, x:x+block_size]
                if roi.size == 0:
                    continue

                # 计算水平梯度（条形码特征）
                grad_x = cv2.Sobel(roi, cv2.CV_64F, 1, 0, ksize=3)
                grad_x = np.absolute(grad_x)

                # 条形码区域应该有高水平梯度
                if grad_x.mean() > 20:
                    candidates.append((x, y, x+block_size, y+block_size, grad_x.mean()))

        # 按梯度排序，取前 5 个
        candidates.sort(key=lambda c: c[4], reverse=True)
        regions = [(c[0], c[1], c[2], c[3]) for c in candidates[:5]]

        logger.info(f"[条形码] 自动检测到 {len(regions)} 个候选区域")
        return regions

    except Exception as e:
        logger.debug(f"[条形码] 自动检测失败: {e}")
        # 返回默认区域（图片中心）
        from PIL import Image
        img = Image.open(image_path)
        w, h = img.size
        return [(w//4, h//4, 3*w//4, 3*h//4)]
