"""
tools/calculator.py
Evaluates arithmetic / math expressions WITHOUT calling eval() or exec().
Walks a parsed AST and only allows a fixed whitelist of numeric
operators and math functions — this is the "safe calculator" pattern,
distinct from the sandboxed general-purpose code executor.
"""

import ast
import math
import operator as op

_ALLOWED_BINOPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.FloorDiv: op.floordiv,
}
_ALLOWED_UNARYOPS = {
    ast.UAdd: op.pos,
    ast.USub: op.neg,
}
_ALLOWED_FUNCS = {
    "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "log": math.log, "log10": math.log10, "exp": math.exp, "pow": math.pow,
    "abs": abs, "round": round, "floor": math.floor, "ceil": math.ceil,
    "factorial": math.factorial,
}
_ALLOWED_CONSTS = {"pi": math.pi, "e": math.e, "tau": math.tau}


class CalculatorError(Exception):
    pass


def _eval_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise CalculatorError(f"Unsupported literal: {node.value!r}")

    if isinstance(node, ast.BinOp):
        op_fn = _ALLOWED_BINOPS.get(type(node.op))
        if op_fn is None:
            raise CalculatorError(f"Operator {type(node.op).__name__} is not allowed")
        return op_fn(_eval_node(node.left), _eval_node(node.right))

    if isinstance(node, ast.UnaryOp):
        op_fn = _ALLOWED_UNARYOPS.get(type(node.op))
        if op_fn is None:
            raise CalculatorError(f"Unary operator {type(node.op).__name__} not allowed")
        return op_fn(_eval_node(node.operand))

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in _ALLOWED_FUNCS:
            name = getattr(node.func, "id", "?")
            raise CalculatorError(f"Function '{name}' is not allowed")
        args = [_eval_node(a) for a in node.args]
        return _ALLOWED_FUNCS[node.func.id](*args)

    if isinstance(node, ast.Name):
        if node.id in _ALLOWED_CONSTS:
            return _ALLOWED_CONSTS[node.id]
        raise CalculatorError(f"Unknown identifier '{node.id}'")

    raise CalculatorError(f"Unsupported expression element: {type(node).__name__}")


def run(expression: str) -> dict:
    expr = expression.strip()
    # Strip a leading "calculate"/"what is" style phrasing if present.
    for prefix in ("calculate", "what is", "compute", "evaluate"):
        if expr.lower().startswith(prefix):
            expr = expr[len(prefix):].strip(" :?")

    try:
        tree = ast.parse(expr, mode="eval")
        result = _eval_node(tree.body)
        return {
            "ok": True,
            "output": f"{result:g}" if isinstance(result, float) else str(result),
            "meta": {"expression": expr},
        }
    except (CalculatorError, SyntaxError, ZeroDivisionError, ValueError, TypeError) as exc:
        return {
            "ok": False,
            "output": f"Could not evaluate '{expr}': {exc}",
            "meta": {"expression": expr, "error_type": type(exc).__name__},
        }
