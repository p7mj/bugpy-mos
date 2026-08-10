import ast
import operator
import sys

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow, ast.BitXor: operator.pow,  # ^ means exponent here
    ast.USub: operator.neg,
}

def _eval(node):
    """Recursively evaluate an AST node using only allowed operations."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp):
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("unsupported expression")

def main(args):
    if "-h" in args or "--help" in args:
        print("""
CALCULATOR
Usage:
  calculator <expression> [flags]

Parameters:
  expression: Evaluate the expression. If none, enters interactive mode.

Flags:
  -h: this help section

Notes:
  A program to make math class easier
        """)
        return

    # Interactive mode (bc-style)
    if not args:
        while True:
            try:
                user_input = input("> ").strip()
                if user_input.lower() == "quit" or user_input.lower() == "exit":
                    break
                if not user_input:
                    continue
                
                result = _eval(ast.parse(user_input, mode='eval').body)
                print(result)
            except Exception:
                print(f"calc: invalid expression")
        return

    # Single-shot command line mode
    expr = " ".join(args)
    try:
        result = _eval(ast.parse(expr, mode='eval').body)
        print(f"calc: {result}")
    except Exception:
        print(f"calc: invalid expression '{expr}'")