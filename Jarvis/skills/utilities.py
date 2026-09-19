"""Safe, deterministic utility commands that do not require an AI provider."""

import ast
import math
import operator
import re


SkillResult = tuple[str, str, str | None]
_OPERATORS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod, ast.Pow: operator.pow, ast.USub: operator.neg,
}


def is_utility_command(query: str) -> bool:
    return query.startswith(("calculate ", "what is ", "convert ", "uppercase ", "lowercase ", "count words ", "set a timer for "))


def _evaluate(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _evaluate(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
        left, right = _evaluate(node.left), _evaluate(node.right)
        if abs(left) > 1e12 or abs(right) > 1e12:
            raise ValueError("number too large")
        return _OPERATORS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPERATORS:
        return _OPERATORS[type(node.op)](_evaluate(node.operand))
    raise ValueError("unsupported expression")


def _calculate(query: str) -> SkillResult:
    expression = re.sub(r"^(calculate|what is)\s+", "", query).strip().rstrip("?")
    percent = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s+percent of\s+(-?\d+(?:\.\d+)?)", expression)
    if percent:
        result = float(percent.group(1)) * float(percent.group(2)) / 100
    else:
        square_root = re.fullmatch(r"(?:the )?square root of\s+(-?\d+(?:\.\d+)?)", expression)
        if square_root:
            result = math.sqrt(float(square_root.group(1)))
        else:
            expression = expression.replace("multiplied by", "*").replace("times", "*").replace("divided by", "/")
            expression = re.sub(r"\bplus\b", "+", expression)
            expression = re.sub(r"\bminus\b", "-", expression)
            result = _evaluate(ast.parse(expression, mode="eval"))
    rendered = f"{result:,.8f}".rstrip("0").rstrip(".")
    return f"The answer is {rendered}.", "speak", None


_CONVERSIONS = {
    ("kilometer", "mile"): 0.621371, ("mile", "kilometer"): 1.609344,
    ("meter", "feet"): 3.28084, ("foot", "meter"): 0.3048,
    ("kilogram", "pound"): 2.204623, ("pound", "kilogram"): 0.453592,
    ("liter", "gallon"): 0.264172, ("gallon", "liter"): 3.785412,
}


def _unit(word: str) -> str:
    aliases = {"km": "kilometer", "kilometers": "kilometer", "miles": "mile", "meters": "meter",
               "metres": "meter", "feet": "feet", "foot": "foot", "kg": "kilogram", "kilograms": "kilogram",
               "lbs": "pound", "pounds": "pound", "liters": "liter", "litres": "liter", "gallons": "gallon"}
    return aliases.get(word, word)


def _convert(query: str) -> SkillResult:
    match = re.fullmatch(r"convert\s+(-?\d+(?:\.\d+)?)\s+([a-z]+)\s+to\s+([a-z]+)", query)
    if not match:
        return "Say convert, a number, the source unit, and the target unit.", "speak", None
    value, source, target = float(match.group(1)), _unit(match.group(2)), _unit(match.group(3))
    if source == "celsius" and target == "fahrenheit":
        result = value * 9 / 5 + 32
    elif source == "fahrenheit" and target == "celsius":
        result = (value - 32) * 5 / 9
    else:
        factor = _CONVERSIONS.get((source, target))
        if factor is None:
            return f"I don't have a conversion from {source} to {target} yet.", "speak", None
        result = value * factor
    return f"{value:g} {source} is {result:,.2f} {target}.", "speak", None


def utility_command(query: str) -> SkillResult:
    try:
        if query.startswith(("calculate ", "what is ")):
            return _calculate(query)
        if query.startswith("convert "):
            return _convert(query)
        if query.startswith("uppercase "):
            return query.removeprefix("uppercase ").upper(), "speak", None
        if query.startswith("lowercase "):
            return query.removeprefix("lowercase ").lower(), "speak", None
        if query.startswith("count words "):
            text = query.removeprefix("count words ").strip()
            return f"That has {len(text.split())} words and {len(text)} characters.", "speak", None
        timer = re.search(r"set a timer for\s+(\d+)\s*(second|seconds|minute|minutes|hour|hours)", query)
        if timer:
            amount = int(timer.group(1))
            multiplier = 3600 if "hour" in timer.group(2) else 60 if "minute" in timer.group(2) else 1
            seconds = min(amount * multiplier, 86400)
            return f"Timer set for {amount} {timer.group(2)}.", "start_timer", str(seconds)
    except (ValueError, SyntaxError, ZeroDivisionError, OverflowError):
        return "I couldn't safely calculate that expression.", "speak", None
    return "I couldn't understand that utility command.", "speak", None
