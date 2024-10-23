import re

class Node:
    def __init__(self, left=None, right=None, type=None, value=None):
        self.left = left
        self.right = right
        self.type = type
        self.value = value

    def to_dict(self):
        return {
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None,
            "type": self.type,
            "value": self.value
        }

def create_rule(rule_string):
    tokens = tokenize(rule_string)
    return build_ast(tokens)

def tokenize(rule_string):
    return re.findall(r"\(|\)|AND|OR|[<>=!]+\s?\w+\s?['\w]+", rule_string)

def build_ast(tokens):
    stack = []
    current_node = None

    for token in tokens:
        token = token.strip()

        if token in ('AND', 'OR'):
            if current_node is not None:
                operator_node = Node(left=current_node, right=None, type='operator', value=token)
                stack.append(operator_node)
                current_node = None
        elif token == '(':
            stack.append('(')
        elif token == ')':
            right_node = current_node
            while stack and stack[-1] != '(':
                operator_node = stack.pop()
                operator_node.right = right_node
                right_node = operator_node
            stack.pop()  # Remove '('
            current_node = right_node
        else:
            clean_value = token.strip()
            operand_node = Node(left=None, right=None, type='operand', value=clean_value)
            current_node = operand_node
    
    while stack:
        operator_node = stack.pop()
        operator_node.right = current_node
        current_node = operator_node

    return current_node

def combine_rules(rules, operator='AND'):
    """
    Combines multiple ASTs into one using the specified operator.
    """
    if not rules:
        return None
    root = rules[0]
    for rule in rules[1:]:
        
        combined_root = Node(left=root, right=rule, type='operator', value=operator)
        root = combined_root
    return root
        
def evaluate_rule(ast_node, data):
    """
    Evaluates the AST against the provided user data to check rule satisfaction.
    """
    if ast_node['type'] == 'operand':
        return eval_condition(ast_node['value'], data)
    elif ast_node['type'] == 'operator':
        left_result = evaluate_rule(ast_node['left'], data)
        right_result = evaluate_rule(ast_node['right'], data)
        if ast_node['value'] == 'AND':
            return left_result and right_result
        elif ast_node['value'] == 'OR':
            return left_result or right_result


def eval_condition(condition, data):
    attribute, operator, value = re.split(r'([<>=!]+)', condition.strip())
    attribute = attribute.strip()
    value = value.strip().strip("'")
    
    if operator == '>':
        return data[attribute] > float(value)
    elif operator == '<':
        return data[attribute] < float(value)
    elif operator == '>=':
        return data[attribute] >= float(value)
    elif operator == '<=':
        return data[attribute] <= float(value)
    elif operator == '==':
        return data[attribute] == value
    elif operator == '!=':
        return data[attribute] != value 
