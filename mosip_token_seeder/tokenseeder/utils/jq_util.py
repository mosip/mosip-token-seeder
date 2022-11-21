import pyjq

class JqUtils:
    def __init__(self):
        pass

    def eval_single_expr_throws_exception(self, expr, data : dict):
        return pyjq.first(expr,data)

    def eval_single_expr(self, expr, data : dict):
        try:
            return self.eval_single_expr_throws_exception(expr, data)
        except:
            return None
