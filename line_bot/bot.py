# line_bot/bot.py
import os
from flask import Flask, request, abort
from datetime import datetime

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    FileMessageContent
)

from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from line_bot.file_extractor import FileExtractor
from line_bot.tasks import process_content_task

app = Flask(__name__)

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Temp directories
TEMP_UPLOAD_DIR = 'temp/uploads'
TEMP_OUTPUT_DIR = 'temp/outputs'

# Ensure directories exist
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)
os.makedirs(TEMP_OUTPUT_DIR, exist_ok=True)


@app.route("/callback", methods=['POST'])
def callback():
    """LINE webhook callback endpoint"""
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    
    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event):
    """Handle text message from user"""
    user_id = event.source.user_id
    text_content = event.message.text.strip()
    
    if not text_content:
        reply_user(event.reply_token, "請輸入有效的文字內容")
        return
    
    # Reply immediately
    reply_user(event.reply_token, "📝 收到文字內容，開始處理中...\n\n處理完成後會自動傳送結果給您。")
    
    # Process async
    process_content_task.delay(
        user_id=user_id,
        content=text_content,
        access_token=LINE_CHANNEL_ACCESS_TOKEN
    )


@handler.add(MessageEvent, message=FileMessageContent)
def handle_file_message(event):
    """Handle file upload from user"""
    user_id = event.source.user_id
    message_id = event.message.id
    file_name = event.message.file_name
    
    # Check file extension
    _, ext = os.path.splitext(file_name)
    if ext.lower() not in FileExtractor.SUPPORTED_FORMATS:
        reply_user(
            event.reply_token,
            f"❌ 不支援的檔案格式：{ext}\n\n"
            f"支援的格式：{', '.join(FileExtractor.SUPPORTED_FORMATS)}"
        )
        return
    
    try:
        # Download file
        file_path = _download_file(message_id, file_name)
        
        # Validate file
        is_valid, error_msg = FileExtractor.validate_file(file_path)
        if not is_valid:
            reply_user(event.reply_token, f"❌ {error_msg}")
            if os.path.exists(file_path):
                os.remove(file_path)
            return
        
        # Extract content
        content = FileExtractor.extract(file_path)
        
        if not content:
            reply_user(event.reply_token, "❌ 檔案內容為空，無法處理")
            os.remove(file_path)
            return
        
        # Reply immediately
        reply_user(
            event.reply_token,
            f"📄 收到檔案：{file_name}\n\n"
            f"開始處理中...\n\n"
            f"處理完成後會自動傳送結果給您。"
        )
        
        # Process async
        process_content_task.delay(
            user_id=user_id,
            content=content,
            access_token=LINE_CHANNEL_ACCESS_TOKEN,
            file_path=file_path
        )
        
    except Exception as e:
        reply_user(
            event.reply_token,
            f"❌ 檔案處理失敗\n\n{str(e)}"
        )
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)


def _download_file(message_id: str, file_name: str) -> str:
    """
    Download file from LINE server
    
    Args:
        message_id: LINE message ID
        file_name: Original file name
        
    Returns:
        Path to downloaded file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{timestamp}_{file_name}"
    file_path = os.path.join(TEMP_UPLOAD_DIR, safe_filename)
    
    with ApiClient(configuration) as api_client:
        blob_client = MessagingApiBlob(api_client)
        file_content = blob_client.get_message_content(message_id)
        
        with open(file_path, "wb") as f:
            f.write(file_content)
    
    return file_path


def reply_user(reply_token: str, text: str):
    """Reply message to user"""
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token=reply_token,
                messages=[TextMessage(text=text)]
            )
        )


if __name__ == "__main__":
    print("LINE Bot server starting...")
    print(f"Temp upload dir: {TEMP_UPLOAD_DIR}")
    print(f"Temp output dir: {TEMP_OUTPUT_DIR}")
    app.run(host='0.0.0.0', port=5000, debug=True)