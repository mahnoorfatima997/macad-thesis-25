Complete Workflow for Testing and Benchmarking

  1. Install Dependencies

  # First, install test dashboard dependencies
  pip install -r thesis_tests/requirements_tests.txt
  python -m spacy download en_core_web_sm

  # Then, install benchmarking dependencies
  pip install -r benchmarking/requirements_benchmarking.txt

  2. Run Test Sessions (Collect Data)

  # Launch the test dashboard to conduct user sessions
  python launch_test_dashboard.py

  # This will:
  # - Launch the interactive test dashboard
  # - Allow you to conduct test sessions with different users
  # - Automatically save interaction data to thesis_data/ folder
  # - Create CSV files with metrics, linkography data, and session logs
  # - Uses REAL cognitive assessment based on response content (not hardcoded values)

  3. Generate Test Data (Optional - for testing without real users)

  # If you want to test the system without real users
  python benchmarking/generate_test_data.py

  # This creates 5 synthetic sessions with varying proficiency levels

  4. Run Benchmarking Analysis

  # After collecting data from test sessions, run the benchmarking analysis
  python benchmarking/run_benchmarking.py

  # This will:
  # - Load all data from thesis_data/ folder
  # - Generate master metrics CSV with all pre-calculated values
  # - Master metrics will use REAL cognitive assessment scores from interactions_*.csv
  # - Prevention rate = mean(prevents_cognitive_offloading column)
  # - Deep thinking rate = mean(encourages_deep_thinking column)
  # - Run comprehensive analysis (linkography, Graph ML, proficiency
  classification)
  # - Generate evaluation reports in benchmarking/results/
  # - Create visualizations and export them
  # - Automatically launch the dashboard when complete

  5. Launch Dashboard Separately (if needed)

  # Option 1: Launch with automatic analysis update (recommended)
  python benchmarking/launch_dashboard.py

  # Option 2: Launch without re-running analysis (faster)
  python benchmarking/launch_dashboard.py --skip-analysis

  # Or directly with Streamlit
  streamlit run benchmarking/benchmark_dashboard.py

  Important Notes:

  Data Flow:

  1. Test Dashboard → Generates data in thesis_data/
  2. Benchmarking Analysis → Reads from thesis_data/ and creates reports in
  benchmarking/results/
  3. Benchmarking Dashboard → Reads from both thesis_data/ (live data) and
  benchmarking/results/ (analysis reports)

  Key Directories:

  - thesis_data/: Raw interaction data from test sessions
    - interactions_*.csv: User interactions (includes real cognitive assessment scores)
    - metrics_*.csv: Cognitive metrics
    - linkography/: Linkography analysis files
    - session_*.json: Session summaries
  - benchmarking/results/: Analysis outputs
    - master_session_metrics.csv: Pre-calculated metrics for all sessions
    - master_aggregate_metrics.csv: Aggregated metrics by proficiency level
    - benchmark_report.json: Main analysis report
    - evaluation_reports/: Per-session evaluations
    - visualizations/: Generated charts
    - benchmark_summary.md: Human-readable summary

  Minimum Data Requirements:

  - Basic analysis: 1+ sessions
  - Clustering: 3+ sessions recommended
  - Proficiency classifier: 5+ sessions required
  - Optimal results: 10+ sessions

  Typical Workflow Example:

  # Day 1: Setup and initial testing
  pip install -r thesis_tests/requirements_tests.txt
  python -m spacy download en_core_web_sm
  python launch_test_dashboard.py
  # Conduct 3-5 test sessions with different users

  # Day 2: More testing
  python launch_test_dashboard.py
  # Conduct more test sessions

  # When ready to analyze (after collecting enough data):
  pip install -r benchmarking/requirements_benchmarking.txt
  python benchmarking/run_benchmarking.py
  # This runs analysis and launches dashboard

  # Later, to view results again:
  python benchmarking/launch_dashboard.py --skip-analysis

Real Cognitive Assessment:

  As of the latest update, the test dashboard now uses REAL cognitive assessment
  instead of hardcoded values:
  
  - MENTOR group: Scores vary based on response content (Socratic = high, direct = low)
  - GENERIC_AI group: Scores reduced by design (30% prevention, 50% deep thinking)
  - CONTROL group: Always 0 (no AI assistance)
  
  This means:
  - No more clustered improvement scores of 209.5%
  - Realistic variance in cognitive metrics
  - Accurate proficiency classification based on actual pedagogical quality
  - Dashboard shows true effectiveness of different approaches