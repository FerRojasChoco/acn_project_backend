#!/usr/bin/env python3
"""
Verify that problem directories are structured correctly
"""
import os
from pathlib import Path

def verify_problem_structure(problem_num: int):
    """Verify a single problem's structure"""
    
    # Get the path to the problem directory
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    problems_dir = project_root / "problems"
    problem_path = problems_dir / f"problem{problem_num}"
    
    print(f"\n{'='*60}")
    print(f"Verifying Problem {problem_num}")
    print(f"{'='*60}")
    print(f"Path: {problem_path}")
    
    if not problem_path.exists():
        print(f"❌ Problem directory does not exist!")
        return False
    
    print(f"✅ Problem directory exists")
    
    # Check required subdirectories
    required_dirs = ['test_cases', 'expected', 'output', 'error', 'meta']
    all_dirs_exist = True
    
    for dir_name in required_dirs:
        dir_path = problem_path / dir_name
        if dir_path.exists():
            # Count files in directory
            file_count = len(list(dir_path.glob('*.txt')))
            print(f"✅ {dir_name:15} exists ({file_count} files)")
        else:
            print(f"❌ {dir_name:15} missing!")
            all_dirs_exist = False
    
    # Check run.py
    run_py = problem_path / "run.py"
    if run_py.exists():
        print(f"✅ run.py exists")
        
        # Show first few lines
        with open(run_py, 'r') as f:
            lines = f.readlines()[:5]
        print(f"\n   First lines of run.py:")
        for line in lines:
            print(f"   {line.rstrip()}")
    else:
        print(f"❌ run.py missing!")
        all_dirs_exist = False
    
    # Check test case matching
    test_cases_dir = problem_path / "test_cases"
    expected_dir = problem_path / "expected"
    
    if test_cases_dir.exists() and expected_dir.exists():
        test_files = set(f.name for f in test_cases_dir.glob('*.txt'))
        expected_files = set(f.name for f in expected_dir.glob('*.txt'))
        
        if test_files == expected_files:
            print(f"✅ Test cases match expected outputs ({len(test_files)} pairs)")
            print(f"   Files: {', '.join(sorted(test_files))}")
        else:
            print(f"⚠️  Test case/expected mismatch!")
            missing_expected = test_files - expected_files
            missing_tests = expected_files - test_files
            if missing_expected:
                print(f"   Missing expected outputs: {missing_expected}")
            if missing_tests:
                print(f"   Missing test cases: {missing_tests}")
    
    # Show sample test case
    if test_cases_dir.exists():
        test_files = list(test_cases_dir.glob('*.txt'))
        if test_files:
            sample_test = test_files[0]
            print(f"\n   Sample test case ({sample_test.name}):")
            with open(sample_test, 'r') as f:
                content = f.read().strip()
            print(f"   Input: {content[:50]}{'...' if len(content) > 50 else ''}")
            
            # Show corresponding expected output
            expected_file = expected_dir / sample_test.name
            if expected_file.exists():
                with open(expected_file, 'r') as f:
                    content = f.read().strip()
                print(f"   Expected: {content[:50]}{'...' if len(content) > 50 else ''}")
    
    return all_dirs_exist

def main():
    """Verify all problems"""
    print("\n" + "="*60)
    print("Problem Structure Verification")
    print("="*60)
    
    # Check for problem1 and problem2
    problems_verified = []
    for i in [1, 2]:
        result = verify_problem_structure(i)
        problems_verified.append(result)
    
    print(f"\n{'='*60}")
    print("Summary")
    print(f"{'='*60}")
    
    for i, verified in enumerate(problems_verified, 1):
        status = "✅ READY" if verified else "❌ NEEDS ATTENTION"
        print(f"Problem {i}: {status}")
    
    print()

if __name__ == "__main__":
    main()