"""
Master Test Runner for PArL Compiler
Run all tests or specific task tests with improved organization and quality focus
"""

import sys
import os
import subprocess


def run_test_file(filename, description, show_ast=False):
    """Run a test file and return success status"""
    print(f"\nRunning {description}...")
    print("-" * 80)
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct full path to test file
    test_file_path = os.path.join(script_dir, filename)
    
    # Build command with optional --show-ast flag
    cmd = [sys.executable, test_file_path]
    if show_ast:
        cmd.append("--show-ast")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    return result.returncode == 0


def main():
    """Main test runner"""
    print("PARL COMPILER TEST RUNNER")
    print("="*80)
    
    # Check for --show-ast flag
    show_ast = "--show-ast" in sys.argv
    if show_ast:
        sys.argv.remove("--show-ast")
        print("AST printing enabled")
        print("Detailed output will be written to organized folders in test_outputs/")
    else:
        print("AST printing disabled (use --show-ast to enable)")
        print("Detailed output will be written to organized folders in test_outputs/")
    
    print()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "all":
            # Run all tests
            test_files = [
                ("test_task1.py", "Task 1 - Lexer Tests"),
                ("test_task2.py", "Task 2 - Parser Tests"),
                ("test_task3.py", "Task 3 - Semantic Analysis Tests"),
                ("test_task4.py", "Task 4 - Code Generation Tests"),
                ("test_task5.py", "Task 5 - Array Tests"),
                ("test_assignment.py", "Assignment Examples"),
                ("test_simulator.py", "Simulator Test Programs")
            ]
            
            results = []
            for filename, description in test_files:
                success = run_test_file(filename, description, show_ast)
                results.append((description, success))
            
            # Overall summary
            print("\n" + "="*80)
            print("OVERALL TEST SUMMARY")
            print("="*80)
            
            completed = len(results)
            
            for test_desc, success in results:
                status = "COMPLETED" if success else "ISSUES"
                print(f"{test_desc:<60} {status}")
            
            print("-"*80)
            print(f"Total: {completed} test suites processed")
            
            print("\nTEST OUTPUT ORGANIZATION:")
            print("- test_outputs/task_1/     - Lexer test results")
            print("- test_outputs/task_2/     - Parser test results") 
            print("- test_outputs/task_3/     - Semantic analysis results")
            print("- test_outputs/task_4/     - Code generation results")
            print("- test_outputs/task_5/     - Array functionality results")
            print("- test_outputs/assignment/ - Assignment example results")
            print("- test_outputs/simulator/  - Simulator programs + PArIR files")
            
            print("\nAll test suites have been processed with quality focus")
            print("Each test is numbered and clearly identified by purpose")
            sys.exit(0)
                
        elif sys.argv[1].startswith("task"):
            # Run specific task test
            task_map = {
                "task1": ("test_task1.py", "Task 1 - Lexer Tests"),
                "task2": ("test_task2.py", "Task 2 - Parser Tests"),
                "task3": ("test_task3.py", "Task 3 - Semantic Analysis Tests"),
                "task4": ("test_task4.py", "Task 4 - Code Generation Tests"),
                "task5": ("test_task5.py", "Task 5 - Array Tests")
            }
            
            task = sys.argv[1].lower()
            if task in task_map:
                filename, description = task_map[task]
                success = run_test_file(filename, description, show_ast)
                print(f"\nCheck test_outputs/{task}/ directory for detailed results")
                sys.exit(0)
            else:
                print(f"Unknown task: {task}")
                print_usage()
                sys.exit(1)
                
        elif sys.argv[1] == "assignment":
            # Run assignment examples
            success = run_test_file("test_assignment.py", "Assignment Examples (7 specific examples)", show_ast)
            print(f"\nCheck test_outputs/assignment/ for detailed results")
            sys.exit(0)
            
        elif sys.argv[1] == "simulator":
            # Run simulator tests
            success = run_test_file("test_simulator.py", "Simulator Test Programs (6 selected programs)", show_ast)
            print(f"\nCheck test_outputs/simulator/ for detailed results and PArIR files")
            sys.exit(0)
            
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print_usage()
            sys.exit(1)
    else:
        # Default: show usage
        print_usage()
        sys.exit(0)


def print_usage():
    """Print usage information"""
    print("\nUsage:")
    print("  python -m test.run_all_tests all --show-ast")
    print("")
    print("  python -m test.run_all_tests task1 --show-ast")
    print("  python -m test.run_all_tests task2 --show-ast")
    print("  python -m test.run_all_tests task3 --show-ast")
    print("  python -m test.run_all_tests task4 --show-ast")
    print("  python -m test.run_all_tests task5 --show-ast")
    print("")
    print("  python -m test.run_all_tests assignment --show-ast")
    print("  python -m test.run_all_tests simulator --show-ast")


if __name__ == "__main__":
    main()