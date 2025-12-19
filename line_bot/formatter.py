# line_bot/formatter.py
import json
from typing import Dict, Any


class ResultFormatter:
    """Format Agent JSON results into readable Markdown"""
    
    @staticmethod
    def format(result_data: Dict[str, Any]) -> str:
        """
        Convert Agent result to Markdown format
        
        Args:
            result_data: Output from app.process(), contains:
                - selected_task_type: "KEYPOINT" or "SYNTHESIS"
                - final_result_text: JSON string
                
        Returns:
            Formatted Markdown string
        """
        task_type = result_data.get("selected_task_type", "")
        final_result_text = result_data.get("final_result_text", "")
        
        if not final_result_text:
            return "# 處理結果\n\n無法生成結果，請檢查輸入內容。"
        
        try:
            result_obj = json.loads(final_result_text)
        except json.JSONDecodeError:
            return f"# 處理結果\n\n{final_result_text}"
        
        if task_type == "KEYPOINT":
            return ResultFormatter._format_keypoint(result_obj)
        elif task_type == "SYNTHESIS":
            return ResultFormatter._format_synthesis(result_obj)
        else:
            return ResultFormatter._format_generic(result_obj)
    
    @staticmethod
    def _format_keypoint(data: Dict[str, Any]) -> str:
        """Format keypoint extraction result"""
        protagonist = data.get("protagonist", "未知")
        focus_aspects = data.get("focus_aspects", [])
        keypoints = data.get("keypoints", [])
        
        md = "# 摘要報告\n\n"
        md += f"**主幹：** {protagonist}\n\n"
        
        if focus_aspects:
            md += "**關注面向：**\n"
            for aspect in focus_aspects:
                md += f"- {aspect}\n"
            md += "\n"
        
        if keypoints:
            md += "**重點整理：**\n\n"
            for i, point in enumerate(keypoints, 1):
                md += f"{i}. {point}\n\n"
        else:
            md += "*無法提取重點*\n"
        
        return md
    
    @staticmethod
    def _format_synthesis(data: Dict[str, Any]) -> str:
        """Format synthesis analysis result"""
        protagonist = data.get("protagonist", "未知")
        focus_aspects = data.get("focus_aspects", [])
        synthesis = data.get("synthesis", "")
        added_context = data.get("added_context", [])
        examples = data.get("examples", [])
        takeaways = data.get("takeaways", [])
        
        md = "# 綜合分析\n\n"
        md += f"**主幹：** {protagonist}\n\n"
        
        if focus_aspects:
            md += "**關注面向：**\n"
            for aspect in focus_aspects:
                md += f"- {aspect}\n"
            md += "\n"
        
        if synthesis:
            md += "## 核心解析\n\n"
            md += f"{synthesis}\n\n"
        
        if added_context:
            md += "## 補充背景\n\n"
            for context in added_context:
                md += f"- {context}\n"
            md += "\n"
        
        if examples:
            md += "## 實例說明\n\n"
            for example in examples:
                md += f"- {example}\n"
            md += "\n"
        
        if takeaways:
            md += "## 關鍵要點\n\n"
            for takeaway in takeaways:
                md += f"- {takeaway}\n"
            md += "\n"
        
        return md
    
    @staticmethod
    def _format_generic(data: Dict[str, Any]) -> str:
        """Generic formatter for unknown result types"""
        md = "# 處理結果\n\n"
        md += "```json\n"
        md += json.dumps(data, ensure_ascii=False, indent=2)
        md += "\n```\n"
        return md