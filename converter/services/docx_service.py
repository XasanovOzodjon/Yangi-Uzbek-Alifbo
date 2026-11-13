"""
Word (.docx) fayllarni Yangi O'zbek Alifbosiga o'girish xizmati.
"""

import io
import logging
from pathlib import Path
from typing import Union
import docx

from .alphabet import process_text

logger = logging.getLogger(__name__)


def _convert_paragraph(paragraph, translate_cyrillic: bool = False, translate_mixed: bool = False):
    """
    Paragraf ichidagi matnni formatlashni saqlab qolgan holda o'giradi.
    $( )$ va #( )# qavslari hamda kirill/aralash sozlamalarini qo'llab-quvvatlaydi.
    """
    if not paragraph.runs:
        if paragraph.text:
            paragraph.text = process_text(paragraph.text, translate_cyrillic, translate_mixed)
        return

    full_text = paragraph.text
    if "$(" not in full_text and "#(" not in full_text:
        for run in paragraph.runs:
            if run.text:
                run.text = process_text(run.text, translate_cyrillic, translate_mixed)
        return

    # Teglar mavjud bo'lganda:
    has_split_tag = False
    for run in paragraph.runs:
        t = run.text or ""
        if (t.count("$(") != t.count(")$")) or (t.count("#(") != t.count(")#")):
            has_split_tag = True
            break

    if not has_split_tag:
        for run in paragraph.runs:
            if run.text:
                run.text = process_text(run.text, translate_cyrillic, translate_mixed)
    else:
        converted = process_text(full_text, translate_cyrillic, translate_mixed)
        if paragraph.runs:
            paragraph.runs[0].text = converted
            for r in paragraph.runs[1:]:
                r.text = ""


def _convert_table(table, translate_cyrillic: bool = False, translate_mixed: bool = False):
    """
    Jadval ichidagi barcha kataklar matnini o'giradi.
    """
    for row in table.rows:
        for cell in row.cells:
            for p in cell.paragraphs:
                _convert_paragraph(p, translate_cyrillic, translate_mixed)
            for sub_table in cell.tables:
                _convert_table(sub_table, translate_cyrillic, translate_mixed)


def convert_docx_file(
    input_source: Union[str, Path, io.BytesIO],
    output_dest: Union[str, Path, io.BytesIO] = None,
    translate_cyrillic: bool = False,
    translate_mixed: bool = False
) -> Union[Path, io.BytesIO]:
    doc = docx.Document(input_source)

    # 1. Asosiy matn paragraflari
    for p in doc.paragraphs:
        _convert_paragraph(p, translate_cyrillic, translate_mixed)

    # 2. Jadvallar
    for t in doc.tables:
        _convert_table(t, translate_cyrillic, translate_mixed)

    # 3. Headers va Footers
    for section in doc.sections:
        if section.header:
            for hp in section.header.paragraphs:
                _convert_paragraph(hp, translate_cyrillic, translate_mixed)
            for ht in section.header.tables:
                _convert_table(ht, translate_cyrillic, translate_mixed)

        if section.footer:
            for fp in section.footer.paragraphs:
                _convert_paragraph(fp, translate_cyrillic, translate_mixed)
            for ft in section.footer.tables:
                _convert_table(ft, translate_cyrillic, translate_mixed)

    if output_dest is None:
        if isinstance(input_source, (str, Path)):
            inp_path = Path(input_source)
            output_dest = inp_path.parent / f"{inp_path.stem}_yangi_alifbo{inp_path.suffix}"
        else:
            output_dest = io.BytesIO()

    doc.save(output_dest)
    if isinstance(output_dest, io.BytesIO):
        output_dest.seek(0)
    return output_dest
