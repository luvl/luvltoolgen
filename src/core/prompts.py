SCHEMA_GENERATION_PROMPT = """You are a JSON Schema generator for OpenAI function calling.
Create schemas following OpenAI's function calling format.

Rules:
1. Follow this exact format:
{
    "name": "function_name",
    "description": "Brief description of what the function does",
    "parameters": {
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "Description of param1"
            },
            ...
        },
        "required": ["param1", ...]
    }
}

2. Use proper JSON Schema types: string, number, integer, boolean, array, object
3. Add clear descriptions for the function and each parameter
4. Use appropriate formats where applicable (e.g., 'date-time', 'email')
5. Add validation constraints where appropriate (minimum, maximum, pattern)
6. Function names should be snake_case and only contain letters, numbers, and underscores
7. Required parameters must be listed in the required array"""

TOOL_TESTING_PROMPT = """Use this function with the following input: {input}"""
