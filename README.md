# LuvlToolGen ❤️

A delightful tool generator that turns simple schemas into production-ready AI function calling tools with love and care.

## Features

- 🎯 Natural language to JSON schema conversion
- 🛠️ OpenAI tool/function calling format generation
- 🧪 Interactive testing interface
- 💾 Save and load tools
- ❤️ Built with love and care

## Requirements

- Python 3.11+
- PySide6 (Qt6)
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/luvltoolgen.git
cd luvltoolgen
```

2. Create and activate conda environment:
```bash
conda create -n luvltoolgen python=3.11
conda activate luvltoolgen
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

## Project Structure


```
luvltoolgen/
├── src/
│ ├── core/ # Core business logic
│ │ ├── schema_generator.py # OpenAI schema generation
│ │ └── tool_manager.py # Tool saving/loading
│ │
│ ├── ui/ # User interface components
│ │ ├── panels/ # UI Panel Components
│ │ │ ├── description_panel.py # Function Description Panel
│ │ │ ├── schema_panel.py # Schema Display Panel
│ │ │ └── test_panel.py # Testing Panel
│ │ ├── dialogs/ # Dialog windows
│ │ │ └── settings_dialog.py # Settings dialog
│ │ ├── formatters.py # Test result formatting
│ │ └── main_window.py # Main application window
│ │
│ └── utils/ # Utility functions
│ ├── async_utils.py # Async support
│ ├── config.py # Configuration management
│ ├── logger.py # Logging setup
│ └── resources.py # Resource paths
│
├── resources/ # Application resources
│ └── icons/ # UI icons
│ ├── luvltoolgen.svg # App icon
│ ├── new.svg # New tool icon
│ ├── generate.svg # Generate schema icon
│ ├── test.svg # Test function icon
│ └── settings.svg # Settings icon
│
├── logs/ # Application logs
├── saved_tools/ # Saved tool schemas
├── requirements.txt # Python dependencies
└── main.py # Application entry point
```

## Features

### 1. Function Description
- Enter natural language description of your desired function
- Get AI-generated OpenAI-compatible function schema
- Interactive help text guides you through the process

### 2. Schema Generation
- Automatic conversion to OpenAI function calling format
- View and copy generated JSON schema
- Schema validation and formatting

### 3. Testing Interface
- Test your function schema with sample inputs
- Verify OpenAI tool calling compatibility
- Real-time feedback and validation

### 4. Tool Management
- Save tools for later use
- Load and modify existing tools
- Export schemas for other applications

### 5. Settings
- Configure OpenAI API settings
- Toggle dark/light mode
- Show/hide help text
- Customize save locations

## Keyboard Shortcuts

- New Tool: `Ctrl+N`
- Save Tool: `Ctrl+S`
- Load Tool: `Ctrl+O`
- Test Function: `F5`
- Clear All: `Ctrl+L`
- Copy Schema: `Ctrl+C`
- Documentation: `F1`
- Exit: `Ctrl+Q`

## Development

- Built with PySide6 (Qt6) for modern UI
- OpenAI API integration for schema generation
- Async support with qasync
- Python 3.11+ features
- In-memory settings management

## License

MIT License - See LICENSE file for details