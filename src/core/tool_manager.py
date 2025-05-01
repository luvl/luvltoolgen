from typing import Dict, Any
from pathlib import Path
import json
import traceback
from datetime import datetime

from ..utils.logger import logger

class ToolManager:
    def __init__(self, save_dir: str = "saved_tools"):
        """Initialize tool manager with save directory"""
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Tool manager initialized with save directory: {self.save_dir}")

    def save_tool(self, file_path: str, tool_data: Dict[str, Any]) -> bool:
        """
        Save tool data to a file

        Args:
            file_path: Path to save the tool
            tool_data: Dictionary containing tool data
                {
                    "description": str,
                    "schema": dict,
                    "test_input": dict,
                    "metadata": {
                        "created": str,
                        "modified": str,
                        "version": str
                    }
                }
        """
        try:
            # Add metadata
            tool_data["metadata"] = {
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "version": "1.0.0"
            }

            # Validate tool data
            self._validate_tool_data(tool_data)

            # Save to file
            save_path = Path(file_path)
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(tool_data, f, indent=2)

            logger.info(f"Tool saved successfully to {save_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save tool: {str(e)}")
            logger.debug(f"Save error details: {traceback.format_exc()}")
            raise

    def load_tool(self, file_path: str) -> Dict[str, Any]:
        """
        Load tool data from a file

        Args:
            file_path: Path to the tool file

        Returns:
            Dictionary containing tool data
        """
        try:
            # Load from file
            load_path = Path(file_path)
            with open(load_path, 'r', encoding='utf-8') as f:
                tool_data = json.load(f)

            # Validate tool data
            self._validate_tool_data(tool_data)

            logger.info(f"Tool loaded successfully from {load_path}")
            return tool_data

        except Exception as e:
            logger.error(f"Failed to load tool: {str(e)}")
            logger.debug(f"Load error details: {traceback.format_exc()}")
            raise

    def create_new_tool(self) -> Dict[str, Any]:
        """
        Create a new empty tool template

        Returns:
            Dictionary containing empty tool template
        """
        return {
            "description": "",
            "schema": None,
            "test_input": None,
            "metadata": {
                "created": datetime.now().isoformat(),
                "modified": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }

    def _validate_tool_data(self, tool_data: Dict[str, Any]) -> None:
        """
        Validate tool data structure

        Args:
            tool_data: Dictionary containing tool data

        Raises:
            ValueError: If tool data is invalid
        """
        required_keys = ["description", "schema"]
        if not all(key in tool_data for key in required_keys):
            raise ValueError(
                f"Invalid tool data format. Required keys: {required_keys}"
            )

        # Validate schema structure if present
        if tool_data["schema"] is not None:
            required_schema_keys = ["name", "parameters"]
            if not all(key in tool_data["schema"] for key in required_schema_keys):
                raise ValueError(
                    f"Invalid schema format. Required keys: {required_schema_keys}"
                )
