"""
Master Test Runner for PArL Compiler
Run all tests or specific task tests
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
    print("PARL COMPILER MASTER TEST RUNNER")
    print("="*80)
    
    # Check for --show-ast flag
    show_ast = "--show-ast" in sys.argv
    if show_ast:
        sys.argv.remove("--show-ast")
        print("AST printing enabled")
        print("Detailed output will be written to files in test_outputs/ directory")
    else:
        print("AST printing disabled (use --show-ast to enable)")
        print("Detailed output will be written to files in test_outputs/ directory")
    
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
            
            passed = sum(1 for _, success in results if success)
            total = len(results)
            
            for test_desc, success in results:
                status = "PASS" if success else "FAIL"
                print(f"{test_desc:<40} {status}")
            
            print("-"*80)
            print(f"Total: {passed}/{total} test suites passed")
            
            if passed == total:
                print("\nALL TESTS PASSED")
                print("Check test_outputs/ directory for detailed results")
                sys.exit(0)
            else:
                print(f"\n{total - passed} TEST SUITE(S) FAILED")
                print("Check test_outputs/ directory for detailed results")
                sys.exit(1)
                
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
                print(f"\nCheck test_outputs/ directory for detailed results")
                sys.exit(0 if success else 1)
            else:
                print(f"Unknown task: {task}")
                print_usage()
                sys.exit(1)
                
        elif sys.argv[1] == "simulator":
            # Run simulator tests
            success = run_test_file("test_simulator.py", "Simulator Test Programs", show_ast)
            print(f"\nCheck test_outputs/ directory for detailed results")
            sys.exit(0 if success else 1)
            
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
    print("  # Run all tests")
    print("  python -m test.run_all_tests all --show-ast")
    print("  # Run specific task tests")
    print("  python -m test.run_all_tests task1 --show-ast      # Lexer tests")
    print("  python -m test.run_all_tests task2 --show-ast      # Parser tests")
    print("  python -m test.run_all_tests task3 --show-ast      # Semantic tests")
    print("  python -m test.run_all_tests task4 --show-ast      # Code generation tests")
    print("  python -m test.run_all_tests task5 --show-ast      # Array tests")
    print("  python -m test.run_all_tests simulator --show-ast  # Simulator tests")
    print("")
    print("  # Run tests without AST output")
    print("  python -m test.run_all_tests task1  ")
    print("  python -m test.run_all_tests task2  ")
    print("  python -m test.run_all_tests task3  ")
    print("  python -m test.run_all_tests task4  ")
    print("  python -m test.run_all_tests task5  ")
    print("")
    print("Note: Detailed output is always written to files in test_outputs/ directory")



if __name__ == "__main__":
    main()