import io
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
import docx
import pymupdf
from converter.models import TelegramUser, WordException, ConversionLog


class ApiEndpointsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_index_view(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["status"], "online")
        self.assertIn(".pdf", data["supported_documents"])

    def test_convert_api_view(self):
        payload = {"text": "Chiroyli o'qish, g'alaba va yangi maktab!"}
        response = self.client.post("/api/v1/convert/", payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertIn("converted_text", data)
        self.assertEqual(data["converted_text"], "Çiroyli öqiş, ğalaba va yangi maktab!")

    def test_convert_api_cyrillic_settings(self):
        # Cyrillic disabled by default
        res1 = self.client.post("/api/v1/convert/", {"text": "Салом дунё"}, format="json")
        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res1.json()["converted_text"], "Салом дунё")

        # Cyrillic enabled
        res2 = self.client.post(
            "/api/v1/convert/",
            {"text": "Салом дунё", "translate_cyrillic": True},
            format="json"
        )
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.json()["converted_text"], "Salom dunyo")

        # Selective tag formatting
        res3 = self.client.post(
            "/api/v1/convert/",
            {"text": "Salom $(chiroyli o'qish)$ va dunyo"},
            format="json"
        )
        self.assertEqual(res3.status_code, status.HTTP_200_OK)
        self.assertEqual(res3.json()["converted_text"], "Salom çiroyli öqiş va dunyo")

    def test_convert_file_api_docx(self):
        doc = docx.Document()
        doc.add_paragraph("O'qituvchi va yangi o'quvchi")
        buf = io.BytesIO()
        doc.save(buf)
        buf.seek(0)

        uploaded = SimpleUploadedFile("dars.docx", buf.getvalue(), content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        response = self.client.post("/api/v1/convert-file/", {"file": uploaded}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("attachment; filename=\"dars_yangi_alifbo.docx\"", response["Content-Disposition"])

        out_doc = docx.Document(io.BytesIO(response.content))
        self.assertEqual(out_doc.paragraphs[0].text, "Öqituvçi va yangi öquvçi")

    def test_convert_file_api_pdf(self):
        pdf_doc = pymupdf.open()
        p = pdf_doc.new_page()
        p.insert_text((50, 50), "O'zbekiston shaxtasi va bog'cha")
        pdf_bytes = pdf_doc.tobytes()
        pdf_doc.close()

        uploaded = SimpleUploadedFile("hujjat.pdf", pdf_bytes, content_type="application/pdf")
        response = self.client.post("/api/v1/convert-file/", {"file": uploaded}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("attachment; filename=\"hujjat_yangi_alifbo.pdf\"", response["Content-Disposition"])

        out_pdf = pymupdf.open(stream=response.content, filetype="pdf")
        self.assertIn("Özbekiston şaxtasi va boğça", out_pdf[0].get_text())
        out_pdf.close()

    def test_convert_file_invalid_type(self):
        uploaded = SimpleUploadedFile("test.txt", b"salom", content_type="text/plain")
        response = self.client.post("/api/v1/convert-file/", {"file": uploaded}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_stats_api_view(self):
        user = TelegramUser.objects.create(telegram_id=123456, first_name="Ali")
        ConversionLog.objects.create(user=user, content_type="text", original_text="salom", converted_text="salom")
        ConversionLog.objects.create(user=user, content_type="pdf", original_text="test.pdf", converted_text="test_yangi.pdf")

        response = self.client.get("/api/v1/stats/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["total_users"], 1)
        self.assertEqual(data["total_conversions"], 2)
        self.assertEqual(data["pdf_conversions"], 1)

    def test_exceptions_api_view(self):
        WordException.objects.create(word="yangi", category="ng")
        response = self.client.get("/api/v1/exceptions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get("results", data)
        self.assertTrue(any(item["word"] == "yangi" for item in results))
