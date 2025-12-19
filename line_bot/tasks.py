# line_bot/tasks.py
import os
import json
from celery import Celery
from datetime import datetime, timedelta
import markdown2
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT

from config import REDIS_HOST, REDIS_PORT
from __init__ import app as agent_app
from line_bot.formatter import ResultFormatter
from line_bot.file_extractor import FileExtractor

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    TextMessage
)

from linebot.v3.messaging import MessagingApiBlob

# Initialize Celery
celery_app = Celery(
    'line_bot_tasks',
    broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/0',
    backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/0'
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Taipei',
    enable_utc=True,
)


@celery_app.task(bind=True)
def process_content_task(self, user_id: str, content: str, access_token: str, file_path: str = None):
    """
    Async task to process user content through Agent
    
    Args:
        user_id: LINE user ID
        content: Text content to process
        access_token: LINE channel access token
        file_path: Optional file path if content was extracted from file
    """
    try:
        # Step 1: Process through Agent
        result = agent_app.process(content)
        
        if not result["success"]:
            error_msg = f"處理失敗\n\n{result['error']}"
            _send_message(user_id, error_msg, access_token)
            return
        
        # Step 2: Format to Markdown
        markdown_content = ResultFormatter.format(result["data"])
        
        # Step 3: Convert to PDF
        pdf_path = _generate_pdf(markdown_content, user_id)
        
        # Step 4: Send download link to user
        pdf_filename = os.path.basename(pdf_path)
        # Get ngrok URL from environment or use default
        download_url = f"https://unmorbidly-uncankered-addison.ngrok-free.dev/download/{pdf_filename}"
        success_msg = f"✅ 處理完成！\n\n📥 點擊下載 PDF：\n{download_url}\n\n⏰ 連結 24 小時內有效"
        _send_message(user_id, success_msg, access_token)
        # Step 5: Cleanup
        if file_path and os.path.exists(file_path):
            _schedule_cleanup(file_path)
        _schedule_cleanup(pdf_path)
        
    except Exception as e:
        error_msg = f"處理過程發生錯誤\n\n{str(e)}"
        _send_message(user_id, error_msg, access_token)


def _generate_pdf(markdown_content: str, user_id: str) -> str:
    """
    Generate PDF from Markdown content using ReportLab
    
    Args:
        markdown_content: Markdown text
        user_id: LINE user ID for filename
        
    Returns:
        Path to generated PDF file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"result_{user_id}_{timestamp}.pdf"
    pdf_path = os.path.join("temp", "outputs", pdf_filename)
    
    # Register Chinese font
    try:
        # Try to register Microsoft JhengHei (微軟正黑體)
        font_paths = [
            'C:/Windows/Fonts/msjh.ttc',  # Windows 10/11
            'C:/Windows/Fonts/msjh.ttf',  # Older Windows
        ]
        
        font_registered = False
        for font_path in font_paths:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('MSJHFont', font_path))
                font_registered = True
                break
        
        if not font_registered:
            raise Exception("Microsoft JhengHei font not found")
            
    except Exception as e:
        raise Exception(f"Failed to register Chinese font: {str(e)}")
    
    # Create PDF document
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    story = []
    
    # Define styles with Chinese font
    styles = getSampleStyleSheet()
    
    # Custom styles for Chinese text
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName='MSJHFont',
        fontSize=18,
        textColor='#2c3e50',
        spaceAfter=20,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName='MSJHFont',
        fontSize=14,
        textColor='#34495e',
        spaceAfter=12,
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontName='MSJHFont',
        fontSize=11,
        leading=18,
        alignment=TA_LEFT,
    )
    
    # Parse markdown and convert to PDF elements
    lines = markdown_content.split('\n')
    
    for line in lines:
        line = line.strip()
        
        if not line:
            story.append(Spacer(1, 0.2*inch))
            continue
        
        # Headers
        if line.startswith('# '):
            text = line[2:].strip()
            story.append(Paragraph(text, title_style))
        elif line.startswith('## '):
            text = line[3:].strip()
            story.append(Paragraph(text, heading_style))
        # Bold text
        elif line.startswith('**') and line.endswith('**'):
            text = line[2:-2].strip()
            story.append(Paragraph(f"<b>{text}</b>", body_style))
        # List items
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            story.append(Paragraph(f"• {text}", body_style))
        # Numbered list
        elif line[0].isdigit() and '. ' in line:
            story.append(Paragraph(line, body_style))
        # Normal text
        else:
            story.append(Paragraph(line, body_style))
    
    # Build PDF
    doc.build(story)
    
    return pdf_path

def _send_message(user_id: str, message: str, access_token: str):
    """Send text message to user"""
    configuration = Configuration(access_token=access_token)
    
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.push_message(
            PushMessageRequest(
                to=user_id,
                messages=[TextMessage(text=message)]
            )
        )


def _schedule_cleanup(file_path: str, hours: int = 24):
    """Schedule file cleanup after specified hours"""
    cleanup_task.apply_async(args=[file_path], countdown=hours * 3600)


@celery_app.task
def cleanup_task(file_path: str):
    """Delete file if exists"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass