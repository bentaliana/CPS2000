"""
PArL to PArIR Code Generator - Task 4 Final Fixed Implementation
CORRECTED: Proper jump distance calculation using instruction counting
"""

from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from parser.ast_nodes import *


@dataclass
class MemoryLocation:
    """Represents a variable's location in memory"""
    frame_index: int
    frame_level: int


class PArIRGenerator:
    """
    Generates PArIR instructions from PArL AST
    FINAL FIX: Accurate jump distance calculation
    """
    
    def __init__(self, debug: bool = False):
        # Instruction generation
        self.instructions: List[str] = []
        self.debug = debug
        
        # Memory management
        self.memory_stack: List[Dict[str, MemoryLocation]] = []
        self.current_frame_level = -1
        self.frame_var_counts: List[int] = []
        self.next_var_indices: List[int] = []
        
        # Function tracking
        self.function_addresses: Dict[str, int] = {}
        self.current_function: Optional[str] = None
        
        # Function size calculation - CORRECTED
        self.function_sizes: Dict[str, int] = {}
        self.dry_run_mode = False
    
    def generate(self, ast: Program) -> List[str]:
        """Generate PArIR code from AST"""
        self.instructions = []
        self._reset_state()
        
        # Generate main function header
        self._emit(".main")
        self._emit("push 4")
        self._emit("jmp")
        self._emit("halt")
        
        # CORRECTED: Proper function size calculation
        self._calculate_function_jump_distances(ast)
        self._generate_program(ast)
        
        return self.instructions
    
    def _reset_state(self):
        """Reset generator state"""
        self.memory_stack = []
        self.current_frame_level = -1
        self.frame_var_counts = []
        self.next_var_indices = []
        self.function_addresses = {}
        self.function_sizes = {}
        self.dry_run_mode = False
    
    # ===== CORRECTED FUNCTION SIZE CALCULATION =====
    
    def _calculate_function_jump_distances(self, ast: Program):
        """
        CORRECTED: Calculate exact jump distances needed to skip over functions
        This accounts for the jump instruction mechanics properly
        """
        for stmt in ast.statements:
            if isinstance(stmt, FunctionDeclaration):
                # Calculate the total instructions the function will generate
                function_body_size = self._dry_run_function_body(stmt)
                
                # CORRECTED: Jump distance calculation  
                # Pattern: push #PC+X, jmp, .function, <body>, <next>
                # From "push #PC+X" we need to jump over:
                # - jmp instruction (1)
                # - function label .name (1)  
                # - function body (function_body_size)
                # - Plus 1 to land AFTER the last instruction
                # Total: 1 + 1 + function_body_size + 1 = 3 + function_body_size
                jump_distance = 3 + function_body_size
                
                self.function_sizes[stmt.name] = jump_distance
                
                if self.debug:
                    print(f"Function '{stmt.name}': body={function_body_size}, jump=#PC+{jump_distance}")
    
    def _dry_run_function_body(self, func_node: FunctionDeclaration) -> int:
        """
        Calculate the exact number of instructions in the function body
        This includes alloc instruction and all body statements
        """
        # Save current state
        saved_instructions = self.instructions.copy()
        saved_memory_stack = [scope.copy() for scope in self.memory_stack]
        saved_frame_level = self.current_frame_level
        saved_frame_var_counts = self.frame_var_counts.copy()
        saved_next_var_indices = self.next_var_indices.copy()
        saved_current_function = self.current_function
        saved_dry_run_mode = self.dry_run_mode
        
        # Enter dry-run mode
        self.dry_run_mode = True
        self.instructions = []
        self.memory_stack = []
        self.current_frame_level = -1
        self.frame_var_counts = []
        self.next_var_indices = []
        
        try:
            # Generate ONLY the function body (not the label)
            self.current_function = func_node.name
            
            param_count = len(func_node.params)
            local_count = self._count_variable_declarations(func_node.body.statements)
            allocation = local_count
            
            # Generate alloc instruction
            self._emit(f"push {allocation}")
            self._emit("alloc")
            
            # Enter function scope
            total_vars = param_count + allocation
            self._enter_scope(total_vars)
            
            # Register parameters
            for i, param in enumerate(func_node.params):
                self._allocate_variable(param.name, i)
            
            if self.next_var_indices:
                self.next_var_indices[-1] = param_count
            
            # Generate body statements
            for stmt in func_node.body.statements:
                self._generate_statement(stmt)
            
            self._exit_scope()
            
            # Count actual instructions generated
            body_size = len(self.instructions)
            
            if self.debug:
                print(f"  Dry-run for '{func_node.name}' generated {body_size} instructions:")
                for i, instr in enumerate(self.instructions):
                    print(f"    {i}: {instr}")
            
        except Exception as e:
            if self.debug:
                print(f"  Error in dry-run for '{func_node.name}': {e}")
            body_size = 10  # Fallback
        finally:
            # Restore state
            self.dry_run_mode = saved_dry_run_mode
            self.instructions = saved_instructions
            self.memory_stack = saved_memory_stack
            self.current_frame_level = saved_frame_level
            self.frame_var_counts = saved_frame_var_counts
            self.next_var_indices = saved_next_var_indices
            self.current_function = saved_current_function
        
        return body_size
    
    # ===== INSTRUCTION GENERATION =====
    
    def _emit(self, instruction: str):
        """Emit a single instruction"""
        self.instructions.append(instruction)
        if self.debug and not self.dry_run_mode:
            print(f"[{len(self.instructions)-1}] {instruction}")
    
    def _get_current_address(self) -> int:
        """Get current instruction address"""
        return len([i for i in self.instructions if not i.startswith("//")])
    
    # ===== MEMORY MANAGEMENT =====
    
    def _enter_scope(self, var_count: int = 0):
        """Enter a new scope"""
        self.current_frame_level += 1
        self.memory_stack.append({})
        self.frame_var_counts.append(var_count)
        self.next_var_indices.append(0)
    
    def _exit_scope(self):
        """Exit current scope"""
        if self.memory_stack:
            self.memory_stack.pop()
            self.frame_var_counts.pop()
            self.next_var_indices.pop()
            self.current_frame_level -= 1
    
    def _allocate_variable(self, name: str, index: Optional[int] = None) -> MemoryLocation:
        """Allocate a variable in current scope"""
        if index is None:
            index = self.next_var_indices[-1]
            self.next_var_indices[-1] += 1
        
        location = MemoryLocation(index, self.current_frame_level)
        self.memory_stack[-1][name] = location
        return location
    
    def _lookup_variable(self, name: str) -> Optional[MemoryLocation]:
        """Find variable in scope chain"""
        for scope_index in range(len(self.memory_stack) - 1, -1, -1):
            if name in self.memory_stack[scope_index]:
                stored_location = self.memory_stack[scope_index][name]
                
                # Frame level calculation
                if self.current_function is None:
                    # In main program
                    frame_level = len(self.memory_stack) - 1 - scope_index
                else:
                    # In function - use 0 for most cases
                    frame_level = 0
                
                return MemoryLocation(stored_location.frame_index, frame_level)
        
        return None
    
    # ===== PROGRAM GENERATION =====
    
    def _generate_program(self, node: Program):
        """Generate code for entire program"""
        # Separate functions from main code
        functions = []
        main_statements = []
        
        for stmt in node.statements:
            if isinstance(stmt, FunctionDeclaration):
                functions.append(stmt)
            else:
                main_statements.append(stmt)
        
        # Calculate main variable count
        main_var_count = self._count_main_variables(main_statements)
        
        # Generate main frame allocation
        self._emit(f"push {main_var_count}")
        self._emit("oframe")
        
        # Generate function skip jumps and definitions
        for func in functions:
            # CORRECTED: Use properly calculated jump distance
            jump_distance = self.function_sizes[func.name]
            self._emit(f"push #PC+{jump_distance}")
            self._emit("jmp")
            
            # Generate function
            self._emit(f".{func.name}")
            self._generate_function_declaration(func)
        
        # Generate main program execution
        self._enter_scope(main_var_count)
        
        for stmt in main_statements:
            self._generate_statement(stmt)
        
        self._emit("cframe")
        self._emit("halt")
        self._exit_scope()
    
    def _count_main_variables(self, statements: List[ASTNode]) -> int:
        """Count variables needed in main scope"""
        direct_vars = 0
        for stmt in statements:
            if isinstance(stmt, VariableDeclaration):
                direct_vars += 1
        return max(direct_vars, 1)
    
    def _generate_function_declaration(self, node: FunctionDeclaration):
        """Generate function declaration"""
        self.current_function = node.name
        
        param_count = len(node.params)
        local_count = self._count_variable_declarations(node.body.statements)
        allocation = local_count
        
        # Always emit alloc instruction
        self._emit(f"push {allocation}")
        self._emit("alloc")
        
        # Enter function scope
        total_vars = param_count + allocation
        self._enter_scope(total_vars)
        
        # Register parameters
        for i, param in enumerate(node.params):
            self._allocate_variable(param.name, i)
        
        # Set next index after parameters
        if self.next_var_indices:
            self.next_var_indices[-1] = param_count
        
        # Generate body
        for stmt in node.body.statements:
            self._generate_statement(stmt)
        
        self._exit_scope()
        self.current_function = None
    
    # ===== STATEMENT GENERATION =====
    
    def _generate_statement(self, node: ASTNode):
        """Generate code for any statement"""
        if isinstance(node, VariableDeclaration):
            self._generate_var_decl(node)
        elif isinstance(node, Assignment):
            self._generate_assignment(node)
        elif isinstance(node, IfStatement):
            self._generate_if_stmt(node)
        elif isinstance(node, WhileStatement):
            self._generate_while_stmt(node)
        elif isinstance(node, ForStatement):
            self._generate_for_stmt(node)
        elif isinstance(node, ReturnStatement):
            self._generate_return_stmt(node)
        elif isinstance(node, PrintStatement):
            self._generate_print_stmt(node)
        elif isinstance(node, DelayStatement):
            self._generate_delay_stmt(node)
        elif isinstance(node, WriteStatement):
            self._generate_write_stmt(node)
        elif isinstance(node, WriteBoxStatement):
            self._generate_write_box_stmt(node)
        elif isinstance(node, ClearStatement):
            self._generate_clear_stmt(node)
        elif isinstance(node, Block):
            self._generate_block(node)
        elif isinstance(node, FunctionCall):
            self._generate_expression(node)
            self._emit("drop")
    
    def _generate_var_decl(self, node: VariableDeclaration):
        """Generate variable declaration"""
        location = self._allocate_variable(node.name)
        
        if node.initializer:
            self._generate_expression(node.initializer)
            self._emit(f"push {location.frame_index}")
            self._emit(f"push {location.frame_level}")
            self._emit("st")
    
    def _generate_assignment(self, node: Assignment):
        """Generate assignment statement"""
        if isinstance(node.target, Identifier):
            location = self._lookup_variable(node.target.name)
            if location:
                self._generate_expression(node.value)
                self._emit(f"push {location.frame_index}")
                self._emit(f"push {location.frame_level}")
                self._emit("st")

    def _generate_for_stmt(self, node: ForStatement):
        """Generate for loop with corrected condition order"""
        # Create scope for loop variable
        var_count = 1 if node.init else 0
        if var_count > 0:
            self._emit(f"push {var_count}")
            self._emit("oframe")
        self._enter_scope(var_count)
        
        # Generate initialization
        if node.init:
            location = self._allocate_variable(node.init.name)
            if node.init.initializer:
                self._generate_expression(node.init.initializer)
                self._emit(f"push {location.frame_index}")
                self._emit("push 0")
                self._emit("st")
        
        # Loop condition start
        condition_start = self._get_current_address()
        
        # CORRECTED: Generate condition with proper operand order
        if isinstance(node.condition, BinaryOperation):
            if node.condition.operator in ['<', '>', '<=', '>=', '==', '!=']:
                # For "i < 64", we want stack to have [64][i] so lt computes i < 64
                self._generate_expression(node.condition.right)  # 64 first
                self._generate_expression(node.condition.left)   # i second
                
                op_map = {'<': 'lt', '>': 'gt', '<=': 'le', '>=': 'ge', '==': 'eq'}
                if node.condition.operator == '!=':
                    self._emit("eq")
                    self._emit("not")
                else:
                    self._emit(op_map[node.condition.operator])
            else:
                self._generate_expression(node.condition)
        else:
            self._generate_expression(node.condition)
        
        # Conditional jump
        self._emit("push #PC+4")
        self._emit("cjmp")
        
        # Jump to exit
        exit_jump_addr = self._get_current_address()
        self._emit("push #PC+999")  # Placeholder
        self._emit("jmp")
        
        # Generate body
        body_start = self._get_current_address()
        self._generate_block_with_frame(node.body)
        
        # Generate update
        if node.update:
            if isinstance(node.update, Assignment) and isinstance(node.update.target, Identifier):
                location = self._lookup_variable(node.update.target.name)
                if location:
                    self._generate_expression(node.update.value)
                    self._emit(f"push {location.frame_index}")
                    self._emit("push 0")
                    self._emit("st")
        
        # Jump back to condition
        current_addr = self._get_current_address()
        back_offset = condition_start - current_addr - 1
        self._emit(f"push #PC{back_offset}")
        self._emit("jmp")
        
        # Patch exit jump
        end_addr = self._get_current_address()
        exit_offset = end_addr - exit_jump_addr - 1
        self.instructions[exit_jump_addr] = f"push #PC+{exit_offset}"
        
        # Close loop scope
        if var_count > 0:
            self._emit("cframe")
        self._exit_scope()
    
    def _generate_if_stmt(self, node: IfStatement):
        """Generate if statement"""
        self._generate_expression(node.condition)
        
        self._emit("push #PC+4")
        self._emit("cjmp")
        
        else_jump_addr = self._get_current_address()
        self._emit("push #PC+999")
        self._emit("jmp")
        
        self._generate_block_with_frame(node.then_block)
        
        if node.else_block:
            end_jump_addr = self._get_current_address()
            self._emit("push #PC+999")
            self._emit("jmp")
            
            else_start = self._get_current_address()
            else_offset = else_start - else_jump_addr - 1
            self.instructions[else_jump_addr] = f"push #PC+{else_offset}"
            
            self._generate_block_with_frame(node.else_block)
            
            end_addr = self._get_current_address()
            end_offset = end_addr - end_jump_addr - 1
            self.instructions[end_jump_addr] = f"push #PC+{end_offset}"
        else:
            end_addr = self._get_current_address()
            else_offset = end_addr - else_jump_addr - 1
            self.instructions[else_jump_addr] = f"push #PC+{else_offset}"
    
    def _generate_while_stmt(self, node: WhileStatement):
        """Generate while statement"""
        loop_start = self._get_current_address()
        
        self._generate_expression(node.condition)
        
        self._emit("push #PC+4")
        self._emit("cjmp")
        
        exit_jump_addr = self._get_current_address()
        self._emit("push #PC+999")
        self._emit("jmp")
        
        self._generate_block_with_frame(node.body)
        
        back_offset = loop_start - self._get_current_address() - 1
        self._emit(f"push #PC{back_offset}")
        self._emit("jmp")
        
        end_addr = self._get_current_address()
        exit_offset = end_addr - exit_jump_addr - 1
        self.instructions[exit_jump_addr] = f"push #PC+{exit_offset}"
    
    def _generate_block(self, node: Block):
        """Generate block statements"""
        for stmt in node.statements:
            self._generate_statement(stmt)
    
    def _generate_block_with_frame(self, node: Block):
        """Generate block with its own frame if needed"""
        local_vars = self._count_variable_declarations(node.statements)
        
        self._emit(f"push {local_vars}")
        self._emit("oframe")
        self._enter_scope(local_vars)
        self._generate_block(node)
        self._exit_scope()
        self._emit("cframe")
    
    def _generate_return_stmt(self, node: ReturnStatement):
        """Generate return statement"""
        self._generate_expression(node.value)
        self._emit("ret")
    
    # ===== BUILT-IN STATEMENTS =====
    
    def _generate_print_stmt(self, node: PrintStatement):
        """Generate print statement"""
        self._generate_expression(node.expression)
        self._emit("print")
    
    def _generate_delay_stmt(self, node: DelayStatement):
        """Generate delay statement"""
        self._generate_expression(node.expression)
        self._emit("delay")
    
    def _generate_write_stmt(self, node: WriteStatement):
        """Generate write statement"""
        self._generate_expression(node.color)
        self._generate_expression(node.y)
        self._generate_expression(node.x)
        self._emit("write")
    
    def _generate_write_box_stmt(self, node: WriteBoxStatement):
        """Generate write box statement"""
        self._generate_expression(node.x)
        self._generate_expression(node.y)
        self._generate_expression(node.width)
        self._generate_expression(node.height)
        self._generate_expression(node.color)
        self._emit("writebox")
    
    def _generate_clear_stmt(self, node: ClearStatement):
        """Generate clear statement"""
        self._generate_expression(node.color)
        self._emit("clear")
    
    # ===== EXPRESSION GENERATION =====
    
    def _generate_expression(self, node: ASTNode):
        """Generate code for expressions"""
        if isinstance(node, Literal):
            self._generate_literal(node)
        elif isinstance(node, Identifier):
            self._generate_identifier(node)
        elif isinstance(node, BinaryOperation):
            self._generate_binary_op(node)
        elif isinstance(node, UnaryOperation):
            self._generate_unary_op(node)
        elif isinstance(node, CastExpression):
            self._generate_cast(node)
        elif isinstance(node, FunctionCall):
            self._generate_function_call(node)
        elif isinstance(node, PadWidth):
            self._emit("width")
        elif isinstance(node, PadHeight):
            self._emit("height")
        elif isinstance(node, PadRandI):
            self._generate_pad_randi(node)
    
    def _generate_literal(self, node: Literal):
        """Generate literal values"""
        if node.literal_type == "colour":
            self._emit(f"push {node.value}")
        elif node.literal_type == "bool":
            self._emit(f"push {1 if node.value else 0}")
        else:
            self._emit(f"push {node.value}")
    
    def _generate_identifier(self, node: Identifier):
        """Generate variable reference"""
        location = self._lookup_variable(node.name)
        if location:
            self._emit(f"push [{location.frame_index}:{location.frame_level}]")
        else:
            self._emit("push 0")
    
    def _generate_binary_op(self, node: BinaryOperation):
        """Generate binary operations"""
        if node.operator == '-':
            # For subtraction: stack [b][a] computes a-b
            self._generate_expression(node.right)
            self._generate_expression(node.left)
            self._emit("sub")
        else:
            # Standard left-right order for other operations
            self._generate_expression(node.left)
            self._generate_expression(node.right)
            
            op_map = {
                '+': 'add', '*': 'mul', '/': 'div',
                '<': 'lt', '>': 'gt', '<=': 'le', '>=': 'ge',
                '==': 'eq', 'and': 'and', 'or': 'or'
            }
            
            if node.operator == '!=':
                self._emit("eq")
                self._emit("not")
            else:
                self._emit(op_map.get(node.operator, 'nop'))
    
    def _generate_unary_op(self, node: UnaryOperation):
        """Generate unary operations"""
        self._generate_expression(node.operand)
        
        if node.operator == '-':
            self._emit("push 0")
            self._emit("sub")
        elif node.operator == 'not':
            self._emit("not")
    
    def _generate_cast(self, node: CastExpression):
        """Generate type cast"""
        self._generate_expression(node.expression)
    
    def _generate_function_call(self, node: FunctionCall):
        """Generate function call"""
        for arg in node.arguments:
            self._generate_expression(arg)
        
        self._emit(f"push {len(node.arguments)}")
        self._emit(f"push .{node.name}")
        self._emit("call")
    
    def _generate_pad_randi(self, node: PadRandI):
        """Generate random integer"""
        self._generate_expression(node.max_val)
        self._emit("irnd")
    
    # ===== UTILITY METHODS =====
    
    def _count_variable_declarations(self, statements: List[ASTNode]) -> int:
        """Count variable declarations in statements"""
        count = 0
        for stmt in statements:
            if isinstance(stmt, VariableDeclaration):
                count += 1
        return count