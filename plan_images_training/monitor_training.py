#!/usr/bin/env python3
"""
Monitor YOLOv8 Training Progress
Shows real-time training metrics and progress
"""

import time
import os
from pathlib import Path
import matplotlib.pyplot as plt
import json

def monitor_training():
    """Monitor training progress"""
    print("🚀 YOLOv8 ARCHITECTURAL MODEL TRAINING MONITOR")
    print("=" * 50)
    
    # Check for training runs
    runs_dir = Path("runs")
    if not runs_dir.exists():
        print("❌ No training runs found. Training may not have started yet.")
        return
    
    # Find the latest training run
    train_dirs = [d for d in runs_dir.iterdir() if d.is_dir() and d.name.startswith("train")]
    if not train_dirs:
        print("❌ No training directories found.")
        return
    
    latest_run = max(train_dirs, key=lambda x: x.stat().st_mtime)
    print(f"📁 Monitoring: {latest_run.name}")
    
    # Check for results file
    results_file = latest_run / "results.csv"
    if not results_file.exists():
        print("⏳ Training is starting up...")
        print("   Waiting for results.csv to be created...")
        return
    
    # Monitor training progress
    print("📊 Training Progress:")
    print("   Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            # Read current results
            if results_file.exists():
                with open(results_file, 'r') as f:
                    lines = f.readlines()
                
                if len(lines) > 1:  # Has header and at least one epoch
                    latest_line = lines[-1].strip().split(',')
                    if len(latest_line) >= 10:
                        epoch = latest_line[0]
                        train_loss = latest_line[1]
                        val_loss = latest_line[2]
                        mAP50 = latest_line[3]
                        mAP50_95 = latest_line[4]
                        
                        print(f"\r   Epoch: {epoch} | Train Loss: {train_loss} | Val Loss: {val_loss} | mAP50: {mAP50} | mAP50-95: {mAP50_95}", end='', flush=True)
            
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped.")
        print("📈 Training continues in background...")

def show_training_summary():
    """Show training summary when complete"""
    runs_dir = Path("runs")
    if not runs_dir.exists():
        return
    
    train_dirs = [d for d in runs_dir.iterdir() if d.is_dir() and d.name.startswith("train")]
    if not train_dirs:
        return
    
    latest_run = max(train_dirs, key=lambda x: x.stat().st_mtime)
    
    # Check if training is complete
    weights_file = latest_run / "weights" / "best.pt"
    if weights_file.exists():
        print(f"\n🎉 Training Complete!")
        print(f"📁 Model saved to: {weights_file}")
        
        # Show final metrics
        results_file = latest_run / "results.csv"
        if results_file.exists():
            with open(results_file, 'r') as f:
                lines = f.readlines()
            
            if len(lines) > 1:
                final_line = lines[-1].strip().split(',')
                if len(final_line) >= 10:
                    print(f"📊 Final Metrics:")
                    print(f"   Epochs: {final_line[0]}")
                    print(f"   Final mAP50: {final_line[3]}")
                    print(f"   Final mAP50-95: {final_line[4]}")

if __name__ == "__main__":
    monitor_training()
    show_training_summary() 