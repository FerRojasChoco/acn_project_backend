from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlmodel import Session, select
from app.core.database import get_session
from app.core.security import get_current_user
from app.core.config import settings
from app.models import Submission, User, SubmissionStatus, Problem
from datetime import datetime
import subprocess
import os
import tempfile
import shutil

router = APIRouter()

# Constants from judge.py
BOX_ID = "0"
MEMORY_LIMIT = "64000"  # 64 MB
TIME_LIMIT = "0.1"  # 0.1s
SANDB0X_PATH = f'/var/local/lib/isolate/{BOX_ID}/box/'

def classify_traceback(path: str):
    """Classifies a Python traceback and sanitizes it"""
    try:
        with open(path, 'r') as f:
            tb = f.read()
    except FileNotFoundError:
        return {"status": "RE", "traceback": "Error file not found"}

    tb_lower = tb.lower()
    
    memory_signatures = [
        "memoryerror",
        "cannot allocate memory",
        "out of memory",
        "oom",
    ]

    # Only consider it MLE if we have explicit memory error keywords
    # Don't rely solely on "killed" as that could be from time limit
    if any(sig in tb_lower for sig in memory_signatures):
        return {"status": "MLE"}

    lines = tb.strip().splitlines()
    filtered = []

    for line in lines:
        if "solution.py" in line:
            filtered.append(line)

    error_line = lines[-1] if lines else ""
    if error_line and error_line not in filtered:
        filtered.append(error_line)

    sanitized = "\n".join(filtered).strip()
    
    return {
        "status": "RE",
        "traceback": sanitized
    }

def run_judge(submission_id: int, problem_path: str, code: str, session: Session):
    """Run the judge on a submission"""
    import logging
    logger = logging.getLogger(__name__)
    
    # Ensure problem_path is absolute
    from pathlib import Path
    problem_path = str(Path(problem_path).resolve())
    
    logger.info(f"Starting judge for submission {submission_id}")
    logger.info(f"Problem path: {problem_path}")
    
    TEST_CASES_PATH = f"{problem_path}/test_cases/"
    OUTPUT_PATH = f"{problem_path}/output/"
    EXPECTED_PATH = f"{problem_path}/expected/"
    ERROR_PATH = f"{problem_path}/error/"
    META_PATH = f"{problem_path}/meta/"
    PROBLEM_FILE = 'run.py'
    
    # Create necessary directories
    os.makedirs(OUTPUT_PATH, exist_ok=True)
    os.makedirs(ERROR_PATH, exist_ok=True)
    os.makedirs(META_PATH, exist_ok=True)
    
    test_cases = []
    all_accepted = True
    
    # Check if isolate is installed
    try:
        isolate_check = subprocess.run(['which', 'isolate'], capture_output=True, text=True)
        if isolate_check.returncode != 0:
            logger.error("isolate command not found!")
            submission = session.get(Submission, submission_id)
            submission.status = SubmissionStatus.INTERNAL_ERR
            submission.result = "Judge system not configured (isolate not installed)"
            session.commit()
            return
        logger.info(f"isolate found at: {isolate_check.stdout.strip()}")
    except Exception as e:
        logger.error(f"Error checking for isolate: {e}")
    
    # Check if test cases directory exists
    if not os.path.exists(TEST_CASES_PATH):
        logger.error(f"Test cases directory not found: {TEST_CASES_PATH}")
        submission = session.get(Submission, submission_id)
        submission.status = SubmissionStatus.INTERNAL_ERR
        submission.result = "Test cases directory not found"
        session.commit()
        return
    
    logger.info(f"Test cases directory found: {TEST_CASES_PATH}")
    
    # Create a temporary solution file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_solution:
        temp_solution.write(code)
        temp_solution_path = temp_solution.name
    
    try:
        for test_file in os.scandir(TEST_CASES_PATH):
            if not test_file.is_file():
                continue
                
            return_dict = {}
            
            # Sandbox cleanup
            subprocess.run(['isolate', '--box-id=0', '--cleanup'], 
                         capture_output=True, check=False)
            
            # Initialize sandbox
            subprocess.run(['isolate', f"--box-id={BOX_ID}", '--init'],
                         capture_output=True, check=False)
            
            # Copy solution file to sandbox
            subprocess.run(['cp', temp_solution_path, f"{SANDB0X_PATH}solution.py"],
                         capture_output=True, check=False)
            
            # Copy problem file to sandbox
            if os.path.exists(f'{problem_path}/{PROBLEM_FILE}'):
                subprocess.run(['cp', f'{problem_path}/{PROBLEM_FILE}', SANDB0X_PATH],
                             capture_output=True, check=False)
            
            # Copy test case input to sandbox
            subprocess.run(['cp', test_file.path, f'{SANDB0X_PATH}stdin.txt'],
                         check=False)
            
            # Create output and error files
            subprocess.run(['touch', f'{SANDB0X_PATH}stdout.txt'], check=False)
            subprocess.run(['touch', f'{SANDB0X_PATH}stderr.txt'], check=False)
            
            # Run python file with constraints
            output = subprocess.run([
                'isolate', 
                f"--box-id={BOX_ID}",
                '--processes=1',
                '--stdin=./stdin.txt',
                '--stdout=./stdout.txt',
                '--stderr=./stderr.txt',
                f'--time={TIME_LIMIT}',
                f'--mem={MEMORY_LIMIT}',
                f'--meta={META_PATH}{test_file.name}',
                '--run',
                '--', 
                '/usr/bin/python3', 
                PROBLEM_FILE
            ], capture_output=True, text=True)
            
            # Parse execution metadata
            meta = {}
            try:
                with open(f"{META_PATH}{test_file.name}", 'r', encoding='utf-8') as meta_file:
                    for line in meta_file.read().split('\n'):
                        if line.strip() and ':' in line:
                            key, value = line.split(':', 1)
                            meta[key] = value
            except FileNotFoundError:
                meta = {'status': 'XX'}
            
            return_dict["mem"] = round(float(meta.get("max-rss", 0))/1000, 2)
            return_dict["time"] = round(float(meta.get("time", 0)), 3)
            
            # Copy output files from sandbox
            subprocess.run(['cp', f'{SANDB0X_PATH}stdout.txt', 
                          f'{OUTPUT_PATH}/{test_file.name}'], check=False)
            subprocess.run(['cp', f'{SANDB0X_PATH}stderr.txt', 
                          f'{ERROR_PATH}/{test_file.name}'], check=False)
            
            # Process execution result
            if output.returncode == 0:
                try:
                    with open(f"{EXPECTED_PATH}{test_file.name}", 'r', 
                            encoding='utf-8') as expected_file:
                        expected_result = expected_file.read()
                    
                    with open(f"{OUTPUT_PATH}{test_file.name}", 'r', 
                            encoding='utf-8') as output_file:
                        output_result = output_file.read()
                    
                    if expected_result.strip() == output_result.strip():
                        return_dict["status"] = "AC"
                    else:
                        return_dict["status"] = "WA"
                        all_accepted = False
                except FileNotFoundError:
                    return_dict["status"] = "XX"
                    all_accepted = False
            else:
                # Non-zero return code - check meta status first
                meta_status = meta.get('status', '')
                
                # Handle time limit exceeded
                if meta_status == "TO":
                    return_dict["status"] = "TO"
                    all_accepted = False
                # Handle internal/sandbox errors
                elif meta_status == "XX":
                    return_dict["status"] = "XX"
                    all_accepted = False
                # Handle runtime errors and memory limit errors
                else:
                    # Check stderr for error details
                    error_result = classify_traceback(f"{ERROR_PATH}{test_file.name}")
                    return_dict.update(error_result)
                    all_accepted = False
            
            test_cases.append(return_dict)
            
            # If any test case fails, we can break early (optional)
            if not all_accepted and return_dict["status"] != "AC":
                break
    
    finally:
        # Cleanup temporary solution file
        if os.path.exists(temp_solution_path):
            os.remove(temp_solution_path)
        
        # Final sandbox cleanup
        subprocess.run(['isolate', '--box-id=0', '--cleanup'], 
                     capture_output=True, check=False)
    
    # Update submission in database
    submission = session.get(Submission, submission_id)
    if submission:
        if all_accepted and test_cases:
            submission.status = SubmissionStatus.ACCEPTED
            submission.result = f"All {len(test_cases)} test cases passed"
        elif test_cases:
            # Set status based on first failure
            first_failure = next((tc for tc in test_cases if tc["status"] != "AC"), None)
            if first_failure:
                status_map = {
                    "WA": SubmissionStatus.WRONG_ANS,
                    "TO": SubmissionStatus.TIME_LIMIT,
                    "MLE": SubmissionStatus.MEM_LIMIT,
                    "RE": SubmissionStatus.RUNTIME_ERR,
                    "XX": SubmissionStatus.INTERNAL_ERR
                }
                submission.status = status_map.get(first_failure["status"], 
                                                   SubmissionStatus.RUNTIME_ERR)
                submission.result = first_failure.get("traceback", 
                                   f"Failed on test case with status {first_failure['status']}")
        else:
            submission.status = SubmissionStatus.INTERNAL_ERR
            submission.result = "No test cases found"
        
        session.commit()
        session.refresh(submission)


@router.post("/{submission_id}/judge")
async def judge_submission(
    submission_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Trigger judging for a submission"""
    
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Check if user owns this submission
    if submission.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to judge this submission")
    
    # Get problem details
    problem = session.get(Problem, submission.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    # Update status to pending
    submission.status = SubmissionStatus.PENDING
    session.commit()
    
    # Get problem path from config
    problem_path = settings.get_problem_path(submission.problem_id)
    
    if not problem_path.exists():
        raise HTTPException(
            status_code=404, 
            detail=f"Problem directory not found: {problem_path}"
        )
    
    # Convert to string for the judge function - THIS WAS THE BUG!
    problem_path_str = str(problem_path)
    
    # Run judge in background - use problem_path_str, not problem_path
    background_tasks.add_task(
        run_judge, 
        submission_id, 
        problem_path_str,  # Fixed: was passing problem_path (Path object)
        submission.code,
        session
    )
    
    return {
        "message": "Submission is being judged",
        "submission_id": submission_id,
        "status": "PENDING"
    }


@router.get("/{submission_id}/status")
def get_submission_status(
    submission_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """Get the status of a submission"""
    
    submission = session.get(Submission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if submission.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return {
        "submission_id": submission.submission_id,
        "status": submission.status,
        "result": submission.result,
        "submitted_at": submission.submitted_at
    }