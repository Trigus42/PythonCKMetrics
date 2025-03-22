"""
Precise tests for Chidamber & Kemerer metrics with exact expected values.
Each test case uses a small class with a specific feature to test exact metric values.
"""
import unittest
import tempfile
import os
from ck_metrics import process_path

class TestPreciseMetrics(unittest.TestCase):

    def run_test_on_code(self, code, expected_metrics):
        """Helper method to run a test on a given code snippet"""
        # Create a temporary file with the test code
        with tempfile.NamedTemporaryFile(suffix='.py', delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(code.encode('utf-8'))

        try:
            # Process the file
            metrics = process_path(temp_file_path)

            # Check each expected metric
            for class_name, expected_class_metrics in expected_metrics.items():
                self.assertIn(class_name, metrics['class_summary'],
                             f"Class {class_name} not found in metrics")

                actual_metrics = metrics['class_summary'][class_name]
                
                for metric_name, expected_value in expected_class_metrics.items():
                    if metric_name == 'methods':
                        # Check method metrics
                        for method_name, method_metrics in expected_value.items():
                            self.assertIn(method_name, actual_metrics['methods'],
                                         f"Method {method_name} not found")
                            
                            for m_name, m_value in method_metrics.items():
                                self.assertEqual(actual_metrics['methods'][method_name][m_name], m_value,
                                               f"Method {method_name} has incorrect {m_name}")
                    else:
                        # Check class-level metrics
                        self.assertEqual(actual_metrics[metric_name], expected_value,
                                        f"Class {class_name} has incorrect {metric_name}")
        
        finally:
            # Clean up
            os.unlink(temp_file_path)

    def test_empty_class(self):
        """Test metrics for an empty class"""
        code = """
class EmptyClass:
    pass
"""
        expected_metrics = {
            'EmptyClass': {
                'wmc': 0,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 0,
                'lcom4': 0,
                'methods': {}
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_single_method(self):
        """Test metrics for a class with a single simple method"""
        code = """
class SingleMethod:
    def simple_method(self):
        return 42
"""
        expected_metrics = {
            'SingleMethod': {
                'wmc': 1,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 1,  # Only the method itself
                'lcom4': 1,  # Single connected component
                'methods': {
                    'simple_method': {'complexity': 1}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_if_statement_complexity(self):
        """Test complexity calculation for if statements"""
        code = """
class IfComplexity:
    def if_method(self, x):
        if x > 0:
            return 1
        return 0
"""
        expected_metrics = {
            'IfComplexity': {
                'wmc': 2,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 1,
                'lcom4': 1,
                'methods': {
                    'if_method': {'complexity': 2}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_for_loop_complexity(self):
        """Test complexity calculation for for loops"""
        code = """
class ForComplexity:
    def for_method(self, items):
        result = 0
        for item in items:
            result += item
        return result
"""
        expected_metrics = {
            'ForComplexity': {
                'wmc': 2,  # Base 1 + for loop 1
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 1,
                'lcom4': 1,
                'methods': {
                    'for_method': {'complexity': 2}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_try_except_complexity(self):
        """Test complexity calculation for try-except blocks"""
        code = """
class TryExceptComplexity:
    def try_method(self, x):
        try:
            return 100 / x
        except ZeroDivisionError:
            return 0
"""
        expected_metrics = {
            'TryExceptComplexity': {
                'wmc': 2,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 1,
                'lcom4': 1,
                'methods': {
                    'try_method': {'complexity': 2}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_single_inheritance(self):
        """Test metrics for a simple inheritance case"""
        code = """
class Parent:
    def parent_method(self):
        return "parent"

class Child(Parent):
    def child_method(self):
        return "child"
"""
        expected_metrics = {
            'Parent': {
                'wmc': 1,
                'dit': 0,  # No parent
                'noc': 1,  # One child
                'cbo': 0,
                'rfc': 1,
                'lcom4': 1,
                'methods': {
                    'parent_method': {'complexity': 1}
                }
            },
            'Child': {
                'wmc': 1,
                'dit': 1,  # One level of inheritance
                'noc': 0,  # No children
                'cbo': 1,  # Coupled to Parent
                'rfc': 1,  # Only its own method
                'lcom4': 1,
                'methods': {
                    'child_method': {'complexity': 1}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_multi_level_inheritance(self):
        """Test metrics for multi-level inheritance"""
        code = """
class Grandparent:
    def grandparent_method(self):
        return "grandparent"

class Parent(Grandparent):
    def parent_method(self):
        return "parent"

class Child(Parent):
    def child_method(self):
        return "child"
"""
        expected_metrics = {
            'Grandparent': {
                'wmc': 1,
                'dit': 0,
                'noc': 1,  # One direct child
                'cbo': 0,
                'rfc': 1,
                'lcom4': 1,
                'methods': {
                    'grandparent_method': {'complexity': 1}
                }
            },
            'Parent': {
                'wmc': 1,
                'dit': 1,  # One level of inheritance
                'noc': 1,  # One direct child
                'cbo': 1,  # Coupled to Grandparent
                'rfc': 1,  # Only its own method
                'lcom4': 1,
                'methods': {
                    'parent_method': {'complexity': 1}
                }
            },
            'Child': {
                'wmc': 1,
                'dit': 2,  # Two levels of inheritance
                'noc': 0,  # No children
                'cbo': 1,  # Coupled to Parent
                'rfc': 1,  # Only its own method
                'lcom4': 1,
                'methods': {
                    'child_method': {'complexity': 1}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_method_calls(self):
        """Test RFC for a class with method calls"""
        code = """
class MethodCalls:
    def method1(self):
        return self.method2() + self.method3()

    def method2(self):
        return 2

    def method3(self):
        return 3
"""
        expected_metrics = {
            'MethodCalls': {
                'wmc': 3,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 3,  # All 3 methods are in the response set
                'lcom4': 1,  # One connected component
                'methods': {
                    'method1': {'complexity': 1},
                    'method2': {'complexity': 1},
                    'method3': {'complexity': 1}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_attribute_access(self):
        """Test LCOM4 for a class with attribute access"""
        code = """
class AttributeAccess:
    def __init__(self):
        self.attr1 = 1
        self.attr2 = 2

    def method1(self):
        return self.attr1

    def method2(self):
        return self.attr2

    def method3(self):
        return self.attr1 + self.attr2
"""
        expected_metrics = {
            'AttributeAccess': {
                'wmc': 4,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 4,
                'lcom4': 1,  # One connected component due to shared attributes
                'methods': {
                    '__init__': {'complexity': 1},
                    'method1': {'complexity': 1},
                    'method2': {'complexity': 1},
                    'method3': {'complexity': 1}
                }
            }
        }

        self.run_test_on_code(code, expected_metrics)

    def test_disconnected_methods(self):
        """Test LCOM4 for a class with disconnected methods"""
        code = """
class DisconnectedMethods:
    def __init__(self):
        self.attr1 = 1
        self.attr2 = 2
        self.attr3 = 3
    
    def group1_method1(self):
        return self.attr1
    
    def group1_method2(self):
        return self.attr1 * 2
    
    def group2_method1(self):
        return self.attr2
    
    def group2_method2(self):
        return self.attr2 * 2
"""
        expected_metrics = {
            'DisconnectedMethods': {
                'wmc': 5,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 5,
                'lcom4': 1,  # One connected component due to transitively connected methods
                'methods': {
                    '__init__': {'complexity': 1},
                    'group1_method1': {'complexity': 1},
                    'group1_method2': {'complexity': 1},
                    'group2_method1': {'complexity': 1},
                    'group2_method2': {'complexity': 1}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_ternary_conditional(self):
        """Test complexity for ternary conditionals"""
        code = """
class TernaryConditional:
    def ternary_method(self, x, y):
        return x if x > y else y
"""
        expected_metrics = {
            'TernaryConditional': {
                'wmc': 2,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 1,
                'lcom4': 1,
                'methods': {
                    'ternary_method': {'complexity': 2}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_list_comprehension(self):
        """Test complexity for list comprehensions with conditions"""
        code = """
class ListComprehension:
    def comprehension_method(self, items):
        return [x*2 for x in items if x > 0]
"""
        expected_metrics = {
            'ListComprehension': {
                'wmc': 2,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 1,
                'lcom4': 1,
                'methods': {
                    'comprehension_method': {'complexity': 2}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_boolean_operators(self):
        """Test complexity for boolean operators"""
        code = """
class BooleanOperators:
    def boolean_method(self, x, y, z):
        if x > 0 and y > 0 and z > 0:
            return True
        return False
"""
        expected_metrics = {
            'BooleanOperators': {
                'wmc': 4,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 1,
                'lcom4': 1,
                'methods': {
                    'boolean_method': {'complexity': 4}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_coupling(self):
        """Test CBO for classes with coupling"""
        code = """
class Helper:
    def help_method(self):
        return "helping"

class User:
    def __init__(self):
        self.helper = Helper()

    def use_helper(self):
        return self.helper.help_method()
"""
        expected_metrics = {
            'Helper': {
                'wmc': 1,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 1,
                'lcom4': 1,
                'methods': {
                    'help_method': {'complexity': 1}
                }
            },
            'User': {
                'wmc': 2,
                'dit': 0,
                'noc': 0,
                'cbo': 1,  # Coupled to Helper
                'rfc': 4,  # 2 own methods + helper init + help_method
                'lcom4': 1,
                'methods': {
                    '__init__': {'complexity': 1},
                    'use_helper': {'complexity': 1}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_lambda_complexity(self):
        """Test complexity for lambda functions"""
        code = """
class LambdaComplexity:
    def lambda_method(self, items):
        return list(map(lambda x: x * 2, items))
"""
        expected_metrics = {
            'LambdaComplexity': {
                'wmc': 1,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 1, # list and map are built-in functions
                'lcom4': 1,
                'methods': {
                    'lambda_method': {'complexity': 1}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_with_statement(self):
        """Test complexity for with statements"""
        code = """
class WithStatement:
    def with_method(self, filename):
        with open(filename, 'r') as f:
            return f.read()
"""
        expected_metrics = {
            'WithStatement': {
                'wmc': 1,
                'dit': 0,
                'noc': 0,
                'cbo': 1,  # Coupled to file handler
                'rfc': 2,
                'lcom4': 1,
                'methods': {
                    'with_method': {'complexity': 1}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_multiple_except_blocks(self):
        """Test complexity for multiple except blocks"""
        code = """
class MultipleExcepts:
    def except_method(self, x):
        try:
            result = 100 / x
            return result
        except ZeroDivisionError:
            return "Division by zero"
        except (TypeError, ValueError):
            return "Type or value error"
        except Exception as e:
            return f"Other error: {e}"
"""
        expected_metrics = {
            'MultipleExcepts': {
                'wmc': 4,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 1,
                'lcom4': 1,
                'methods': {
                    'except_method': {'complexity': 4}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_inheritance_with_overrides(self):
        """Test metrics for inheritance with method overrides"""
        code = """
class Base:
    def method(self):
        return "base"

class Derived(Base):
    def method(self):
        return "derived: " + super().method()
"""
        expected_metrics = {
            'Base': {
                'wmc': 1,
                'dit': 0,
                'noc': 1,
                'cbo': 0,
                'rfc': 1,
                'lcom4': 1,
                'methods': {
                    'method': {'complexity': 1}
                }
            },
            'Derived': {
                'wmc': 1,
                'dit': 1,
                'noc': 0,
                'cbo': 1,  # Coupled to Base
                'rfc': 2,  # Its own method and the inherited one
                'lcom4': 1,
                'methods': {
                    'method': {'complexity': 1}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)

    def test_nested_control_structures(self):
        """Test complexity for nested control structures"""
        code = """
class NestedControls:
    def nested_method(self, items):
        result = 0
        for item in items:
            if item > 0:
                for sub_item in range(item):
                    if sub_item % 2 == 0:
                        result += sub_item
        return result
"""
        expected_metrics = {
            'NestedControls': {
                'wmc': 5,
                'dit': 0,
                'noc': 0,
                'cbo': 0,
                'rfc': 1, # range is a built-in function
                'lcom4': 1,
                'methods': {
                    'nested_method': {'complexity': 5}
                }
            }
        }
        
        self.run_test_on_code(code, expected_metrics)


if __name__ == '__main__':
    unittest.main()