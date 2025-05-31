"""
Shared Test Utilities
Common functions used across all test modules
"""

import os
import sys
from datetime import datetime

# Global flag to control AST printing
PRINT_AST_ENABLED = True
# Global file handle for test output
current_test_file = None

def set_ast_printing(enabled):
    """Enable or disable AST printing globally"""
    global PRINT_AST_ENABLED
    PRINT_AST_ENABLED = enabled

def create_test_output_file(test_module_name):
    """Create output file for test results"""
    global current_test_file
    
    # Create output directory if it doesn't exist
    output_dir = "test_outputs"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/{test_module_name}_{timestamp}.txt"
    
    current_test_file = open(filename, 'w', encoding='utf-8')
    
    # Write header
    current_test_file.write(f"TEST OUTPUT: {test_module_name}\n")
    current_test_file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    current_test_file.write("="*80 + "\n\n")
    current_test_file.flush()
    
    print(f"Test output will be written to: {filename}")
    return filename

def close_test_output_file():
    """Close the current test output file"""
    global current_test_file
    if current_test_file:
        current_test_file.close()
        current_test_file = None

def write_to_file(text):
    """Write text to current test output file"""
    global current_test_file
    if current_test_file:
        current_test_file.write(text + "\n")
        current_test_file.flush()

def print_test_header(test_name, description):
    """Print test header"""
    header_text = "\n" + "="*80 + "\n"
    header_text += f"TEST: {test_name}\n"
    header_text += f"TESTING: {description}\n"
    header_text += "="*80
    
    write_to_file(header_text)
    print(f"Running: {test_name}")

def print_ast(ast, max_lines=50):
    """Print AST structure (only if enabled)"""
    if not PRINT_AST_ENABLED:
        write_to_file("\nAST PRINTING: Disabled (use --show-ast to enable)")
        return
        
    write_to_file("\nPROGRAM AST:")
    write_to_file("-"*60)
    try:
        ast_str = str(ast)
        lines = ast_str.split('\n')
        for i, line in enumerate(lines[:max_lines]):
            # Handle unicode characters for file output
            write_to_file(line.encode('utf-8', errors='replace').decode('utf-8'))
        if len(lines) > max_lines:
            write_to_file(f"... ({len(lines) - max_lines} more lines)")
    except Exception as e:
        write_to_file(f"Error printing AST: {e}")
    write_to_file("-"*60)

def print_outcome(success, details=""):
    """Print test outcome"""
    outcome_text = "\nTEST OUTCOME:\n"
    if success:
        outcome_text += "PASS"
        print("  PASS")
    else:
        outcome_text += f"FAIL: {details}"
        print(f"  FAIL: {details}")
    
    write_to_file(outcome_text)
    write_to_file("\n" + "="*80 + "\n")