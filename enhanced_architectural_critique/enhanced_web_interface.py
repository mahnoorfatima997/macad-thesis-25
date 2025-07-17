#!/usr/bin/env python3
"""
Enhanced Web Interface for Architectural Critique System
Provides a modern, interactive interface for comprehensive architectural analysis
"""

from flask import Flask, request, jsonify, render_template_string, send_file, Response
from flask_cors import CORS
import os
import json
import base64
from io import BytesIO
from PIL import Image
import numpy as np
import cv2
from pathlib import Path
import tempfile
import shutil
import time
from datetime import datetime
import threading
import queue

# Import our enhanced application
from enhanced_architectural_critique import EnhancedArchitecturalCritiqueApp, AnalysisMode
from enhanced_config_manager import EnhancedConfigManager, AnalysisMode as ConfigAnalysisMode

app = Flask(__name__)
CORS(app)

# Initialize the enhanced critique app and config manager
config_manager = EnhancedConfigManager()
critique_app = EnhancedArchitecturalCritiqueApp(
    yolo_model_path=config_manager.config.models.yolo_model_path,
    sam_checkpoint=config_manager.config.models.sam_checkpoint
)

# Create directories
UPLOAD_FOLDER = Path('uploads')
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER = Path('outputs')
OUTPUT_FOLDER.mkdir(exist_ok=True)
CACHE_FOLDER = Path('cache')
CACHE_FOLDER.mkdir(exist_ok=True)

# Analysis queue for background processing
analysis_queue = queue.Queue()
analysis_results = {}

# Enhanced HTML template with modern UI and interactive features
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Architectural Critique System</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            overflow-x: hidden;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
            position: relative;
        }
        
        .header h1 {
            font-size: 3em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .header p {
            font-size: 1.3em;
            opacity: 0.9;
            margin-bottom: 20px;
        }
        
        .header .version {
            position: absolute;
            top: 10px;
            right: 20px;
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .upload-section {
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            position: sticky;
            top: 20px;
        }
        
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 50px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            position: relative;
            overflow: hidden;
        }
        
        .upload-area:hover {
            background: linear-gradient(135deg, #f8f9ff 0%, #e3f2fd 100%);
            border-color: #764ba2;
            transform: translateY(-2px);
        }
        
        .upload-area.dragover {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-color: #2196f3;
            transform: scale(1.02);
        }
        
        .upload-icon {
            font-size: 4em;
            color: #667eea;
            margin-bottom: 20px;
            transition: all 0.3s ease;
        }
        
        .upload-area:hover .upload-icon {
            transform: scale(1.1);
            color: #764ba2;
        }
        
        .upload-text {
            font-size: 1.2em;
            color: #666;
            margin-bottom: 20px;
            line-height: 1.6;
        }
        
        .file-input {
            display: none;
        }
        
        .upload-btn {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 30px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
        }
        
        .upload-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        
        .analysis-controls {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 15px;
        }
        
        .control-group {
            margin-bottom: 20px;
        }
        
        .control-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .control-group select,
        .control-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }
        
        .control-group select:focus,
        .control-group input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .analyze-btn {
            background: linear-gradient(45deg, #4caf50, #45a049);
            color: white;
            border: none;
            padding: 18px 40px;
            border-radius: 30px;
            font-size: 1.2em;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
        }
        
        .analyze-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(76, 175, 80, 0.4);
        }
        
        .analyze-btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .results-section {
            background: white;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            display: none;
        }
        
        .loading {
            text-align: center;
            padding: 60px;
            color: #667eea;
        }
        
        .spinner {
            border: 6px solid #f3f3f3;
            border-top: 6px solid #667eea;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin: 0 auto 30px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #f0f0f0;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(45deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s ease;
            border-radius: 4px;
        }
        
        .results-content {
            display: none;
        }
        
        .score-dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .score-card {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }
        
        .score-value {
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        
        .score-label {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .image-comparison {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .image-container {
            position: relative;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }
        
        .image-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .image-label {
            position: absolute;
            top: 15px;
            left: 15px;
            background: rgba(0,0,0,0.7);
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }
        
        .critique-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }
        
        .critique-panel {
            background: #f8f9ff;
            padding: 25px;
            border-radius: 15px;
            border-left: 6px solid #667eea;
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .critique-panel:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        }
        
        .critique-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .critique-title {
            font-size: 1.3em;
            color: #333;
            font-weight: 600;
        }
        
        .severity-badge {
            display: inline-block;
            padding: 6px 15px;
            border-radius: 25px;
            color: white;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .severity-critical { background: linear-gradient(45deg, #f44336, #d32f2f); }
        .severity-high { background: linear-gradient(45deg, #ff9800, #f57c00); }
        .severity-medium { background: linear-gradient(45deg, #2196f3, #1976d2); }
        .severity-low { background: linear-gradient(45deg, #4caf50, #388e3c); }
        
        .critique-description {
            color: #666;
            line-height: 1.6;
            margin-bottom: 15px;
        }
        
        .improvement-suggestion {
            background: #e8f5e8;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #4caf50;
            color: #2e7d32;
            font-style: italic;
        }
        
        .critique-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 15px;
            font-size: 0.9em;
            color: #888;
        }
        
        .impact-score {
            display: flex;
            align-items: center;
            gap: 5px;
        }
        
        .impact-bar {
            width: 60px;
            height: 6px;
            background: #e0e0e0;
            border-radius: 3px;
            overflow: hidden;
        }
        
        .impact-fill {
            height: 100%;
            background: linear-gradient(45deg, #667eea, #764ba2);
            border-radius: 3px;
        }
        
        .download-section {
            text-align: center;
            margin-top: 40px;
            padding: 30px;
            background: #f8f9ff;
            border-radius: 15px;
        }
        
        .download-btn {
            background: linear-gradient(45deg, #764ba2, #667eea);
            color: white;
            border: none;
            padding: 15px 35px;
            border-radius: 30px;
            font-size: 1.1em;
            cursor: pointer;
            transition: all 0.3s ease;
            margin: 0 10px;
            box-shadow: 0 5px 15px rgba(118, 75, 162, 0.3);
        }
        
        .download-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(118, 75, 162, 0.4);
        }
        
        .metrics-panel {
            background: white;
            padding: 25px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
        }
        
        .metric-item {
            text-align: center;
            padding: 15px;
            background: #f8f9ff;
            border-radius: 10px;
        }
        
        .metric-value {
            font-size: 1.8em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #666;
        }
        
        .compliance-summary {
            background: #fff3e0;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            border-left: 6px solid #ff9800;
        }
        
        .compliance-score {
            font-size: 2em;
            font-weight: bold;
            color: #f57c00;
            margin-bottom: 10px;
        }
        
        .compliance-issues {
            list-style: none;
            padding: 0;
        }
        
        .compliance-issues li {
            padding: 8px 0;
            border-bottom: 1px solid #ffe0b2;
        }
        
        .compliance-issues li:last-child {
            border-bottom: none;
        }
        
        @media (max-width: 1200px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .upload-section {
                position: static;
            }
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .critique-grid {
                grid-template-columns: 1fr;
            }
            
            .image-comparison {
                grid-template-columns: 1fr;
            }
            
            .score-dashboard {
                grid-template-columns: repeat(2, 1fr);
            }
        }
        
        .notification {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 25px;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            z-index: 1000;
            transform: translateX(400px);
            transition: transform 0.3s ease;
        }
        
        .notification.show {
            transform: translateX(0);
        }
        
        .notification.success {
            background: linear-gradient(45deg, #4caf50, #45a049);
        }
        
        .notification.error {
            background: linear-gradient(45deg, #f44336, #d32f2f);
        }
        
        .notification.info {
            background: linear-gradient(45deg, #2196f3, #1976d2);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="version">v2.0.0</div>
            <h1><i class="fas fa-building"></i> Enhanced Architectural Critique</h1>
            <p>AI-powered comprehensive design analysis with multimodal feedback</p>
        </div>
        
        <div class="main-content">
            <div class="upload-section">
                <div class="upload-area" id="uploadArea">
                    <div class="upload-icon">
                        <i class="fas fa-cloud-upload-alt"></i>
                    </div>
                    <div class="upload-text">
                        <strong>Drag and drop</strong> your architectural image here,<br>
                        or <strong>click to select</strong> from your files
                    </div>
                    <input type="file" id="fileInput" class="file-input" accept="image/*">
                    <button class="upload-btn" onclick="document.getElementById('fileInput').click()">
                        <i class="fas fa-folder-open"></i> Choose File
                    </button>
                </div>
                
                <div class="analysis-controls">
                    <div class="control-group">
                        <label for="analysisMode">Analysis Mode:</label>
                        <select id="analysisMode">
                            <option value="interior">Interior Analysis</option>
                            <option value="exterior">Exterior Analysis</option>
                            <option value="site_plan">Site Plan Analysis</option>
                            <option value="floor_plan">Floor Plan Analysis</option>
                            <option value="section">Section Analysis</option>
                            <option value="elevation">Elevation Analysis</option>
                        </select>
                    </div>
                    
                    <div class="control-group">
                        <label for="confidenceThreshold">Confidence Threshold:</label>
                        <input type="range" id="confidenceThreshold" min="0.1" max="0.9" step="0.1" value="0.5">
                        <span id="confidenceValue">0.5</span>
                    </div>
                    
                    <div class="control-group">
                        <label for="maxCritiques">Max Critique Points:</label>
                        <input type="number" id="maxCritiques" min="5" max="20" value="12">
                    </div>
                    
                    <button class="analyze-btn" id="analyzeBtn" disabled onclick="analyzeImage()">
                        <i class="fas fa-search"></i> Analyze Design
                    </button>
                </div>
            </div>
            
            <div class="results-section" id="resultsSection">
                <div class="loading" id="loadingIndicator">
                    <div class="spinner"></div>
                    <h3>Analyzing your architectural design...</h3>
                    <p>This may take a few moments depending on image complexity</p>
                    <div class="progress-bar">
                        <div class="progress-fill" id="progressFill"></div>
                    </div>
                    <p id="progressText">Initializing analysis...</p>
                </div>
                
                <div id="resultsContent" class="results-content">
                    <!-- Results will be populated here -->
                </div>
            </div>
        </div>
    </div>

    <div id="notification" class="notification"></div>

    <script>
        let uploadedFile = null;
        let analysisResults = null;
        let analysisId = null;
        
        // DOM elements
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const analyzeBtn = document.getElementById('analyzeBtn');
        const resultsSection = document.getElementById('resultsSection');
        const confidenceSlider = document.getElementById('confidenceThreshold');
        const confidenceValue = document.getElementById('confidenceValue');
        
        // Event listeners
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileUpload(files[0]);
            }
        });
        
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        });
        
        confidenceSlider.addEventListener('input', (e) => {
            confidenceValue.textContent = e.target.value;
        });
        
        function handleFileUpload(file) {
            if (!file.type.startsWith('image/')) {
                showNotification('Please select an image file', 'error');
                return;
            }
            
            uploadedFile = file;
            analyzeBtn.disabled = false;
            showNotification('Image uploaded successfully', 'success');
        }
        
        async function analyzeImage() {
            if (!uploadedFile) return;
            
            // Generate analysis ID
            analysisId = 'analysis_' + Date.now();
            
            // Show results section
            resultsSection.style.display = 'block';
            document.getElementById('loadingIndicator').style.display = 'block';
            document.getElementById('resultsContent').style.display = 'none';
            
            // Prepare form data
            const formData = new FormData();
            formData.append('image', uploadedFile);
            formData.append('analysis_mode', document.getElementById('analysisMode').value);
            formData.append('confidence_threshold', confidenceSlider.value);
            formData.append('max_critiques', document.getElementById('maxCritiques').value);
            
            try {
                // Start analysis
                const response = await fetch('/analyze', {
                    method: 'POST',
                    body: formData
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const results = await response.json();
                
                if (results.error) {
                    throw new Error(results.error);
                }
                
                analysisResults = results;
                displayResults(results);
                showNotification('Analysis completed successfully!', 'success');
                
            } catch (error) {
                showNotification('Error analyzing image: ' + error.message, 'error');
            } finally {
                document.getElementById('loadingIndicator').style.display = 'none';
                document.getElementById('resultsContent').style.display = 'block';
            }
        }
        
        function displayResults(results) {
            const resultsContent = document.getElementById('resultsContent');
            
            resultsContent.innerHTML = `
                <div class="score-dashboard">
                    <div class="score-card">
                        <div class="score-value">${results.overall_score.toFixed(1)}</div>
                        <div class="score-label">Overall Score</div>
                    </div>
                    <div class="score-card">
                        <div class="score-value">${results.detected_objects.length}</div>
                        <div class="score-label">Objects Detected</div>
                    </div>
                    <div class="score-card">
                        <div class="score-value">${results.critique_points.length}</div>
                        <div class="score-label">Issues Found</div>
                    </div>
                    <div class="score-card">
                        <div class="score-value">${(results.compliance_summary.overall_compliance_score * 100).toFixed(0)}%</div>
                        <div class="score-label">Compliance</div>
                    </div>
                </div>
                
                <div class="image-comparison">
                    <div class="image-container">
                        <img src="/uploads/${results.original_image}" alt="Original Image">
                        <div class="image-label">Original</div>
                    </div>
                    <div class="image-container">
                        <img src="${results.annotated_image_url}" alt="Annotated Analysis">
                        <div class="image-label">Analysis</div>
                    </div>
                </div>
                
                <div class="metrics-panel">
                    <h3><i class="fas fa-chart-line"></i> Design Metrics</h3>
                    <div class="metrics-grid">
                        ${Object.entries(results.design_metrics).map(([key, value]) => `
                            <div class="metric-item">
                                <div class="metric-value">${(value * 10).toFixed(1)}</div>
                                <div class="metric-label">${key.replace(/_/g, ' ').toUpperCase()}</div>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                ${results.compliance_summary.compliance_issues.length > 0 ? `
                    <div class="compliance-summary">
                        <div class="compliance-score">
                            ${(results.compliance_summary.overall_compliance_score * 100).toFixed(0)}% Compliance
                        </div>
                        <h4>Compliance Issues:</h4>
                        <ul class="compliance-issues">
                            ${results.compliance_summary.compliance_issues.map(issue => `
                                <li>${issue.issue}</li>
                            `).join('')}
                        </ul>
                    </div>
                ` : ''}
                
                <div class="critique-grid">
                    ${results.critique_points.map(critique => createCritiquePanel(critique)).join('')}
                </div>
                
                <div class="download-section">
                    <button class="download-btn" onclick="downloadReport()">
                        <i class="fas fa-file-pdf"></i> Download Report
                    </button>
                    <button class="download-btn" onclick="downloadAnnotatedImage()">
                        <i class="fas fa-image"></i> Download Analysis
                    </button>
                    <button class="download-btn" onclick="downloadJSON()">
                        <i class="fas fa-code"></i> Download JSON
                    </button>
                </div>
            `;
        }
        
        function createCritiquePanel(critique) {
            const severityClass = getSeverityClass(critique.severity);
            const severityText = getSeverityText(critique.severity);
            
            return `
                <div class="critique-panel" onclick="showCritiqueDetails(${JSON.stringify(critique).replace(/"/g, '&quot;')})">
                    <div class="critique-header">
                        <div class="critique-title">${critique.title}</div>
                        <span class="severity-badge ${severityClass}">${severityText}</span>
                    </div>
                    <div class="critique-description">${critique.description}</div>
                    <div class="improvement-suggestion">
                        <strong><i class="fas fa-lightbulb"></i> Suggestion:</strong> ${critique.improvement_suggestion}
                    </div>
                    <div class="critique-meta">
                        <div class="impact-score">
                            Impact: 
                            <div class="impact-bar">
                                <div class="impact-fill" style="width: ${critique.impact_score * 100}%"></div>
                            </div>
                            ${critique.impact_score.toFixed(1)}
                        </div>
                        <div>Priority: ${critique.priority}</div>
                    </div>
                </div>
            `;
        }
        
        function getSeverityClass(severity) {
            if (severity >= 4) return 'severity-critical';
            if (severity >= 3) return 'severity-high';
            if (severity >= 2) return 'severity-medium';
            return 'severity-low';
        }
        
        function getSeverityText(severity) {
            if (severity >= 4) return 'Critical';
            if (severity >= 3) return 'High';
            if (severity >= 2) return 'Medium';
            return 'Low';
        }
        
        function showCritiqueDetails(critique) {
            const details = `
                <strong>Category:</strong> ${critique.category}<br>
                <strong>Severity:</strong> ${critique.severity}/4<br>
                <strong>Impact Score:</strong> ${critique.impact_score.toFixed(2)}<br>
                <strong>Affected Objects:</strong> ${critique.affected_objects.length}<br>
                ${critique.standards_reference ? `<strong>Standards Reference:</strong> ${critique.standards_reference}<br>` : ''}
                <strong>Evidence:</strong><br>
                ${critique.evidence.map(e => `• ${e}`).join('<br>')}
            `;
            
            showNotification(details, 'info');
        }
        
        async function downloadReport() {
            if (!analysisResults) return;
            
            try {
                const response = await fetch('/download-report', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(analysisResults)
                });
                
                const blob = await response.blob();
                downloadBlob(blob, 'architectural_critique_report.pdf');
                
            } catch (error) {
                showNotification('Error downloading report: ' + error.message, 'error');
            }
        }
        
        async function downloadAnnotatedImage() {
            if (!analysisResults || !analysisResults.annotated_image_url) return;
            
            try {
                const response = await fetch(analysisResults.annotated_image_url);
                const blob = await response.blob();
                downloadBlob(blob, 'annotated_analysis.jpg');
                
            } catch (error) {
                showNotification('Error downloading image: ' + error.message, 'error');
            }
        }
        
        async function downloadJSON() {
            if (!analysisResults) return;
            
            const jsonString = JSON.stringify(analysisResults, null, 2);
            const blob = new Blob([jsonString], { type: 'application/json' });
            downloadBlob(blob, 'analysis_results.json');
        }
        
        function downloadBlob(blob, filename) {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);
        }
        
        function showNotification(message, type = 'info') {
            const notification = document.getElementById('notification');
            notification.textContent = message;
            notification.className = `notification ${type}`;
            notification.classList.add('show');
            
            setTimeout(() => {
                notification.classList.remove('show');
            }, 5000);
        }
        
        // Simulate progress updates
        function updateProgress(progress, text) {
            const progressFill = document.getElementById('progressFill');
            const progressText = document.getElementById('progressText');
            
            if (progressFill) progressFill.style.width = progress + '%';
            if (progressText) progressText.textContent = text;
        }
        
        // Initialize progress simulation
        let progressInterval;
        function startProgressSimulation() {
            let progress = 0;
            const steps = [
                { progress: 10, text: 'Loading models...' },
                { progress: 25, text: 'Detecting objects...' },
                { progress: 45, text: 'Analyzing spatial relationships...' },
                { progress: 65, text: 'Generating critique points...' },
                { progress: 85, text: 'Creating visual feedback...' },
                { progress: 95, text: 'Finalizing report...' }
            ];
            
            let stepIndex = 0;
            progressInterval = setInterval(() => {
                if (stepIndex < steps.length) {
                    const step = steps[stepIndex];
                    updateProgress(step.progress, step.text);
                    stepIndex++;
                } else {
                    updateProgress(100, 'Analysis complete!');
                    clearInterval(progressInterval);
                }
            }, 1000);
        }
        
        // Start progress when analysis begins
        document.addEventListener('DOMContentLoaded', () => {
            // Initialize any additional features
            console.log('Enhanced Architectural Critique System v2.0.0 loaded');
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Main page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/analyze', methods=['POST'])
def analyze_image():
    """Enhanced image analysis endpoint"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image file selected'}), 400
        
        # Get analysis parameters
        analysis_mode = request.form.get('analysis_mode', 'interior')
        confidence_threshold = float(request.form.get('confidence_threshold', 0.5))
        max_critiques = int(request.form.get('max_critiques', 12))
        
        # Update configuration based on analysis mode
        config_manager.apply_analysis_mode(ConfigAnalysisMode(analysis_mode))
        config_manager.update_model_config(confidence_threshold=confidence_threshold)
        config_manager.update_critique_config(max_critique_points=max_critiques)
        
        # Save uploaded file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"upload_{timestamp}.jpg"
        filepath = UPLOAD_FOLDER / filename
        file.save(filepath)
        
        # Load image into critique app
        critique_app.load_image(str(filepath))
        
        # Run enhanced analysis pipeline
        objects = critique_app.detect_objects(
            confidence_threshold=config_manager.config.models.confidence_threshold
        )
        
        # Segment objects if SAM is available
        critique_app.segment_objects()
        
        # Analyze spatial relationships
        analysis = critique_app.analyze_spatial_relationships()
        
        # Generate critique points
        critiques = critique_app.generate_critique_points(analysis)
        
        # Create visual feedback
        output_filename = f"annotated_{filename}"
        output_path = OUTPUT_FOLDER / output_filename
        critique_app.create_visual_feedback(str(output_path))
        
        # Generate comprehensive report
        report = critique_app.generate_report(str(OUTPUT_FOLDER / f"report_{filename}.json"))
        
        # Prepare enhanced response
        response = {
            'analysis_id': f"analysis_{timestamp}",
            'timestamp': timestamp,
            'original_image': filename,
            'overall_score': report['overall_score'],
            'critique_points': report['critique_points'],
            'detected_objects': report['detected_objects'],
            'spatial_relationships': report['spatial_relationships'],
            'design_metrics': report['design_metrics'],
            'compliance_summary': report['compliance_summary'],
            'improvement_priorities': report['improvement_priorities'],
            'annotated_image_url': f'/outputs/{output_filename}',
            'recommendations': report['recommendations'],
            'analysis_mode': analysis_mode,
            'configuration_used': config_manager.get_config_summary()
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/uploads/<filename>')
def serve_upload(filename):
    """Serve uploaded files"""
    return send_file(UPLOAD_FOLDER / filename)

@app.route('/outputs/<filename>')
def serve_output(filename):
    """Serve output files"""
    return send_file(OUTPUT_FOLDER / filename)

@app.route('/download-report', methods=['POST'])
def download_report():
    """Download analysis report"""
    try:
        report_data = request.json
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(report_data, f, indent=2)
            temp_path = f.name
        
        return send_file(temp_path, as_attachment=True, download_name='critique_report.json')
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    """Manage application configuration"""
    if request.method == 'GET':
        return jsonify(config_manager.get_config_summary())
    
    elif request.method == 'POST':
        try:
            config_updates = request.json
            
            # Update configuration
            if 'models' in config_updates:
                config_manager.update_model_config(**config_updates['models'])
            
            if 'analysis' in config_updates:
                config_manager.update_analysis_config(**config_updates['analysis'])
            
            if 'critique' in config_updates:
                config_manager.update_critique_config(**config_updates['critique'])
            
            if 'visualization' in config_updates:
                config_manager.update_visualization_config(**config_updates['visualization'])
            
            return jsonify({'success': True, 'message': 'Configuration updated'})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'version': '2.0.0',
        'models_loaded': {
            'yolo': critique_app.yolo_model is not None,
            'sam': critique_app.sam_predictor is not None
        },
        'config_valid': len(config_manager.validate_config()) == 0,
        'analysis_modes': [mode.value for mode in AnalysisMode],
        'features': [
            'Enhanced Object Detection',
            'SAM Segmentation',
            'Spatial Relationship Analysis',
            'Comprehensive Critique Generation',
            'Visual Feedback System',
            'Compliance Checking',
            'Cost Estimation',
            'Multi-modal Analysis'
        ]
    })

if __name__ == '__main__':
    print("Starting Enhanced Architectural Critique System v2.0.0...")
    print("Access the web interface at: http://localhost:5000")
    
    # Validate configuration
    issues = config_manager.validate_config()
    if issues:
        print("Configuration issues found:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("Configuration is valid")
    
    # Print system information
    print(f"Analysis modes available: {[mode.value for mode in AnalysisMode]}")
    print(f"YOLO model: {config_manager.config.models.yolo_model_path}")
    print(f"SAM model: {config_manager.config.models.sam_checkpoint}")
    print(f"Device: {config_manager.config.models.device}")
    
    app.run(debug=True, host='0.0.0.0', port=5000) 