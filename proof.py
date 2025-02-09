from typing import Dict, Union, Tuple

# === Type System (Extended Curry-Howard) ===
class Type:
    """Base class for types in our system."""
    def __str__(self):
        return self.__repr__()

class Int(Type):
    """Integer Type (Peano arithmetic proof)."""
    def __repr__(self):
        return "Int"

class Bool(Type):
    """Boolean Type (Classical logic proposition)."""
    def __repr__(self):
        return "Bool"

class Function(Type):
    """Function Type (Corresponds to implication in logic)."""
    def __init__(self, input_type: Type, output_type: Type):
        self.input_type = input_type
        self.output_type = output_type

    def __repr__(self):
        return f"({self.input_type} → {self.output_type})"

class DependentFunction(Type):
    """Dependent Function Type (Π-type: Maps a value to a type)."""
    def __init__(self, param_name: str, param_type: Type, return_type_fn):
        self.param_name = param_name
        self.param_type = param_type
        self.return_type_fn = return_type_fn  # Function that returns a type

    def __repr__(self):
        return f"(Π {self.param_name}: {self.param_type}. {self.return_type_fn(self.param_name)})"

class LinearType(Type):
    """Linear Type (Must be used exactly once)."""
    def __init__(self, base_type: Type):
        self.base_type = base_type

    def __repr__(self):
        return f"Linear[{self.base_type}]"

class EffectfulType(Type):
    """Effect Tracking Type (IO, mutation, etc.)."""
    def __init__(self, effect: str, base_type: Type):
        self.effect = effect
        self.base_type = base_type

    def __repr__(self):
        return f"Effect[{self.effect}, {self.base_type}]"

# === Expressions (Lambda Calculus with Dependent Types) ===
class Expr:
    """Base class for expressions."""
    pass

class Var(Expr):
    """Variable expression (Typed via context)."""
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

class Lambda(Expr):
    """Lambda abstraction λx.e (Function in Type System)."""
    def __init__(self, param: str, param_type: Type, body: Expr):
        self.param = param
        self.param_type = param_type
        self.body = body

    def __repr__(self):
        return f"(λ{self.param}: {self.param_type}. {self.body})"

class Application(Expr):
    """Function application (e1 e2)."""
    def __init__(self, func: Expr, arg: Expr):
        self.func = func
        self.arg = arg

    def __repr__(self):
        return f"({self.func} {self.arg})"

class EffectfulExpr(Expr):
    """Expression that tracks an effect."""
    def __init__(self, effect: str, expr: Expr):
        self.effect = effect
        self.expr = expr

    def __repr__(self):
        return f"[{self.effect}] {self.expr}"

# === Inference Rules (Extended for Dependent, Linear, and Effect Types) ===
def type_infer(expr: Expr, context: Dict[str, Type]) -> Type:
    """
    Infers the type of an expression given a typing context.
    """
    if isinstance(expr, Var):
        if expr.name in context:
            return context[expr.name]
        else:
            raise TypeError(f"Unbound variable: {expr.name}")

    elif isinstance(expr, Lambda):
        new_context = context.copy()
        new_context[expr.param] = expr.param_type
        body_type = type_infer(expr.body, new_context)

        if isinstance(expr.param_type, LinearType):
            if expr.param not in expr.body.__repr__():  # Basic linear check
                raise TypeError(f"Linear variable {expr.param} must be used exactly once.")

        return Function(expr.param_type, body_type)

    elif isinstance(expr, Application):
        func_type = type_infer(expr.func, context)
        arg_type = type_infer(expr.arg, context)

        if isinstance(func_type, Function) and func_type.input_type == arg_type:
            return func_type.output_type
        else:
            raise TypeError(f"Type mismatch: {func_type} cannot be applied to {arg_type}")

    elif isinstance(expr, EffectfulExpr):
        base_type = type_infer(expr.expr, context)
        return EffectfulType(expr.effect, base_type)

    else:
        raise TypeError("Unknown expression type")

# === Testing the Extended Type System ===
if __name__ == "__main__":
    context = {}

    # Example 1: Identity function λx: Int. x
    id_func = Lambda("x", Int(), Var("x"))
    print(f"Expression: {id_func}")
    print(f"Type: {type_infer(id_func, context)}\n")  # Expected: (Int → Int)

    # Example 2: Linear Type - λx: Linear[Int]. x (must be used exactly once)
    linear_func = Lambda("x", LinearType(Int()), Var("x"))
    print(f"Expression: {linear_func}")
    print(f"Type: {type_infer(linear_func, context)}\n")  # Expected: (Linear[Int] → Int)

    # Example 3: Dependent Function - Π n: Int. Vector(n)
    dependent_func = DependentFunction("n", Int(), lambda n: f"Vector({n})")
    print(f"Dependent Function Type: {dependent_func}\n")  # Expected: (Π n: Int. Vector(n))

    # Example 4: Effectful Expression - IO tracked function
    io_expr = EffectfulExpr("IO", Var("x"))
    context["x"] = Int()
    print(f"Expression: {io_expr}")
    print(f"Type: {type_infer(io_expr, context)}\n")  # Expected: Effect[IO, Int]

    # Example 5: Function application (λx: Int. x) 42
    app = Application(id_func, Var("x"))
    context["x"] = Int()
    print(f"Expression: {app}")
    print(f"Type: {type_infer(app, context)}\n")  # Expected: Int

    # Example 6: Type Error (Linear variable not used)
    try:
        bad_linear = Lambda("x", LinearType(Int()), Var("y"))
        print(f"Expression: {bad_linear}")
        print(f"Type: {type_infer(bad_linear, context)}\n")  # Expected to fail
    except TypeError as e:
        print(f"Type Error: {e}")
