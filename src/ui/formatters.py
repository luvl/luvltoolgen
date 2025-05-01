from typing import Dict, Any
import json
from ..utils.logger import logger
import traceback

def format_test_result(result: Dict[str, Any]) -> str:
    """Format test result for display."""
    try:
        if result["status"] == "success":
            tool_call = result["tool_call"]
            formatted_parts = [
                "✅ SUCCESS: OpenAI Tool Call Verification",
                "\nOpenAI successfully created a tool call using your schema.",
                "This means it can correctly use your function in conversations.",
                "\nTool Call Details:",
                f"Type: {tool_call['type']}",
                f"Function: {tool_call['function']['name']}",
                "\nArguments OpenAI would pass to your function:",
                json.dumps(json.loads(tool_call['function']['arguments']), indent=2),
                "\nThis shows that OpenAI:",
                "- Understood your function's purpose",
                "- Knew how to call it with proper arguments",
                "- Generated valid JSON matching your schema",
                f"\nTimestamp: {result['timestamp']}"
            ]
            return "\n".join(formatted_parts)
        else:
            return (
                f"❌ Error: {result.get('error', 'Unknown error')}\n"
                "OpenAI was unable to create a valid tool call using your schema.\n"
                "Consider simplifying your schema or making it more clear.\n"
                f"\nTimestamp: {result['timestamp']}"
            )
    except Exception as e:
        logger.error(f"Error formatting test result: {str(e)}")
        logger.debug(f"Format error details: {traceback.format_exc()}")
        return f"Error formatting result: {str(e)}"
