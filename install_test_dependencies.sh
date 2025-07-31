#!/bin/bash

echo "Installing MEGA Test System Dependencies..."
echo "=========================================="

echo ""
echo "Updating pip..."
python3 -m pip install --upgrade pip

echo ""
echo "Installing requirements..."
python3 -m pip install -r thesis_tests/requirements_tests.txt

echo ""
echo "Installing spaCy language model..."
python3 -m spacy download en_core_web_sm

echo ""
echo "Creating directories..."
mkdir -p thesis_tests/test_data
mkdir -p thesis_tests/linkography_data
mkdir -p thesis_tests/uploads
mkdir -p benchmarking/data/sessions

echo ""
echo "=========================================="
echo "Installation complete!"
echo ""
echo "To run the test dashboard:"
echo "  python3 launch_test_dashboard.py"
echo ""
echo "Note: Make sure you have a .env file with:"
echo "  OPENAI_API_KEY=your-api-key-here"
echo ""