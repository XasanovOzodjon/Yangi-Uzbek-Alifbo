import io
import tempfile
import unittest
from pathlib import Path
import docx
import pymupdf

from converter.services.alphabet import (
    convert_to_new_alphabet,
    convert_full_to_new_alphabet,
    process_text,
    has_cyrillic,
    has_latin,
    is_mixed,
)
from converter.services.cyrillic import convert_cyrillic_to_new_latin
from converter.services.docx_service import convert_docx_file
from converter.services.pdf_service import (
    convert_pdf_file,
    PdfEmptyError,
    PdfEncryptedError,
)
from utils.misc.text_splitter import split_into_copyable_chunks


class TestAlphabetConverter(unittest.TestCase):
    def test_ch_conversion(self):
        self.assertEqual(convert_to_new_alphabet("choy"), "çoy")
        self.assertEqual(convert_to_new_alphabet("Chaqaloq"), "Çaqaloq")
        self.assertEqual(convert_to_new_alphabet("CHOY"), "ÇOY")
        self.assertEqual(convert_to_new_alphabet("kichik"), "kiçik")

    def test_sh_conversion(self):
        self.assertEqual(convert_to_new_alphabet("shaxta"), "şaxta")
        self.assertEqual(convert_to_new_alphabet("Shaxta"), "Şaxta")
        self.assertEqual(convert_to_new_alphabet("SHAXTA"), "ŞAXTA")
        self.assertEqual(convert_to_new_alphabet("quyosh"), "quyoş")

    def test_o_apostrophe_conversion(self):
        apostrophes = ["'", "ʻ", "’", "‘", "ʼ", "`", "´", "′"]
        for ap in apostrophes:
            self.assertEqual(convert_to_new_alphabet(f"o{ap}qish"), "öqiş")
            self.assertEqual(convert_to_new_alphabet(f"O{ap}qish"), "Öqiş")
            self.assertEqual(convert_to_new_alphabet(f"o{ap}zbek"), "özbek")
            self.assertEqual(convert_to_new_alphabet(f"O{ap}ZBEK"), "ÖZBEK")

    def test_g_apostrophe_conversion(self):
        apostrophes = ["'", "ʻ", "’", "‘", "ʼ", "`", "´", "′"]
        for ap in apostrophes:
            self.assertEqual(convert_to_new_alphabet(f"g{ap}alaba"), "ğalaba")
            self.assertEqual(convert_to_new_alphabet(f"G{ap}alaba"), "Ğalaba")
            self.assertEqual(convert_to_new_alphabet(f"G{ap}ALABA"), "ĞALABA")

    def test_ng_not_converted(self):
        # Yangi alifboda ng o'zgarmasdan qoladi (faqat 4 ta o'zgarish: o', g', ch, sh)
        self.assertEqual(convert_to_new_alphabet("tingla"), "tingla")
        self.assertEqual(convert_to_new_alphabet("Tingla"), "Tingla")
        self.assertEqual(convert_to_new_alphabet("TINGLA"), "TINGLA")
        self.assertEqual(convert_to_new_alphabet("singil"), "singil")

    def test_exceptions(self):
        # "yangi" va "bodring" kabi so'zlarda ham ng o'zgarmaydi
        self.assertEqual(convert_to_new_alphabet("yangi"), "yangi")
        self.assertEqual(convert_to_new_alphabet("Yangi"), "Yangi")
        self.assertEqual(convert_to_new_alphabet("YANGI"), "YANGI")
        self.assertEqual(convert_to_new_alphabet("yangilik"), "yangilik")
        self.assertEqual(convert_to_new_alphabet("yangilar"), "yangilar")
        # ch harfi ç ga aylanadi, lekin ng saqlanadi:
        self.assertEqual(convert_to_new_alphabet("yangicha"), "yangiça")
        self.assertEqual(convert_to_new_alphabet("bodring"), "bodring")
        self.assertEqual(convert_to_new_alphabet("jangovar"), "jangovar")

    def test_combined_sentence(self):
        text = "Bugun yangi O'zbekistonda chiroyli shaxta ochildi va g'alaba qozonildi."
        expected = "Bugun yangi Özbekistonda çiroyli şaxta oçildi va ğalaba qozonildi."
        self.assertEqual(convert_to_new_alphabet(text), expected)

    def test_docx_conversion(self):
        doc = docx.Document()
        doc.add_paragraph("Yangi o'qish va chiroyli bog'cha")
        table = doc.add_table(rows=1, cols=1)
        table.cell(0, 0).text = "G'alaba va shaxta"

        buf_in = io.BytesIO()
        doc.save(buf_in)
        buf_in.seek(0)

        buf_out = convert_docx_file(buf_in)
        doc_out = docx.Document(buf_out)

        self.assertEqual(doc_out.paragraphs[0].text, "Yangi öqiş va çiroyli boğça")
        self.assertEqual(doc_out.tables[0].rows[0].cells[0].text, "Ğalaba va şaxta")

    def test_pdf_conversion(self):
        doc = pymupdf.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Yangi o'qish va chiroyli bog'cha", fontsize=14)
        page.insert_text((50, 100), "G'alaba va shaxta quyosh", fontsize=12)

        pdf_bytes = doc.tobytes()
        doc.close()

        buf_in = io.BytesIO(pdf_bytes)
        buf_out = io.BytesIO()
        convert_pdf_file(buf_in, buf_out)

        doc_out = pymupdf.open(stream=buf_out.getvalue(), filetype="pdf")
        self.assertEqual(len(doc_out), 1)
        out_text = doc_out[0].get_text()
        doc_out.close()

        self.assertIn("Yangi öqiş va çiroyli boğça", out_text)
        self.assertIn("Ğalaba va şaxta quyoş", out_text)

    def test_pdf_conversion_with_paths(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            src_path = Path(tmp_dir) / "test_doc.pdf"
            doc = pymupdf.open()
            page = doc.new_page()
            page.insert_text((50, 50), "O'zbekiston shaxtasi", fontsize=12)
            doc.save(str(src_path))
            doc.close()

            res_path = convert_pdf_file(src_path)
            self.assertTrue(res_path.exists())
            self.assertEqual(res_path.name, "test_doc_yangi_alifbo.pdf")

            doc_out = pymupdf.open(str(res_path))
            out_text = doc_out[0].get_text()
            doc_out.close()
            self.assertIn("Özbekiston şaxtasi", out_text)

    def test_pdf_empty_error(self):
        doc = pymupdf.open()
        doc.new_page()
        buf_in = io.BytesIO(doc.tobytes())
        doc.close()

        buf_out = io.BytesIO()
        with self.assertRaises(PdfEmptyError):
            convert_pdf_file(buf_in, buf_out)

    def test_cyrillic_conversion(self):
        self.assertEqual(convert_cyrillic_to_new_latin("Ўзбекистон"), "Özbekiston")
        self.assertEqual(convert_cyrillic_to_new_latin("ЎЗБЕКИСТОН"), "ÖZBEKISTON")
        self.assertEqual(convert_cyrillic_to_new_latin("Шошилинч хабар"), "Şoşilinç xabar")
        self.assertEqual(convert_cyrillic_to_new_latin("Ғалаба"), "Ğalaba")
        self.assertEqual(convert_cyrillic_to_new_latin("Чўлпон"), "Çölpon")
        self.assertEqual(convert_cyrillic_to_new_latin("Ер шари"), "Yer şari")
        self.assertEqual(convert_cyrillic_to_new_latin("келди"), "keldi")
        self.assertEqual(convert_cyrillic_to_new_latin("поезд"), "poyezd")
        self.assertEqual(convert_cyrillic_to_new_latin("Ёшлар"), "Yoşlar")
        self.assertEqual(convert_cyrillic_to_new_latin("ЁШЛАР"), "YOŞLAR")
        self.assertEqual(convert_cyrillic_to_new_latin("Юлдуз"), "Yulduz")
        self.assertEqual(convert_cyrillic_to_new_latin("Янги йил"), "Yangi yil")
        self.assertEqual(convert_cyrillic_to_new_latin("аъло"), "a'lo")
        self.assertEqual(convert_cyrillic_to_new_latin("Исҳоқ"), "Ishoq")
        self.assertEqual(convert_cyrillic_to_new_latin("цирк"), "tsirk")
        self.assertEqual(convert_cyrillic_to_new_latin("июль"), "iyul")

    def test_settings_cyrillic_toggle(self):
        text = "Салом дунё"
        # Kirillcha sozlama OFF bo'lsa - o'girmaydi
        self.assertEqual(process_text(text, translate_cyrillic=False), "Салом дунё")
        # Kirillcha sozlama ON bo'lsa - yangi alifboga o'giradi
        self.assertEqual(process_text(text, translate_cyrillic=True), "Salom dunyo")

    def test_settings_mixed_toggle(self):
        text = "Bu chiroyli шаҳар va o'rmon"
        # Aralash sozlama OFF bo'lsa - faqat lotin o'giriladi, kirill qoladi
        self.assertEqual(process_text(text, translate_mixed=False), "Bu çiroyli шаҳар va örmon")
        # Aralash sozlama ON bo'lsa - ham lotin, ham kirill yangi alifboga o'giriladi
        self.assertEqual(process_text(text, translate_mixed=True), "Bu çiroyli şahar va örmon")

    def test_tag_dollar_bracket_selective(self):
        # $( matn )$: faqat shu qavs ichi o'giriladi, qolgani o'z holida qoladi, qavslar o'chiriladi
        text = "Bu matn o'zgarmasin, faqat $(chiroyli o'qish)$ o'zgarsin."
        expected = "Bu matn o'zgarmasin, faqat çiroyli öqiş o'zgarsin."
        self.assertEqual(process_text(text), expected)

        # Qavs ichida kirillcha bo'lsa ham yangi alifboga o'tkazadi
        text2 = "Ushbu $(янги шаҳар)$ qurildi va o'sdi."
        expected2 = "Ushbu yangi şahar qurildi va o'sdi."
        self.assertEqual(process_text(text2), expected2)

    def test_tag_hash_bracket_protection(self):
        # #( matn )#: shu qavs ichi o'girilmaydi, qolgani o'giriladi, qavslar o'chiriladi
        text = "Bugun #(chiroyli)# o'qishga bordik."
        expected = "Bugun chiroyli öqişga bordik."
        self.assertEqual(process_text(text), expected)

        # Ichida kirillcha himoyalangan bo'lsa
        text2 = "Bugun #(шаҳар)# chiroyli bo'ldi."
        expected2 = "Bugun шаҳар çiroyli böldi."
        self.assertEqual(process_text(text2), expected2)

    def test_multiple_tags(self):
        text1 = "A $(choy)$ B $(quyosh)$ C"
        self.assertEqual(process_text(text1), "A çoy B quyoş C")

        text2 = "#(choy)# va #(quyosh)# chiroyli"
        self.assertEqual(process_text(text2), "choy va quyosh çiroyli")

    def test_docx_with_tags_and_cyrillic(self):
        doc = docx.Document()
        doc.add_paragraph("Bu $(chiroyli o'qish)$ va o'zgarmasin.")
        doc.add_paragraph("Bu esa #(chiroyli)# o'qish.")
        table = doc.add_table(rows=1, cols=1)
        table.cell(0, 0).text = "Oddiy matn: Салом dunyo"

        buf_in = io.BytesIO()
        doc.save(buf_in)
        buf_in.seek(0)

        buf_out = convert_docx_file(buf_in, translate_mixed=True)
        doc_out = docx.Document(buf_out)

        self.assertEqual(doc_out.paragraphs[0].text, "Bu çiroyli öqiş va o'zgarmasin.")
        self.assertEqual(doc_out.paragraphs[1].text, "Bu esa chiroyli öqiş.")
        self.assertEqual(doc_out.tables[0].rows[0].cells[0].text, "Oddiy matn: Salom dunyo")

    def test_copyable_chunks_formatting(self):
        chunks = split_into_copyable_chunks("Salom dunyo!")
        self.assertEqual(chunks, ["<code>Salom dunyo!</code>"])

    def test_copyable_chunks_html_escaping(self):
        chunks = split_into_copyable_chunks("Test <salom> & 'dunyo' \"yangi\"")
        self.assertEqual(chunks, ["<code>Test &lt;salom&gt; &amp; 'dunyo' \"yangi\"</code>"])

    def test_copyable_chunks_empty(self):
        self.assertEqual(split_into_copyable_chunks(""), [])

    def test_copyable_chunks_long_text(self):
        long_text = "Çiroyli matn. " * 400
        chunks = split_into_copyable_chunks(long_text)
        self.assertGreater(len(chunks), 1)
        for chunk in chunks:
            self.assertTrue(chunk.startswith("<code>"))
            self.assertTrue(chunk.endswith("</code>"))
            self.assertLessEqual(len(chunk), 4096)


if __name__ == "__main__":
    unittest.main()
