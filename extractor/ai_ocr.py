from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class OcrLine:
    text: str
    confidence: float


_PADDLE_OCR_CACHE: Dict[str, "PaddleOCR"] = {}


def _get_paddle_ocr(lang: str):
    import os

    # Avoid slow/fragile model hoster connectivity checks at import time.
    os.environ.setdefault("PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK", "True")

    try:
        from paddleocr import PaddleOCR  # type: ignore
    except Exception as e:  # pragma: no cover
        raise RuntimeError(
            "PaddleOCR is not installed. Install it with: pip install paddleocr paddlepaddle"
        ) from e

    if lang not in _PADDLE_OCR_CACHE:
        _PADDLE_OCR_CACHE[lang] = PaddleOCR(use_angle_cls=True, lang=lang, show_log=False)
    return _PADDLE_OCR_CACHE[lang]


def ocr_paddle(
    pil_image,
    *,
    langs: Iterable[str] = ("hi", "en"),
    min_confidence: float = 0.30,
) -> str:
    """
    OCR a PIL image using PaddleOCR.

    We run OCR for each language in `langs` and concatenate the recognized lines.
    This helps on mixed Hindi+English scans without assuming fixed layout.
    """
    import numpy as np

    rgb = pil_image.convert("RGB")
    np_img = np.array(rgb)
    # PaddleOCR expects BGR (OpenCV-style)
    bgr = np_img[:, :, ::-1]

    collected: List[OcrLine] = []

    for lang in langs:
        ocr = _get_paddle_ocr(lang)
        result = ocr.ocr(bgr, cls=True)
        if not result:
            continue

        # result: List[List[ [box], (text, conf) ]]
        for page in result:
            for item in page:
                if not item or len(item) < 2:
                    continue
                text_conf = item[1]
                if not text_conf or len(text_conf) < 2:
                    continue
                text = (text_conf[0] or "").strip()
                conf = float(text_conf[1] or 0.0)
                if text and conf >= min_confidence:
                    collected.append(OcrLine(text=text, confidence=conf))

    return "\n".join(line.text for line in collected).strip() + "\n"


def ocr_tesseract(
    pil_image,
    *,
    tesseract_cmd: Optional[str] = None,
    lang: str = "hin+eng",
) -> str:
    import pytesseract

    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    return (pytesseract.image_to_string(pil_image, lang=lang) or "").strip() + "\n"

