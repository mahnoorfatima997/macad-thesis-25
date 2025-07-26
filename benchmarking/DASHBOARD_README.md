# 🧠 Cognitive Benchmarking Dashboard

## Overview

The Cognitive Benchmarking Dashboard provides an interactive visualization interface for exploring the results of the MEGA Architectural Mentor's Graph ML-based cognitive benchmarking system.

## Features

### 📊 Key Metrics Overview
- Total sessions analyzed
- Cognitive offloading prevention rate
- Deep thinking engagement rate
- Improvement vs traditional baseline

### 🎯 Proficiency Analysis
- User proficiency distribution (Beginner, Intermediate, Advanced, Expert)
- Detailed characteristics for each proficiency level
- Interactive pie charts and expandable details

### 🧩 Cognitive Pattern Analysis
- Radar charts comparing system performance vs baseline
- Session-by-session performance heatmaps
- Multi-dimensional cognitive metric visualization

### 📈 Learning Progression
- Temporal analysis of improvement over time
- Skill level progression tracking
- Trend analysis with interactive charts

### 🤖 Agent Effectiveness
- Multi-agent coordination scores
- Agent response distribution
- System effectiveness gauges

### ⚖️ Comparative Analysis
- Bar charts showing improvement percentages
- Dimension-by-dimension comparison with baseline
- Performance highlights and insights

### 💡 Recommendations
- System strengths identification
- Areas for improvement
- Actionable recommendations

## Usage

### Running the Dashboard

1. **After Benchmarking** (Automatic):
   ```bash
   python benchmarking/run_benchmarking.py
   # Dashboard launches automatically after completion
   ```

2. **Standalone Launch**:
   ```bash
   python benchmarking/launch_dashboard.py
   ```

3. **Direct Streamlit Command**:
   ```bash
   streamlit run benchmarking/benchmark_dashboard.py
   ```

### Navigation

- Use the **sidebar** to navigate between different sections
- Each section includes:
  - **Visualizations**: Interactive charts and graphs
  - **Explanations**: Blue boxes explaining what metrics mean
  - **Key Insights**: Yellow boxes highlighting important findings

### Understanding the Visualizations

#### Radar Charts
- Shows performance across multiple cognitive dimensions
- Blue line = MEGA system performance
- Orange line = Traditional baseline
- Further from center = Better performance

#### Heatmaps
- Darker green = Better performance
- Darker red = Needs improvement
- Numbers show exact scores (0-1 scale)

#### Gauge Charts
- Green zone (0.75-1.0) = Excellent
- Blue zone (0.5-0.75) = Good
- Yellow zone (0.25-0.5) = Fair
- Red zone (0-0.25) = Needs improvement

## Data Sources

The dashboard reads from:
- `benchmarking/results/benchmark_report.json` - Main benchmark results
- `benchmarking/results/evaluation_reports/*.json` - Individual session evaluations
- `benchmarking/results/benchmark_summary.md` - Summary text

## Export Options

The dashboard provides options to export:
- **JSON Report**: Complete benchmark data in JSON format
- **PDF Summary**: (Future feature) Formatted PDF report
- **Visualizations**: (Future feature) High-resolution chart exports

## Technical Requirements

- Python 3.8+
- Streamlit
- Plotly
- Pandas
- NumPy

## Troubleshooting

### Dashboard won't launch
- Ensure Streamlit is installed: `pip install streamlit`
- Check that benchmark results exist in `benchmarking/results/`

### Missing visualizations
- Run the full benchmarking pipeline first
- Ensure all result files are generated

### Performance issues
- Close other Streamlit instances
- Clear browser cache
- Use Chrome or Firefox for best performance