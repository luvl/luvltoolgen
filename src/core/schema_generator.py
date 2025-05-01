from datetime import datetime
from openai import AsyncOpenAI, APIError, APIConnectionError, AuthenticationError
from typing import Dict, Any, Optional
import json
import re
from ..utils.config import config
from ..utils.logger import logger
from .prompts import SCHEMA_GENERATION_PROMPT, TOOL_TESTING_PROMPT
import traceback

class SchemaGenerator:
    def __init__(self):
        logger.info("Initializing SchemaGenerator")
        self.client = None
        try:
            self._initialize_client()
        except ValueError as e:
            logger.warning(f"Initial client initialization skipped: {str(e)}")

    def _initialize_client(self) -> None:
        """Initialize or reinitialize the OpenAI client"""
        if not config.openai_api_key:
            logger.warning("OpenAI API key not found")
            raise ValueError(
                "OpenAI API key not found. Please set it in the settings dialog."
            )
        try:
            self.client = AsyncOpenAI(api_key=config.openai_api_key)
            logger.debug("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

    async def generate_schema(self, description: str) -> Optional[Dict[str, Any]]:
        """Generate OpenAI function calling schema from natural language description."""
        if not self.client:
            raise ValueError(
                "OpenAI client not initialized. Please set your API key in settings."
            )
        try:
            logger.info("Starting schema generation")
            logger.debug(f"Input description: {description}")

            messages = [
                {"role": "system", "content": SCHEMA_GENERATION_PROMPT},
                {"role": "user", "content": f"Create a function schema for this description:\n{description}\n\nRespond with ONLY the JSON schema, no additional text."}
            ]

            logger.debug("Sending request to OpenAI API")

            try:
                response = await self.client.chat.completions.create(
                    model=config.openai_model,
                    messages=messages,
                    temperature=config.openai_temperature,
                    max_tokens=1000,
                    response_format={"type": "json_object"}
                )
            except AuthenticationError as auth_error:
                logger.error(f"Authentication error: {str(auth_error)}")
                raise Exception("Invalid OpenAI API key. Please check your settings.")
            except APIConnectionError as conn_error:
                logger.error(f"Connection error: {str(conn_error)}")
                raise Exception("Failed to connect to OpenAI. Please check your internet connection.")
            except APIError as api_error:
                logger.error(f"API error: {str(api_error)}")
                raise Exception(f"OpenAI API error: {str(api_error)}")

            schema_text = response.choices[0].message.content
            logger.debug(f"Raw response: {schema_text}")

            try:
                schema = json.loads(schema_text)
                schema = self._validate_function_schema(schema)

                # Pretty print for logging
                formatted_schema = json.dumps(schema, indent=2)
                logger.info("Schema generated successfully")
                logger.debug(f"Final schema: {formatted_schema}")

                return schema

            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                raise Exception("Could not parse the generated schema as valid JSON")

        except Exception as e:
            logger.error(f"Schema generation failed: {str(e)}")
            logger.debug(f"Error details: {traceback.format_exc()}")
            raise Exception(f"Failed to generate schema: {str(e)}")

    async def test_function(self, schema: Dict[str, Any], test_input: Dict[str, Any]) -> Dict[str, Any]:
        """Verify the function/tool calling format with OpenAI."""
        if not self.client:
            return {
                "status": "error",
                "error": "OpenAI client not initialized. Please set your API key in settings.",
                "timestamp": datetime.now().isoformat()
            }
        try:
            logger.info("Testing function format")
            logger.debug(f"Schema: {schema}")
            logger.debug(f"Test input: {test_input}")

            messages = [
                {"role": "user", "content": TOOL_TESTING_PROMPT.format(input=json.dumps(test_input))}
            ]

            try:
                # Test the function calling format
                response = await self.client.chat.completions.create(
                    model=config.openai_model,
                    messages=messages,
                    tools=[{
                        "type": "function",
                        "function": schema
                    }],
                    tool_choice={"type": "function", "function": {"name": schema["name"]}},
                    temperature=config.openai_temperature
                )
            except AuthenticationError:
                return {
                    "status": "error",
                    "error": "Invalid OpenAI API key. Please check your settings.",
                    "timestamp": datetime.now().isoformat()
                }
            except APIConnectionError:
                return {
                    "status": "error",
                    "error": "Failed to connect to OpenAI. Please check your internet connection.",
                    "timestamp": datetime.now().isoformat()
                }
            except APIError as api_error:
                return {
                    "status": "error",
                    "error": f"OpenAI API error: {str(api_error)}",
                    "timestamp": datetime.now().isoformat()
                }

            # Get the tool call from the response
            message = response.choices[0].message
            tool_calls = message.tool_calls if hasattr(message, 'tool_calls') else []

            if tool_calls:
                tool_call = tool_calls[0]
                result = {
                    "status": "success",
                    "tool_call": {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    },
                    "timestamp": datetime.now().isoformat()
                }
            else:
                result = {
                    "status": "error",
                    "error": "No tool call generated",
                    "timestamp": datetime.now().isoformat()
                }

            logger.info("Function format test completed")
            logger.debug(f"Test result: {json.dumps(result, indent=2)}")

            return result

        except Exception as e:
            logger.error(f"Function format test failed: {str(e)}")
            logger.debug(f"Error details: {traceback.format_exc()}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _validate_function_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and ensure the schema follows OpenAI's function calling format."""
        required_fields = ['name', 'description', 'parameters']

        # Ensure name is valid (alphanumeric and underscores only)
        if 'name' not in schema:
            schema['name'] = 'generated_function'
        schema['name'] = re.sub(r'[^a-zA-Z0-9_]', '_', schema['name'])

        # Ensure description exists
        if 'description' not in schema:
            schema['description'] = "Generated function schema"

        # Ensure parameters follow JSON Schema format
        if 'parameters' not in schema:
            schema['parameters'] = {
                "type": "object",
                "properties": {},
                "required": []
            }
        else:
            if 'type' not in schema['parameters']:
                schema['parameters']['type'] = 'object'
            if 'properties' not in schema['parameters']:
                schema['parameters']['properties'] = {}
            if 'required' not in schema['parameters']:
                schema['parameters']['required'] = []

        return schema
