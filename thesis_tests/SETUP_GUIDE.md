# Test Dashboard Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install -r thesis_tests/requirements_tests.txt
python -m spacy download en_core_web_sm
```

### 2. Configure OpenAI API (Optional - for Generic AI Group)
Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your-api-key-here
```

Note: The Generic AI test environment will work without an API key using fallback responses.

### 3. Launch the Test Dashboard

#### Option A: Minimal Version (Recommended)
```bash
python launch_minimal_test.py
```
Supports: Generic AI and Control groups

#### Option B: Full Version (Requires multi-agent dependencies)
```bash
python launch_test_dashboard.py
```
Supports: All three groups (MENTOR, Generic AI, Control)

## Test Groups

### 1. MENTOR Group
- Multi-agent scaffolding system
- Socratic questioning approach
- Prevents cognitive offloading
- **Requires**: LangGraph and multi-agent dependencies

### 2. Generic AI Group
- Direct AI assistance (ChatGPT-like)
- Provides immediate answers
- Works with or without OpenAI API key
- Uses fallback responses if no API key

### 3. Control Group
- No AI assistance
- Baseline for comparison
- Self-directed design work

## Features

- **Real-time Linkography**: Tracks design moves and cognitive patterns
- **Pre/Post Tests**: Assesses learning outcomes
- **Automatic Logging**: All interactions saved to CSV/JSON
- **Export Functions**: Download session data anytime

## Troubleshooting

### "No module named 'langgraph'" Error
Use the minimal version: `python launch_minimal_test.py`

### OpenAI API Key Missing
The system will show a warning but continue with fallback responses.

### Missing Dependencies
```bash
pip install streamlit pandas spacy openai
python -m spacy download en_core_web_sm
```

## Data Output

Session data is saved to:
- `thesis_tests/test_data/` - Session logs
- `thesis_tests/linkography_data/` - Linkography analysis
- `thesis_tests/uploads/` - User uploads

## Current Status

✅ Generic AI Environment - Fully functional
✅ Control Environment - Fully functional
✅ Logging System - Working
✅ Linkography Logger - Simplified version working
⚠️ MENTOR Environment - Requires additional setup