# 🏗️ Mega Architectural Mentor

## Unified AI System: Vision Analysis + Multi-Agent Cognitive Enhancement

A comprehensive AI-powered architectural learning system that combines GPT Vision + SAM analysis with sophisticated multi-agent cognitive enhancement to provide personalized architectural education.

---

## 🚀 Quick Start (Without SAM)

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv mega_env
   mega_env\Scripts\activate  # On Windows
   # or
   source mega_env/bin/activate  # On Mac/Linux
   ```
2. **Install requirements (no SAM):**
   ```bash
   pip install -r requirements_simple.txt
   ```
3. **Set your OpenAI API key:**
   - Create a `.env` file in the project root:
     ```env
     OPENAI_API_KEY=your_openai_api_key_here
     ```
4. **Run the app:**
   ```bash
   streamlit run mega_architectural_mentor.py
   ```

---

## 🚀 Full Setup (With SAM)

1. **Create and activate a virtual environment:**
   ```bash
   python -m venv mega_env
   mega_env\Scripts\activate  # On Windows
   # or
   source mega_env/bin/activate  # On Mac/Linux
   ```
2. **Install all requirements (including SAM):**
   ```bash
   pip install -r requirements_mega.txt
   ```
   - If you encounter errors with `segment-anything` or `groundingdino-py`, make sure PyTorch is installed first:
     ```bash
     pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
     pip install -r requirements_mega.txt
     ```
3. **Set your OpenAI API key:**
   - Create a `.env` file in the project root:
     ```env
     OPENAI_API_KEY=your_openai_api_key_here
     ```
4. **Run the app:**
   ```bash
   streamlit run mega_architectural_mentor.py
   ```

---

## 🧩 How to Use SAM in the App
- The app will automatically use SAM for segmentation if the dependencies are installed.
- If SAM is not installed, the app will still run, but segmentation features will be disabled or limited.
- You can check the sidebar in the app for system status (SAM Ready/Not Ready).

---

## 🛠️ Troubleshooting SAM
- **If you see errors about missing `segment-anything` or `groundingdino-py`:**
  - Make sure you have installed PyTorch first (see above).
  - Try installing SAM dependencies manually:
    ```bash
    pip install git+https://github.com/facebookresearch/segment-anything.git
    pip install git+https://github.com/IDEA-Research/GroundingDINO.git
    ```
- **If you see CUDA or memory errors:**
  - Try running on CPU by setting the device in your `.env`:
    ```env
    SAM_DEVICE=cpu
    ```
- **If you see model loading errors:**
  - Clear your model cache:
    ```bash
    rm -rf ~/.cache/huggingface/
    ```
  - Reinstall SAM dependencies as above.

---

---

**🏗️ Mega Architectural Mentor** - Transforming architectural education through AI-powered cognitive enhancement. 