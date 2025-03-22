"""
Chidamber & Kemerer Metrics Suite Implementation
Calculate object-oriented metrics for Python code
"""

import ast
import os
from typing import Dict, List, Set, TypedDict, Optional, Union, Tuple, Any
import networkx as nx

class MethodMetrics(TypedDict):
    """TypedDict for method-level metrics"""
    complexity: int


class ClassMetrics(TypedDict):
    """TypedDict for class-level metrics"""
    wmc: int                # Weighted Methods per Class
    dit: int                # Depth of Inheritance Tree
    noc: int                # Number of Children
    cbo: int                # Coupling Between Object Classes
    rfc: int                # Response For a Class
    lcom4: int              # Lack of Cohesion in Methods
    lcom4_normalized: float # Normalized Lack of Cohesion in Methods
    methods: Dict[str, MethodMetrics]  # Method-level metrics


class FileMetrics(TypedDict):
    """TypedDict for file-level metrics"""
    classes: Dict[str, ClassMetrics]
    path: str


class ProjectMetrics(TypedDict):
    """TypedDict for project-level metrics"""
    files: Dict[str, FileMetrics]
    class_summary: Dict[str, ClassMetrics]  # Merged class metrics across files


class ClassInfo:
    """Class to store information about a Python class"""
    def __init__(self, name: str, bases: List[str]):
        self.name = name
        self.bases = bases
        self.methods: Set[str] = set()
        self.attributes: Set[str] = set()
        self.method_calls: Dict[str, Set[str]] = {}  # method -> set of called methods
        self.method_attrs: Dict[str, Set[str]] = {}  # method -> set of used attributes
        self.called_classes: Set[str] = set()        # classes being called
        self.method_complexity: Dict[str, int] = {}  # method -> complexity


class ComplexityVisitor(ast.NodeVisitor):
    """
    AST visitor that calculates cyclomatic complexity
    Handles complex scenarios like: conditionals, loops, comprehensions,
    try-except blocks, match statements, etc.
    """
    def __init__(self):
        self.complexity = 1  # Base complexity of 1

    def visit_If(self, node: ast.If) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        # Add complexity for and/or operators
        if isinstance(node.op, (ast.And, ast.Or)):
            self.complexity += len(node.values) - 1
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        # The try block itself is not a branch point
        # Except handlers will be counted in visit_ExceptHandler
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        self.complexity += 1
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        # Add 1 for each if condition in the comprehension
        for generator in node.generators:
            self.complexity += len(generator.ifs)
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        # Add 1 for each if condition in the comprehension
        for generator in node.generators:
            self.complexity += len(generator.ifs)
        self.generic_visit(node)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        # Add 1 for each if condition in the comprehension
        for generator in node.generators:
            self.complexity += len(generator.ifs)
        self.generic_visit(node)

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        # Add 1 for each if condition in the generator expression
        for generator in node.generators:
            self.complexity += len(generator.ifs)
        self.generic_visit(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        # Lambda itself isn't a branch point, don't increase complexity
        self.generic_visit(node)

    def visit_Match(self, node: Any) -> None:
        # For Python 3.10+ match statements
        # Add 1 for match and 1 for each case
        if hasattr(ast, 'Match') and isinstance(node, ast.Match):
            self.complexity += 1  # For the match itself
            self.complexity += len(node.cases)  # For each case
            self.generic_visit(node)

    def visit_IfExp(self, node: ast.IfExp) -> None:
        """Handle ternary conditionals: x if condition else y"""
        self.complexity += 1
        self.generic_visit(node)

    def visit_Assert(self, node: ast.Assert) -> None:
        """Handle assert statements"""
        # Asserts enforce invariants, they are not branch points
        # If in a try block, it will be counted separately
        self.generic_visit(node)

    def visit_Yield(self, node: ast.Yield) -> None:
        """Handle yield statements in generator functions"""
        # Return isn't a branch point, don't increase complexity
        self.generic_visit(node)

    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:
        """Handle 'yield from' expressions"""
        # Return isn't a branch point, don't increase complexity
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        """Handle returns"""
        # Return isn't a branch point, don't increase complexity
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        """Handle raise statements"""
        # Raise isn't a branch point, don't increase complexity
        # If it is in a try block, it will be counted separately
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        """Handle walrus operator (:=)"""
        # Walrus operator isn't a branch point, don't increase complexity
        self.generic_visit(node)

class MethodVisitor(ast.NodeVisitor):
    """
    Visit AST nodes to extract method calls and attribute access
    Enhanced to handle complex scenarios
    """

    def __init__(self):
        self.method_calls: Set[str] = set()
        self.attributes: Set[str] = set()
        self.classes: Set[str] = set()

    def visit_Call(self, node: ast.Call) -> None:
        """Process method calls"""
        if isinstance(node.func, ast.Name):
            self.method_calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                # Could be a class method call or instance method call
                self.classes.add(node.func.value.id)
            self.method_calls.add(node.func.attr)

        # Continue walking
        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> None:
        """Process attribute access"""
        if isinstance(node.value, ast.Name) and node.value.id == 'self':
            self.attributes.add(node.attr)

        # Continue walking
        self.generic_visit(node)

    def visit_Try(self, node: ast.Try) -> None:
        """Process try-except blocks"""
        # Visit try body
        for item in node.body:
            self.visit(item)

        # Visit except handlers
        for handler in node.handlers:
            self.visit(handler)

        # Visit else block if it exists
        if node.orelse:
            for item in node.orelse:
                self.visit(item)

        # Visit finally block if it exists
        if node.finalbody:
            for item in node.finalbody:
                self.visit(item)

    def visit_With(self, node: ast.With) -> None:
        """Process with statements"""
        # Visit each context manager
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars:
                self.visit(item.optional_vars)

        # Visit body
        for item in node.body:
            self.visit(item)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        """Process async with statements"""
        # Visit each context manager
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars:
                self.visit(item.optional_vars)

        # Visit body
        for item in node.body:
            self.visit(item)

    def visit_ListComp(self, node: ast.ListComp) -> None:
        """Process list comprehensions"""
        self.visit(node.elt)
        for generator in node.generators:
            self.visit(generator.iter)
            self.visit(generator.target)
            for if_clause in generator.ifs:
                self.visit(if_clause)

    def visit_DictComp(self, node: ast.DictComp) -> None:
        """Process dictionary comprehensions"""
        self.visit(node.key)
        self.visit(node.value)
        for generator in node.generators:
            self.visit(generator.iter)
            self.visit(generator.target)
            for if_clause in generator.ifs:
                self.visit(if_clause)

    def visit_SetComp(self, node: ast.SetComp) -> None:
        """Process set comprehensions"""
        self.visit(node.elt)
        for generator in node.generators:
            self.visit(generator.iter)
            self.visit(generator.target)
            for if_clause in generator.ifs:
                self.visit(if_clause)
    
    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        """Process generator expressions"""
        self.visit(node.elt)
        for generator in node.generators:
            self.visit(generator.iter)
            self.visit(generator.target)
            for if_clause in generator.ifs:
                self.visit(if_clause)

    def visit_Match(self, node: Any) -> None:
        """Process match statements (Python 3.10+)"""
        if hasattr(ast, 'Match') and isinstance(node, ast.Match):
            self.visit(node.subject)
            for case in node.cases:
                self.visit(case)


class CKMetrics:
    """Calculate Chidammer & Kemerer metrics for Python code"""

    def __init__(self, class_filter: Optional[List[str]] = None):
        """
        Initialize CK metrics analyzer with optional class name filter
        
        Args:
            class_filter: Optional list of class names to analyze. If provided,
                         only classes whose names are in this list will be analyzed.
        """
        self.classes: Dict[str, ClassInfo] = {}
        self.inheritance_graph = nx.DiGraph()
        self.file_paths: Dict[str, str] = {}  # class name -> file path
        self.class_filter = class_filter  # List of class names to analyze
    
    def parse_file(self, file_path: str) -> None:
        """Parse a Python file and extract class information"""
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        try:
            tree = ast.parse(code)
            self._process_ast(tree, file_path)
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
    
    def parse_directory(self, dir_path: str) -> None:
        """Parse all Python files in a directory recursively"""
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.py'):
                    self.parse_file(os.path.join(root, file))
    
    def _process_ast(self, tree: ast.AST, file_path: str) -> None:
        """Process AST and extract class information"""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Skip if class filter is active and class name is not in filter
                if self.class_filter is not None and node.name not in self.class_filter:
                    continue
                    
                bases = [base.id if isinstance(base, ast.Name) else self._get_attribute_name(base)
                         for base in node.bases if isinstance(base, (ast.Name, ast.Attribute))]
                
                class_name = node.name
                self.file_paths[class_name] = file_path
                
                class_info = ClassInfo(class_name, bases)
                self.classes[class_name] = class_info
                
                # Add inheritance relationships to graph
                self.inheritance_graph.add_node(class_name)
                for base in bases:
                    if base != 'object':  # Skip 'object' as it's the default base
                        self.inheritance_graph.add_edge(base, class_name)
                
                # Process methods and attributes
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) or isinstance(item, ast.AsyncFunctionDef):
                        method_name = item.name
                        class_info.methods.add(method_name)
                        
                        # Method visitor to find calls and attribute access
                        method_visitor = MethodVisitor()
                        method_visitor.visit(item)
                        
                        # Complexity visitor to calculate complexity
                        complexity_visitor = ComplexityVisitor()
                        complexity_visitor.visit(item)
                        
                        class_info.method_calls[method_name] = method_visitor.method_calls
                        class_info.method_attrs[method_name] = method_visitor.attributes
                        class_info.called_classes.update(method_visitor.classes)
                        class_info.method_complexity[method_name] = complexity_visitor.complexity
                    
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                class_info.attributes.add(target.id)
                            elif isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                class_info.attributes.add(target.attr)
                    
                    elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Name):
                        class_info.attributes.add(item.target.id)
                    elif isinstance(item, ast.AnnAssign) and isinstance(item.target, ast.Attribute) and isinstance(item.target.value, ast.Name) and item.target.value.id == 'self':
                        class_info.attributes.add(item.target.attr)
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get full name of an attribute (e.g., module.Class)"""
        parts = []
        current = node
        while isinstance(current, ast.Attribute):
            parts.insert(0, current.attr)
            current = current.value
        
        if isinstance(current, ast.Name):
            parts.insert(0, current.id)
        
        return '.'.join(parts)
    
    def calculate_metrics(self) -> ProjectMetrics:
        """Calculate all CK metrics for the parsed code"""
        result: ProjectMetrics = {
            'files': {},
            'class_summary': {}
        }
        
        # Create reverse mapping for file to classes
        file_to_classes: Dict[str, List[str]] = {}
        for class_name, file_path in self.file_paths.items():
            if file_path not in file_to_classes:
                file_to_classes[file_path] = []
            file_to_classes[file_path].append(class_name)
        
        # Calculate metrics for each class
        for class_name, class_info in self.classes.items():
            class_metrics = self._calculate_class_metrics(class_name, class_info)
            
            # Add to class summary
            result['class_summary'][class_name] = class_metrics
            
            # Add to file metrics
            file_path = self.file_paths.get(class_name, "unknown")
            if file_path not in result['files']:
                result['files'][file_path] = {
                    'classes': {},
                    'path': file_path
                }
            
            result['files'][file_path]['classes'][class_name] = class_metrics
        
        return result
    
    def _calculate_class_metrics(self, class_name: str, class_info: ClassInfo) -> ClassMetrics:
        """Calculate all metrics for a single class"""
        wmc = self._calculate_wmc(class_info)
        dit = self._calculate_dit(class_name)
        noc = self._calculate_noc(class_name)
        cbo = self._calculate_cbo(class_name, class_info)
        rfc = self._calculate_rfc(class_info)
        lcom4 = self._calculate_lcom4(class_info)
        lcom4_normalized = self._calculate_normalized_lcom4(class_info, lcom4)
        
        methods_dict = {method: {'complexity': class_info.method_complexity.get(method, 1)}
                       for method in class_info.methods}
        
        return {
            'wmc': wmc,
            'dit': dit,
            'noc': noc,
            'cbo': cbo,
            'rfc': rfc,
            'lcom4': lcom4,
            'lcom4_normalized': lcom4_normalized,
            'methods': methods_dict
        }
    
    def _calculate_wmc(self, class_info: ClassInfo) -> int:
        """Calculate Weighted Methods per Class (sum of method complexities)"""
        return sum(class_info.method_complexity.get(method, 1) for method in class_info.methods)
    
    def _calculate_dit(self, class_name: str) -> int:
        """Calculate Depth of Inheritance Tree"""
        # Find all paths from any root to this class
        # Return the maximum length
        if class_name not in self.inheritance_graph:
            return 0
        
        # Find roots (nodes with no incoming edges)
        roots = [node for node in self.inheritance_graph.nodes() 
                if self.inheritance_graph.in_degree(node) == 0]
        
        max_depth = 0
        for root in roots:
            try:
                # Find paths from root to class_name
                paths = list(nx.all_simple_paths(self.inheritance_graph, root, class_name))
                if paths:
                    # Length of the path is the number of edges, which is nodes - 1
                    max_depth = max(max_depth, max(len(path) - 1 for path in paths))
            except nx.NetworkXNoPath:
                pass
        
        return max_depth
    
    def _calculate_noc(self, class_name: str) -> int:
        """Calculate Number of Children (direct subclasses)"""
        if class_name not in self.inheritance_graph:
            return 0
        
        return len(list(self.inheritance_graph.successors(class_name)))

    def _calculate_cbo(self, class_name: str, class_info: ClassInfo) -> int:
        """Calculate Coupling Between Object Classes"""
        # Start with bases and directly called classes
        coupled_classes = set(class_info.bases + list(class_info.called_classes))

        # Check for instance creation and attribute references
        for method_name, method_calls in class_info.method_calls.items():
            for called_class in method_calls:
                if called_class in self.classes and called_class != class_name:
                    coupled_classes.add(called_class)

        for attr in class_info.attributes:
            if attr in self.classes and attr != class_name:
                coupled_classes.add(attr)

        # Remove standard class and self
        if 'object' in coupled_classes:
            coupled_classes.remove('object')
        if 'self' in coupled_classes:
            coupled_classes.remove('self')

        return len(coupled_classes)

    def _calculate_rfc(self, class_info: ClassInfo) -> int:
        """Calculate Response For a Class"""
        # Count own methods and all called methods
        response_set = set(class_info.methods)

        for called_methods in class_info.method_calls.values():
            # Exclude built-in functions
            response_set.update(method for method in called_methods if not self._is_builtin_function(method))

        return len(response_set)

    def _is_builtin_function(self, method_name: str) -> bool:
        """Check if a method name corresponds to a built-in function"""
        # List of built-in functions that can interact with user-defined classes
        # Note: This is not exhaustive and may need to be updated
        special_builtins = {"super", "getattr", "setattr", "delattr", "hasattr", "type", "dir"}
        if method_name in special_builtins:
            return False

        built_ins = __builtins__ if isinstance(__builtins__, dict) else __builtins__.__dict__
        if method_name not in built_ins:
            return False

        return True

    def _calculate_lcom4(self, class_info: ClassInfo) -> int:
        """Calculate Lack of Cohesion in Methods (LCOM4)"""
        if not class_info.methods:
            return 0

        # Create graph where nodes are methods
        graph = nx.Graph()

        # Add all methods as nodes
        for method in class_info.methods:
            graph.add_node(method)

        # Add edges between methods that share attributes
        for method1 in class_info.methods:
            attrs1 = class_info.method_attrs.get(method1, set())

            # Add edges for shared attributes
            for method2 in class_info.methods:
                if method1 != method2:
                    attrs2 = class_info.method_attrs.get(method2, set())
                    if attrs1.intersection(attrs2):
                        graph.add_edge(method1, method2)

            # Add edges for method calls
            for called in class_info.method_calls.get(method1, set()):
                if called in class_info.methods:
                    graph.add_edge(method1, called)

        # Count connected components
        return nx.number_connected_components(graph)
    
    def _calculate_normalized_lcom4(self, class_info: ClassInfo, lcom4: int) -> float:
        """
        Calculate Normalized LCOM4 - ranges from 0 to 1
        
        0 = perfect cohesion (single connected component)
        1 = complete lack of cohesion (each method is isolated)

        Formula: (LCOM4 - 1) / (M - 1) if M > 1, else 0
        where M is the number of methods in the class
        """
        method_count = len(class_info.methods)

        if method_count <= 1:
            # Classes with 0 or 1 methods have perfect cohesion by definition
            return 0.0

        # Normalize to range 0-1
        return (lcom4 - 1) / (method_count - 1)


def process_path(path: str, class_filter: Optional[List[str]] = None) -> ProjectMetrics:
    """
    Process a file or directory and calculate CK metrics
    
    Args:
        path: Path to Python file or directory with Python files
        class_filter: Optional list of class names to analyze. If provided,
                     only classes whose names are in this list will be analyzed.
    
    Returns:
        ProjectMetrics object with calculated metrics
    """
    analyzer = CKMetrics(class_filter)

    if os.path.isfile(path) and path.endswith('.py'):
        analyzer.parse_file(path)
    elif os.path.isdir(path):
        analyzer.parse_directory(path)
    else:
        raise ValueError(f"Path {path} is not a Python file or directory")

    return analyzer.calculate_metrics()
