# line_bot/tasks.py
import os
import json
from celery import Celery
from weasyprint import HTML
from datetime import datetime, timedelta

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
    TextMessage,
    MessageAction
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
        
        # Step 4: Send PDF to user
        _send_pdf(user_id, pdf_path, access_token)
        
        # Step 5: Cleanup
        if file_path and os.path.exists(file_path):
            _schedule_cleanup(file_path)
        _schedule_cleanup(pdf_path)
        
    except Exception as e:
        error_msg = f"處理過程發生錯誤\n\n{str(e)}"
        _send_message(user_id, error_msg, access_token)


def _generate_pdf(markdown_content: str, user_id: str) -> str:
    """
    Generate PDF from Markdown content
    
    Args:
        markdown_content: Markdown text
        user_id: LINE user ID for filename
        
    Returns:
        Path to generated PDF file
    """
    # Convert Markdown to HTML with styling
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif;
                line-height: 1.8;
                padding: 40px;
                max-width: 800px;
                margin: 0 auto;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                margin-top: 30px;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 8px;
            }}
            strong {{
                color: #2980b9;
            }}
            ul, ol {{
                margin-left: 20px;
            }}
            li {{
                margin-bottom: 8px;
            }}
            code {{
                background-color: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
            }}
        </style>
    </head>
    <body>
        {_markdown_to_html(markdown_content)}
    </body>
    </html>
    """
    
    # Generate PDF
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"result_{user_id}_{timestamp}.pdf"
    pdf_path = os.path.join("temp", "outputs", pdf_filename)
    
    HTML(string=html_content).write_pdf(pdf_path)
    
    return pdf_path


def _markdown_to_html(markdown_text: str) -> str:
    """
    Simple Markdown to HTML converter
    
    Args:
        markdown_text: Markdown formatted text
        
    Returns:
        HTML string
    """
    import re
    
    html = markdown_text
    
    # Headers
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    
    # Bold
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # Lists (unordered)
    html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    html = re.sub(r'(<li>.*</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)
    
    # Lists (ordered)
    html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # Paragraphs
    html = re.sub(r'\n\n', r'</p><p>', html)
    html = '<p>' + html + '</p>'
    
    # Line breaks
    html = html.replace('\n', '<br>')
    
    return html


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


def _send_pdf(user_id: str, pdf_path: str, access_token: str):
    """Send PDF file to user"""
    # Note: LINE Bot SDK v3 doesn't support direct file upload via API
    # We need to host the file and send a download link
    # For now, send a message with file path
    
    message = f"✅ 處理完成！\n\n檔案已生成：{os.path.basename(pdf_path)}\n\n⚠️ 注意：目前需要手動實作檔案傳送功能"
    _send_message(user_id, message, access_token)


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