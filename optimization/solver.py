"""
This module contains the function for solving the optimization model using a specified solver.
Available solvers:
    - Gurobi
    - SCIP
"""

from pyomo.opt import SolverFactory

def execute(model, solver_name, time_limit):
    """
    Parameters: 
    ----------
    model: pyomo.environ.ConcreteModel
        The optimization model to be solved
    solver_name: str
        The name of the solver to be used. 
        Available solvers: "gurobi", "scip"
    time_limit: int
        The time limit (in seconds) for the optimization process before it terminates
    """
    # Initialize
    solver = SolverFactory(solver_name)
    if not solver.available():
        print(f"{solver_name} solver is not available!")
        return None
    else:
        print(f"Using {solver_name} to solve the model.")

        if solver_name == "gurobi":
            solver.options['Heuristics'] = 1.0
            solver.options['MIPFocus'] = 2
            solver.options['TimeLimit'] = time_limit
            solver.options['MIPGap'] = 0.00
        elif solver_name == "scip":
            solver.options['limits/time'] = time_limit
            # solver.options['cuts'] = 'strong'
            solver.options['presolving'] = 1
            solver.options['threads'] = 4
            solver.options['decomposition'] = 'block'
        elif solver_name == "appsi_highs":
            solver.options['time_limit'] = time_limit

        # Solve the model
        results = solver.solve(model, tee=True)
        
        return model