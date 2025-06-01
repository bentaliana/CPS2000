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
test_counter = 0

def set_ast_printing(enabled):
    """Enable or disable AST printing globally"""
    global PRINT_AST_ENABLED
    PRINT_AST_ENABLED = enabled

def create_test_output_file(task_name, test_name):
    """Create output file for individual test results"""
    global current_test_file, test_counter
    test_counter += 1
    
    # Create output directory structure
    output_dir = f"test_outputs/{task_name}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Clean test name for filename
    clean_name = "".join(c for c in test_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    clean_name = clean_name.replace(' ', '_').lower()
    
    # Create numbered filename
    filename = f"{output_dir}/example_{test_counter}_{clean_name}.txt"
    
    current_test_file = open(filename, 'w', encoding='utf-8')
    
    # Write header
    current_test_file.write(f"TEST: {test_name}\n")
    current_test_file.write(f"TASK: {task_name.upper()}\n")
    current_test_file.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    current_test_file.write("="*80 + "\n\n")
    current_test_file.flush()
    
    print(f"Test output: {filename}")
    return filename

def create_parir_output_file(task_name, test_name, instructions):
    """Create PArIR output file only for simulator tests"""
    if task_name.lower() != 'simulator':
        return  # Only create PArIR files for simulator tests
    
    # Create output directory structure
    output_dir = f"test_outputs/{task_name}"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Clean test name for filename
    clean_name = "".join(c for c in test_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    clean_name = clean_name.replace(' ', '_').lower()
    
    # Create timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{output_dir}/{clean_name}_{timestamp}.parir"
    
    # Write PArIR instructions
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"// PArIR for: {test_name}\n")
        f.write(f"// Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("// " + "="*76 + "\n\n")
        
        for instruction in instructions:
            f.write(instruction + "\n")
    
    print(f"PArIR saved to: {filename}")
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
    """Print test header with improved formatting"""
    header_text = f"TEST: {test_name}"
    header_text += f"\nPURPOSE: {description}"
    header_text += "\n" + "-"*80
    
    write_to_file(header_text)
    print(f"Running: {test_name}")

def print_ast(ast, max_lines= 400):
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

def print_completion_status(phase, success=True):
    """Print phase completion status"""
    if success:
        status_text = f"\n{phase.upper()}: Successfully completed"
        print(f"  {phase}: Success")
    else:
        status_text = f"\n{phase.upper()}: Completed with issues"
        print(f"  {phase}: Issues detected")
    
    write_to_file(status_text)
    write_to_file("\n" + "="*80 + "\n")

def reset_test_counter():
    """Reset test counter for new task"""
    global test_counter
    test_counter = 0

# Backward compatibility
def print_status(status, details=""):
    """Legacy function for backward compatibility"""
    if "SUCCESSFUL" in status or "COMPLETE" in status:
        print_completion_status("Compilation", True)
    else:
        print_completion_status("Compilation", False)

def print_outcome(success, details=""):
    """Legacy function for backward compatibility"""
    print_completion_status("Processing", success)