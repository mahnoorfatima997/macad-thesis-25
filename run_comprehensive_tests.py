"""
Master Test Runner

Runs all comprehensive tests and provides a unified report.
"""

import subprocess
import sys
import time
from datetime import datetime

def run_test(test_file, test_name):
    """Run a single test file and capture results."""
    print(f"\n{'='*80}")
    print(f"🧪 RUNNING: {test_name}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, 
                              text=True, 
                              timeout=300)  # 5 minute timeout
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(result.stdout)
        
        if result.stderr:
            print(f"\n⚠️ STDERR OUTPUT:")
            print(result.stderr)
        
        success = result.returncode == 0
        return {
            'name': test_name,
            'file': test_file,
            'success': success,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        print(f"⏰ TEST TIMEOUT: {test_name} exceeded 5 minutes")
        return {
            'name': test_name,
            'file': test_file,
            'success': False,
            'duration': 300,
            'stdout': '',
            'stderr': 'Test timeout after 5 minutes',
            'return_code': -1
        }
    except Exception as e:
        print(f"💥 TEST ERROR: {e}")
        return {
            'name': test_name,
            'file': test_file,
            'success': False,
            'duration': 0,
            'stdout': '',
            'stderr': str(e),
            'return_code': -2
        }

def extract_test_stats(stdout):
    """Extract test statistics from stdout."""
    stats = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'success_rate': 0.0
    }
    
    lines = stdout.split('\n')
    for line in lines:
        if 'Total tests:' in line or 'Total scenarios:' in line:
            try:
                stats['total'] = int(line.split(':')[1].strip())
            except:
                pass
        elif 'Passed:' in line or 'Successful:' in line:
            try:
                stats['passed'] = int(line.split(':')[1].strip())
            except:
                pass
        elif 'Failed:' in line:
            try:
                stats['failed'] = int(line.split(':')[1].strip())
            except:
                pass
        elif 'Success rate:' in line:
            try:
                rate_str = line.split(':')[1].strip().replace('%', '')
                stats['success_rate'] = float(rate_str)
            except:
                pass
    
    return stats

def main():
    """Run all comprehensive tests."""
    
    print("🚀 COMPREHENSIVE TEST SUITE")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Define all tests
    tests = [
        ('test_comprehensive_database.py', 'Database Search & Knowledge Retrieval'),
        ('test_comprehensive_routing.py', 'Routing & Intent Detection'),
        ('test_comprehensive_gamification.py', 'Gamification UI & Rendering'),
        ('test_comprehensive_integration.py', 'End-to-End Integration')
    ]
    
    results = []
    total_start_time = time.time()
    
    # Run each test
    for test_file, test_name in tests:
        result = run_test(test_file, test_name)
        results.append(result)
    
    total_end_time = time.time()
    total_duration = total_end_time - total_start_time
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("📊 COMPREHENSIVE TEST REPORT")
    print(f"{'='*80}")
    
    successful_tests = sum(1 for r in results if r['success'])
    total_tests = len(results)
    
    print(f"🕐 Total Duration: {total_duration:.1f} seconds")
    print(f"📈 Overall Success: {successful_tests}/{total_tests} tests passed")
    print(f"🎯 Overall Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    print(f"\n📋 INDIVIDUAL TEST RESULTS:")
    print("-" * 80)
    
    all_stats = {
        'total_tests': 0,
        'total_passed': 0,
        'total_failed': 0
    }
    
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        duration = f"{result['duration']:.1f}s"
        
        print(f"{status} | {result['name']:<40} | {duration:>8}")
        
        # Extract detailed stats
        stats = extract_test_stats(result['stdout'])
        if stats['total'] > 0:
            print(f"     └─ {stats['total']} tests, {stats['passed']} passed, {stats['failed']} failed ({stats['success_rate']:.1f}%)")
            all_stats['total_tests'] += stats['total']
            all_stats['total_passed'] += stats['passed']
            all_stats['total_failed'] += stats['failed']
        
        if not result['success'] and result['stderr']:
            print(f"     └─ Error: {result['stderr'][:100]}...")
    
    # Aggregate statistics
    if all_stats['total_tests'] > 0:
        print(f"\n📊 AGGREGATE TEST STATISTICS:")
        print("-" * 80)
        print(f"Total Individual Tests: {all_stats['total_tests']}")
        print(f"Total Passed: {all_stats['total_passed']}")
        print(f"Total Failed: {all_stats['total_failed']}")
        print(f"Aggregate Success Rate: {(all_stats['total_passed']/all_stats['total_tests'])*100:.1f}%")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 80)
    
    failed_tests = [r for r in results if not r['success']]
    if not failed_tests:
        print("🎉 All test suites passed! The system is working well.")
    else:
        print("🔧 Issues found in the following areas:")
        for failed_test in failed_tests:
            print(f"   - {failed_test['name']}")
        
        print("\n🛠️ Suggested actions:")
        print("   1. Review failed test outputs above")
        print("   2. Check component initialization and dependencies")
        print("   3. Verify database connectivity and content")
        print("   4. Test individual components in isolation")
    
    # System health summary
    print(f"\n🏥 SYSTEM HEALTH SUMMARY:")
    print("-" * 80)
    
    health_score = (successful_tests / total_tests) * 100
    
    if health_score >= 90:
        print("🟢 EXCELLENT: System is performing very well")
    elif health_score >= 75:
        print("🟡 GOOD: System is mostly functional with minor issues")
    elif health_score >= 50:
        print("🟠 FAIR: System has significant issues that need attention")
    else:
        print("🔴 POOR: System has major issues requiring immediate attention")
    
    print(f"\nOverall Health Score: {health_score:.1f}%")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Return exit code based on results
    return 0 if successful_tests == total_tests else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
