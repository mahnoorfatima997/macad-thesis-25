# Complete Setup Guide for MEGA Cognitive Benchmarking Test System

This guide provides step-by-step instructions to set up and run the cognitive benchmarking test system that compares three conditions: MENTOR (scaffolding), Generic AI (direct assistance), and Control (no AI).

## Prerequisites

- Python 3.8 or higher
- Windows/Mac/Linux operating system
- OpenAI API key
- ~2GB free disk space for models and dependencies

## Step 1: Clone or Download the Repository

```bash
# If using git
git clone <repository-url>
cd macad-thesis-25

# Or download and extract the ZIP file
```

## Step 2: Create and Activate Virtual Environment

### Windows:
```bash
python -m venv mega_env
mega_env\Scripts\activate
```

### Mac/Linux:
```bash
python -m venv mega_env
source mega_env/bin/activate
```

## Step 3: Install Core Dependencies

```bash
# Install core requirements
pip install -r requirements.txt

# Install MEGA-specific requirements (includes SAM)
pip install -r requirements_mega.txt

# Install benchmarking requirements
pip install -r benchmarking/requirements_benchmarking.txt
```

## Step 4: Install Additional Dependencies for MENTOR

The MENTOR multi-agent system requires additional packages:

```bash
# Install OpenCV for vision components
pip install opencv-python

# Install LangGraph and LangChain
pip install langgraph langchain langchain-openai

# Install ChromaDB for knowledge base
pip install chromadb

# Install other required packages
pip install sentence-transformers numpy pandas matplotlib seaborn
```

## Step 5: Set Up Environment Variables

Create a `.env` file in the root directory:

```bash
# Windows
echo OPENAI_API_KEY=your-api-key-here > .env

# Mac/Linux
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

Replace `your-api-key-here` with your actual OpenAI API key.

## Step 6: Fix ChromaDB Issues (if needed)

If you encounter "collection already exists" errors:

```bash
python fix_chromadb_issue.py
```

## Step 7: Verify MENTOR System

Run the verification script to ensure all components are working:

```bash
python verify_mentor_system.py
```

You should see all checks passing with green checkmarks.

## Step 8: Initialize Knowledge Base (Optional)

If you want to populate the knowledge base for MENTOR:

```bash
cd thesis-agents/knowledge_base
python knowledge_manager.py
cd ../..
```

## Step 9: Launch the Cognitive Benchmarking Test

Start the full test system:

```bash
python launch_full_test.py
```

This will open your default web browser with the test interface.

## Step 10: Running the Test

1. **Registration**: Enter participant ID and select proficiency level
2. **Pre-test**: Complete the 10-minute assessment
3. **Main Test**: Work through three design phases:
   - Ideation (15 min)
   - Visualization (20 min)
   - Materialization (20 min)
4. **Post-test**: Complete final assessment

## Troubleshooting

### Issue: "MENTOR environment unavailable"
**Solution**: Install OpenCV
```bash
pip install opencv-python
```

### Issue: "AttributeError: 'LangGraphOrchestrator' object has no attribute 'process_input'"
**Solution**: This has been fixed. The correct method is `process_student_input`.

### Issue: ChromaDB "collection already exists"
**Solution**: Run the fix script
```bash
python fix_chromadb_issue.py
```

### Issue: ModuleNotFoundError
**Solution**: Ensure all dependencies are installed
```bash
pip install -r requirements.txt
pip install -r requirements_mega.txt
pip install -r benchmarking/requirements_benchmarking.txt
pip install opencv-python langgraph langchain langchain-openai chromadb
```

### Issue: OpenAI API errors
**Solution**: Check your API key in `.env` file
```bash
# Verify .env file exists and contains your key
cat .env  # Mac/Linux
type .env  # Windows
```

## Testing Individual Components

### Test MENTOR Orchestrator:
```bash
python test_mentor_orchestrator.py
```

### Test Knowledge Base:
```bash
cd thesis-agents/knowledge_base
python knowledge_manager.py
```

### Test Benchmarking:
```bash
python benchmarking/generate_test_data.py
python benchmarking/run_benchmarking.py
```

## Data Export

After completing tests, export session data:

1. Click "Export Session Data" in the sidebar during testing
2. Or find auto-saved files in `./thesis_data/` directory
3. Run benchmarking analysis:
   ```bash
   python benchmarking/run_benchmarking.py
   ```

## Quick Start Summary

For a minimal quick start after cloning:

```bash
# 1. Create virtual environment
python -m venv mega_env

# 2. Activate it (Windows)
mega_env\Scripts\activate

# 3. Install all dependencies
pip install -r requirements.txt
pip install -r requirements_mega.txt
pip install -r benchmarking/requirements_benchmarking.txt
pip install opencv-python langgraph langchain langchain-openai chromadb

# 4. Set up API key
echo OPENAI_API_KEY=your-key-here > .env

# 5. Fix potential issues
python fix_chromadb_issue.py

# 6. Launch test
python launch_full_test.py
```

## System Architecture Overview

The test system includes three conditions:

1. **MENTOR**: Multi-agent scaffolding system
   - Uses LangGraph orchestration
   - 5 specialized agents (Socratic Tutor, Domain Expert, etc.)
   - Prevents cognitive offloading through Socratic questioning

2. **Generic AI**: Direct ChatGPT-like assistance
   - Provides immediate answers
   - Enables cognitive offloading

3. **Control**: No AI assistance
   - Baseline for comparison

## Support

If you encounter issues not covered here:
1. Check the console/terminal for detailed error messages
2. Ensure all dependencies are installed correctly
3. Verify your OpenAI API key is valid
4. Check that you're in the correct directory when running commands

The system is now ready for cognitive benchmarking experiments!