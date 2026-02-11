"""
Генерация PDF сертификатов о прохождении теста.
Production-ready с встроенными шрифтами.
"""
import io
import logging
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from config.settings import settings
from .models import CurrentTestState

logger = logging.getLogger(__name__)

# Загрузка встроенного шрифта
FONT_PATH = Path(__file__).parent / "fonts" / "DejaVuSans.ttf"

def register_fonts():
    """Регистрация русских шрифтов для PDF."""
    try:
        if FONT_PATH.exists():
            pdfmetrics.registerFont(TTFont('DejaVu', str(FONT_PATH)))
            logger.info(f"✅ Шрифт загружен: {FONT_PATH}")
            return 'DejaVu', 'DejaVu'
        else:
            logger.warning(f"⚠️ Шрифт не найден: {FONT_PATH}, используется Helvetica")
            return 'Helvetica', 'Helvetica-Bold'
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки шрифта: {e}")
        return 'Helvetica', 'Helvetica-Bold'


async def generate_certificate(test_state: CurrentTestState, user_id: int) -> io.BytesIO:
    """
    Генерирует PDF сертификат и возвращает BytesIO buffer.
    
    Returns:
        io.BytesIO: PDF в памяти
    """
    font_regular, font_bold = register_fonts()
    
    # Создаём PDF в памяти
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    # Заголовок
    c.setFont(font_bold, 24)
    c.setFillColor(colors.HexColor("#1a5490"))
    c.drawCentredString(width / 2, height - 100, "СЕРТИФИКАТ")
    
    c.setFont(font_regular, 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width / 2, height - 130, "о прохождении тестирования")
    
    # Данные
    y_position = height - 200
    c.setFont(font_bold, 12)
    
    data_fields = [
        ("ФИО:", test_state.full_name),
        ("Должность:", test_state.position),
        ("Подразделение:", test_state.department),
        ("Специализация:", test_state.specialization.upper()),
        ("Уровень сложности:", test_state.difficulty.value.capitalize()),
        ("", ""),
        ("Оценка:", test_state.grade.upper()),
        ("Правильных ответов:", f"{test_state.correct_count} из {test_state.total_questions}"),
        ("Процент:", f"{test_state.percentage:.1f}%"),
        ("Время:", test_state.elapsed_time),
        ("Дата:", datetime.now().strftime("%d.%m.%Y")),
    ]
    
    for label, value in data_fields:
        if label:
            c.setFont(font_bold, 11)
            c.drawString(100, y_position, label)
            c.setFont(font_regular, 11)
            c.drawString(280, y_position, value)
        y_position -= 25
    
    c.setFont(font_regular, 9)
    c.setFillColor(colors.grey)
    c.drawCentredString(width / 2, 50, f"Telegram Bot • ID: {user_id}")
    
    c.save()
    
    # Возвращаем buffer с позицией в начале
    buffer.seek(0)
    logger.info(f"✅ Сертификат сгенерирован для пользователя {user_id}")
    return buffer
