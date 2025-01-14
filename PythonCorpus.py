import ast
from typing import Dict, List, Optional, Union, Set
from dataclasses import dataclass
from pathlib import Path
import tokenize
from collections import defaultdict
import json
import re

@dataclass
class CodeExample:
    """Represents a single code example"""
    code: str
    ast_tree: ast.AST
    patterns: List[str]
    complexity: int
    category: str
    source: str
    docstring: Optional[str]

class PythonCorpus:
    """Python code corpus manager"""
    
    def __init__(self, base_path: str = "corpus"):
        self.base_path = Path(base_path)
        self.examples: Dict[str, CodeExample] = {}
        self.patterns = defaultdict(list)
        self.categories = defaultdict(list)
        
    def add_example(self, 
                   name: str, 
                   code: str, 
                   category: str,
                   source: str = "user") -> None:
        """Add a code example to the corpus"""
        try:
            # Parse the code into AST
            tree = ast.parse(code)
            
            # Extract patterns
            patterns = self._extract_patterns(tree)
            
            # Calculate complexity
            complexity = self._calculate_complexity(tree)
            
            # Extract docstring
            docstring = ast.get_docstring(tree)
            
            # Create example
            example = CodeExample(
                code=code,
                ast_tree=tree,
                patterns=patterns,
                complexity=complexity,
                category=category,
                source=source,
                docstring=docstring
            )
            
            # Store example
            self.examples[name] = example
            self.categories[category].append(name)
            
            # Index patterns
            for pattern in patterns:
                self.patterns[pattern].append(name)
                
        except SyntaxError as e:
            print(f"Invalid Python code in example {name}: {e}")
    
    def _extract_patterns(self, tree: ast.AST) -> List[str]:
        """Extract common code patterns from AST"""
        patterns = []
        
        # Class patterns
        class_visitor = ClassPatternVisitor()
        class_visitor.visit(tree)
        patterns.extend(class_visitor.patterns)
        
        # Function patterns
        func_visitor = FunctionPatternVisitor()
        func_visitor.visit(tree)
        patterns.extend(func_visitor.patterns)
        
        return patterns
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate code complexity"""
        complexity_visitor = ComplexityVisitor()
        complexity_visitor.visit(tree)
        return complexity_visitor.complexity
    
    def search(self, 
              pattern: Optional[str] = None,
              category: Optional[str] = None,
              complexity_range: Optional[tuple] = None) -> List[str]:
        """Search for examples matching criteria"""
        results = set(self.examples.keys())
        
        if pattern:
            pattern_matches = set(self.patterns.get(pattern, []))
            results &= pattern_matches
        
        if category:
            category_matches = set(self.categories.get(category, []))
            results &= category_matches
        
        if complexity_range:
            min_complexity, max_complexity = complexity_range
            complexity_matches = {
                name for name, example in self.examples.items()
                if min_complexity <= example.complexity <= max_complexity
            }
            results &= complexity_matches
        
        return list(results)
    
    def save(self, filename: str) -> None:
        """Save corpus to file"""
        data = {
            name: {
                'code': example.code,
                'category': example.category,
                'patterns': example.patterns,
                'complexity': example.complexity,
                'source': example.source,
                'docstring': example.docstring
            }
            for name, example in self.examples.items()
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self, filename: str) -> None:
        """Load corpus from file"""
        with open(filename, 'r') as f:
            data = json.load(f)
        
        for name, example_data in data.items():
            self.add_example(
                name=name,
                code=example_data['code'],
                category=example_data['category'],
                source=example_data['source']
            )

class ClassPatternVisitor(ast.NodeVisitor):
    """Visit class definitions to extract patterns"""
    
    def __init__(self):
        self.patterns = []
        
    def visit_ClassDef(self, node):
        # Check for inheritance
        if node.bases:
            self.patterns.append('inheritance')
        
        # Check for decorators
        if node.decorator_list:
            self.patterns.append('class_decorator')
        
        # Check for special methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name.startswith('__') and item.name.endswith('__'):
                    self.patterns.append('special_method')
                    break
        
        self.generic_visit(node)

class FunctionPatternVisitor(ast.NodeVisitor):
    """Visit function definitions to extract patterns"""
    
    def __init__(self):
        self.patterns = []
        
    def visit_FunctionDef(self, node):
        # Check for decorators
        if node.decorator_list:
            self.patterns.append('function_decorator')
        
        # Check for type hints
        if node.returns or any(isinstance(arg.annotation, ast.AST) 
                             for arg in node.args.args):
            self.patterns.append('type_hints')
        
        # Check for default arguments
        if node.args.defaults:
            self.patterns.append('default_arguments')
        
        self.generic_visit(node)

class ComplexityVisitor(ast.NodeVisitor):
    """Calculate code complexity"""
    
    def __init__(self):
        self.complexity = 1
        
    def visit_If(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_Try(self, node):
        self.complexity += len(node.handlers)
        self.generic_visit(node)

# Example usage
if __name__ == "__main__":
    # Initialize corpus
    corpus = PythonCorpus()
    
    # Add some examples
    corpus.add_example(
        name="decorator_example",
        code="""
        def my_decorator(func):
            def wrapper(*args, **kwargs):
                print("Before function")
                result = func(*args, **kwargs)
                print("After function")
                return result
            return wrapper
            
        @my_decorator
        def example():
            print("Inside function")
        """,
        category="decorators"
    )
    
    corpus.add_example(
        name="class_example",
        code="""
        class MyClass:
            def __init__(self, value):
                self.value = value
                
            def __str__(self):
                return str(self.value)
                
            def process(self):
                return self.value * 2
        """,
        category="classes"
    )
    
    # Search examples
    decorator_examples = corpus.search(pattern="function_decorator")
    print("Examples with decorators:", decorator_examples)
    
    # Save corpus
    corpus.save("python_corpus.json")
