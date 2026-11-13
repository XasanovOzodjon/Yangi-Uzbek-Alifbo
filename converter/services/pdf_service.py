import io
import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import pymupdf

from .alphabet import process_text

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FONTS_DIR = BASE_DIR / "data" / "fonts"


class PdfConversionError(Exception):
    pass


class PdfEncryptedError(PdfConversionError):
    pass


class PdfEmptyError(PdfConversionError):
    pass


def _get_font_info(is_bold: bool = False, is_italic: bool = False) -> Tuple[str, str]:
    if is_bold and is_italic:
        fname = "vera_bold_italic"
        filename = "VeraBI.ttf"
    elif is_bold:
        fname = "vera_bold"
        filename = "VeraBd.ttf"
    elif is_italic:
        fname = "vera_italic"
        filename = "VeraIt.ttf"
    else:
        fname = "vera_regular"
        filename = "Vera.ttf"

    font_path = FONTS_DIR / filename
    if font_path.exists():
        return fname, str(font_path)

    try:
        import reportlab
        rl_path = Path(reportlab.__file__).parent / "fonts" / filename
        if rl_path.exists():
            return fname, str(rl_path)
    except Exception:
        pass

    return fname, ""


def _merge_adjacent_spans(spans: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    for span in spans:
        text = span.get("text", "")
        if not text:
            continue

        if not merged:
            merged.append(dict(span))
            continue

        prev = merged[-1]
        same_font = prev.get("font") == span.get("font")
        same_size = abs(prev.get("size", 0) - span.get("size", 0)) < 0.5
        same_color = prev.get("color") == span.get("color")
        same_flags = prev.get("flags") == span.get("flags")

        prev_bbox = prev["bbox"]
        span_bbox = span["bbox"]
        same_baseline = abs(prev_bbox[1] - span_bbox[1]) < 3 and abs(prev_bbox[3] - span_bbox[3]) < 3
        is_adjacent = span_bbox[0] >= prev_bbox[0] and (span_bbox[0] - prev_bbox[2]) < (span.get("size", 12) * 1.5)

        if same_font and same_size and same_color and same_flags and same_baseline and is_adjacent:
            prev["text"] += span["text"]
            prev["bbox"] = (
                min(prev_bbox[0], span_bbox[0]),
                min(prev_bbox[1], span_bbox[1]),
                max(prev_bbox[2], span_bbox[2]),
                max(prev_bbox[3], span_bbox[3]),
            )
        else:
            merged.append(dict(span))

    return merged


def convert_pdf_file(
    input_source: Union[str, Path, io.BytesIO, bytes],
    output_dest: Optional[Union[str, Path, io.BytesIO]] = None,
    return_char_count: bool = False,
    translate_cyrillic: bool = False,
    translate_mixed: bool = False
) -> Union[Path, io.BytesIO, Tuple[Union[Path, io.BytesIO], int]]:
    if isinstance(input_source, (str, Path)):
        doc = pymupdf.open(str(input_source))
    elif isinstance(input_source, io.BytesIO):
        doc = pymupdf.open(stream=input_source.getvalue(), filetype="pdf")
    elif isinstance(input_source, bytes):
        doc = pymupdf.open(stream=input_source, filetype="pdf")
    else:
        raise ValueError(f"Notogri kirish turi: {type(input_source)}")

    try:
        if doc.is_encrypted:
            if not doc.authenticate(""):
                raise PdfEncryptedError("PDF parol bilan himoyalangan.")

        total_chars = 0

        for page in doc:
            data = page.get_text("dict")
            blocks = data.get("blocks", [])

            spans_to_replace = []

            for block in blocks:
                if block.get("type") != 0:
                    continue

                for line in block.get("lines", []):
                    line_dir = line.get("dir", (1.0, 0.0))
                    angle = 0
                    if line_dir != (1.0, 0.0):
                        cos_val, sin_val = line_dir
                        angle = round(math.degrees(math.atan2(sin_val, cos_val))) % 360

                    raw_spans = line.get("spans", [])
                    merged_spans = _merge_adjacent_spans(raw_spans)

                    for span in merged_spans:
                        raw_text = span.get("text", "")
                        if not raw_text.strip():
                            continue

                        total_chars += len(raw_text)
                        converted_text = process_text(
                            raw_text,
                            translate_cyrillic=translate_cyrillic,
                            translate_mixed=translate_mixed
                        )

                        bbox = span.get("bbox")
                        if not bbox:
                            continue

                        rect = pymupdf.Rect(bbox)
                        origin = span.get("origin", (bbox[0], bbox[3]))
                        size = span.get("size", 11.0)
                        if size <= 0:
                            size = 11.0

                        color_int = span.get("color", 0)
                        try:
                            rgb = pymupdf.sRGB_to_rgb(color_int)
                            color_tuple = (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
                        except Exception:
                            color_tuple = (0.0, 0.0, 0.0)

                        flags = span.get("flags", 0)
                        font_name_str = span.get("font", "").lower()
                        is_bold = bool(flags & 16) or ("bold" in font_name_str) or ("black" in font_name_str)
                        is_italic = bool(flags & 2) or ("italic" in font_name_str) or ("oblique" in font_name_str)

                        font_alias, font_file = _get_font_info(is_bold=is_bold, is_italic=is_italic)

                        page.add_redact_annot(rect)

                        spans_to_replace.append({
                            "origin": origin,
                            "text": converted_text,
                            "font_alias": font_alias,
                            "font_file": font_file,
                            "size": size,
                            "color": color_tuple,
                            "angle": angle,
                        })

            if spans_to_replace:
                page.apply_redactions(images=0)

                for item in spans_to_replace:
                    try:
                        page.insert_text(
                            point=item["origin"],
                            text=item["text"],
                            fontname=item["font_alias"],
                            fontfile=item["font_file"] if item["font_file"] else None,
                            fontsize=item["size"],
                            color=item["color"],
                            rotate=item["angle"],
                        )
                    except Exception:
                        try:
                            page.insert_text(
                                point=item["origin"],
                                text=item["text"],
                                fontsize=item["size"],
                            )
                        except Exception:
                            pass

        if total_chars == 0:
            raise PdfEmptyError("PDF faylda matn topilmadi.")

        if output_dest is None:
            if isinstance(input_source, (str, Path)):
                inp_path = Path(input_source)
                output_dest = inp_path.parent / f"{inp_path.stem}_yangi_alifbo{inp_path.suffix}"
            else:
                output_dest = io.BytesIO()

        if isinstance(output_dest, (str, Path)):
            doc.save(str(output_dest), garbage=4, deflate=True)
            res = Path(output_dest)
        elif isinstance(output_dest, io.BytesIO):
            out_bytes = doc.tobytes(garbage=4, deflate=True)
            output_dest.write(out_bytes)
            output_dest.seek(0)
            res = output_dest
        else:
            doc.save(output_dest, garbage=4, deflate=True)
            res = output_dest

        if return_char_count:
            return res, total_chars
        return res

    finally:
        doc.close()
