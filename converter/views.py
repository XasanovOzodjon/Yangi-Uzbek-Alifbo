import io
import logging
from pathlib import Path
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import TelegramUser, ConversionLog, WordException
from .serializers import (
    ConversionLogSerializer,
    TelegramUserSerializer,
    TextConversionSerializer,
    WordExceptionSerializer,
)
from .services.alphabet import convert_to_new_alphabet, default_converter
from .services.docx_service import convert_docx_file
from .services.pdf_service import convert_pdf_file, PdfConversionError, PdfEmptyError, PdfEncryptedError

logger = logging.getLogger(__name__)


def index_view(request):
    """Veb-sayt bosh sahifasi (kelgusida sayt uchun)."""
    user_count = TelegramUser.objects.count()
    conversion_count = ConversionLog.objects.count()
    exceptions_count = WordException.objects.filter(is_active=True).count()
    
    return JsonResponse({
        "status": "online",
        "service": "Yangi O'zbek Alifbosi Bot & Web API",
        "supported_documents": [".docx", ".pdf"],
        "rules": {
            "Ch, ch": "Ç, ç",
            "Sh, sh": "Ş, ş",
            "Oʻ, oʻ (O', o')": "Ö, ö",
            "Gʻ, gʻ (G', g')": "Ğ, ğ",
        },
        "stats": {
            "total_users": user_count,
            "total_conversions": conversion_count,
            "active_exceptions": exceptions_count
        },
        "api_endpoints": {
            "convert": "/api/v1/convert/",
            "convert_file": "/api/v1/convert-file/",
            "exceptions": "/api/v1/exceptions/",
            "stats": "/api/v1/stats/",
            "admin": "/admin/"
        }
    })


class ConvertTextAPIView(APIView):
    """
    Matnni Yangi O'zbek Alifbosiga o'girish uchun REST API endpoint.
    POST: {"text": "Chiroyli o'qish va yangi g'alaba"}
    """
    def post(self, request, *args, **kwargs):
        serializer = TextConversionSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ConvertFileAPIView(APIView):
    """
    Word (.docx) va PDF (.pdf) hujjatlarini Yangi O'zbek Alifbosiga o'girish uchun API endpoint.
    POST (multipart/form-data): file=<file>
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "Iltimos, 'file' maydonida fayl yuboring."}, status=status.HTTP_400_BAD_REQUEST)

        file_name = uploaded_file.name
        suffix = Path(file_name).suffix.lower()
        stem = Path(file_name).stem

        if suffix not in [".docx", ".pdf"]:
            return Response(
                {"error": "Faqat Word (.docx) va PDF (.pdf) fayllar qabul qilinadi."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            input_bytes = io.BytesIO(uploaded_file.read())
            output_bytes = io.BytesIO()

            if suffix == ".docx":
                convert_docx_file(input_bytes, output_bytes)
                content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                log_type = "document"
            else:
                convert_pdf_file(input_bytes, output_bytes)
                content_type = "application/pdf"
                log_type = "pdf"

            output_bytes.seek(0)
            new_filename = f"{stem}_yangi_alifbo{suffix}"

            ConversionLog.objects.create(
                content_type=log_type,
                file_name=file_name,
                char_count=uploaded_file.size
            )

            response = HttpResponse(output_bytes.getvalue(), content_type=content_type)
            response["Content-Disposition"] = f'attachment; filename="{new_filename}"'
            return response

        except (PdfEmptyError, PdfEncryptedError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Fayl konvertatsiya xatoligi: {e}")
            return Response({"error": f"Faylni o'girishda xatolik yuz berdi: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WordExceptionViewSet(viewsets.ModelViewSet):
    """
    Istisno so'zlarni boshqarish uchun REST API (CRUD).
    """
    queryset = WordException.objects.all()
    serializer_class = WordExceptionSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        default_converter.reload_exceptions()

    def perform_update(self, serializer):
        instance = serializer.save()
        default_converter.reload_exceptions()

    def perform_destroy(self, instance):
        super().perform_destroy(instance)
        default_converter.reload_exceptions()


class StatsAPIView(APIView):
    """
    Bot va tizim statistikasi API si.
    """
    def get(self, request, *args, **kwargs):
        return Response({
            "total_users": TelegramUser.objects.count(),
            "active_users": TelegramUser.objects.filter(is_active=True).count(),
            "total_conversions": ConversionLog.objects.count(),
            "text_conversions": ConversionLog.objects.filter(content_type="text").count(),
            "media_conversions": ConversionLog.objects.filter(content_type__in=["photo", "video"]).count(),
            "docx_conversions": ConversionLog.objects.filter(content_type="document").count(),
            "pdf_conversions": ConversionLog.objects.filter(content_type="pdf").count(),
            "exceptions_count": WordException.objects.count(),
        })
