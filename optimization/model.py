import logging
from pyomo.environ import *
from optimization.constraints import *
from optimization.objectives import *

class AssemblyLineModel:
    def __init__(self):
        logging.getLogger('pyomo').setLevel(logging.WARNING)
        self.model = None

    def prepare(self, data):
        tasks = data["tasks"]
        cycle_time = data["cycle_time"]
        station_costs = data["station_costs"]
        station_types = data.get("station_types", list(station_costs.keys()))
        task_time_dict = data["task_time_dict"] 
        task_relevance = data["task_relevance"]
        precedence_relations = data.get("precedence_relations", self.default_precedence_relations(tasks, task_relevance))
        incompatible_tasks = data.get("incompatible_tasks", [])
        same_station_pairs = data.get("same_station_pairs", [])
        station_type_compatibility = data["station_type_compatibility"]
        process_specific_costs = data["process_specific_costs"]

        products = ["Test"]

        print(precedence_relations)

        self.model = self.build_model(cycle_time, tasks, station_types, products, task_time_dict, precedence_relations,
                    incompatible_tasks, same_station_pairs, station_type_compatibility, station_costs, 
                    process_specific_costs, task_relevance)

        return self.model

    def default_precedence_relations(self, tasks, task_relevance):
        """
        Generates a default precedence relation for the given tasks. Tasks are ordered in a sequence.
        """
        relevant_tasks = [task for task in tasks if task_relevance.get(task, 0) == 1]
        
        # Generate precedence relations for consecutive tasks with relevance 1
        return [(relevant_tasks[i], relevant_tasks[i+1]) for i in range(len(relevant_tasks) - 1)]

    def build_model(self, cycle_time, tasks, station_types, products, task_time_dict, precedence_relations,
                    incompatible_tasks, same_station_pairs, station_type_compatibility, station_costs, 
                    process_specific_costs, task_relevance):
        """
        Parameters: 
        ----------
        cycle_time_dict : dict[str, int]
            A dictionary where:
            - The key is a String, representing one product of the assembly line
            - The value is the required cycle time for this product
        tasks : list[int]
            A list of tasks with their IDs.
        station_types : list[str]
            A list of Strings, each representing a different station type.
        products: list[str]
            A list of Strings, each representing one product of the assembly line
        task_time_dict: dict[tuple[int, str], int]
            A dictionary where:
            - The key is a tuple (task_ID, station_type)
            - The value is the processing time (in integer units) required for the task on the given station type
        precedence_relations: list[tuple[int, int]]:
            A list of tuples (g, h) where task g must precede task h
        incompatible_tasks: list[tuple[int, int]]
            A list of tuples (d, f) where tasks d and f cannot be assigned to the same station
        same_station_pairs: list[tuple[int, int]]
            A list of tuples (m, n) where tasks m and n must be assigned to the same station
        station_type_compatibility: dict[tuple[int, str], int]
            A dictionary where:
            - The key is a tuple (task_ID, station_type) indicating the task and station type combination
            - The value is 1 if the task is compatible with the station type, and 0 otherwise
        station_costs: dict[str, int]
            A dictionary where:
            - The key is a station type (string)
            - The value is the fixed cost (integer) of opening a station of that type
        process_specific_costs: dict[tuple[int, str], int]
            A dictionary where:
            - The key is a tuple (task_ID, station_type) indicating the task and station type combination
            - The value is the additional cost (integer) for processing the task on the given station type
        space_requirements: dict[int, int]
            A dictionary where:
            - The key is an int (task_ID)
            - The value is the space requirement (int) of the task
        task_relevance: dict[tuple[int, str], int]
            A dictionary where:
            - The key is a tuple (task_ID, product_ID) indicating the task and product combination
            - The value is the relevance (int) of the task for the given product
        """
        model = ConcreteModel() 

        # Define upper bound for number of stations
        max_stations = 72

        # Sets
        model.TASKS = Set(initialize=tasks)
        model.STATIONS = Set(initialize=list(range(1, max_stations + 1))) # Initialize STATIONS with an upper bound
        model.TYPES = Set(initialize=station_types)
        model.PRODUCTS = Set(initialize=products)
        model.PrecedencePairs = Set(initialize=precedence_relations, within=model.TASKS * model.TASKS)
        model.IncompatiblePairs = Set(initialize=incompatible_tasks, within=model.TASKS * model.TASKS)
        model.SameStationPairs = Set(initialize=same_station_pairs, within=model.TASKS * model.TASKS)

        # Parameters
        model.c = Param(initialize=cycle_time) # Cycle time
        model.t = Param(model.TASKS, model.TYPES, initialize=task_time_dict) # Processing time of a task 
        model.F = Param(model.TASKS, model.TYPES, initialize=station_type_compatibility, within=Binary)
        model.C = Param(model.TYPES, initialize=station_costs) # Cost for opening a station
        model.q = Param(model.TASKS, model.TYPES, initialize=process_specific_costs) # Cost for processing a task on a station type
        model.r = Param(model.TASKS, initialize=task_relevance, within=Binary) # Defines which tasks are relevant for a product

        # Decision Variables
        model.x = Var(model.TASKS, model.STATIONS, within=Binary)  # Task assignment
        model.z = Var(model.STATIONS, within=Binary)  # Station open/close
        model.y = Var(model.STATIONS, model.TYPES, within=Binary)  # Station type assignment
        model.p = Var(model.STATIONS, within=NonNegativeIntegers) # Number of parallel stations
        model.task_order = Var(model.TASKS, model.STATIONS, within=NonNegativeIntegers) # For precedence relations within stations
        model.l = Var(model.STATIONS, model.TYPES, within=NonNegativeIntegers)

        # Objective Function
        model.objective = Objective(rule=minimize_costs, sense=minimize)

        # Constraints
        model.task_assignment = Constraint(model.TASKS, rule=task_assignment_rule)
        model.open_station = Constraint(model.TASKS, model.STATIONS, rule=open_station_rule)
        model.cycle_time = Constraint(model.STATIONS, rule=cycle_time_constraint)
        model.precedence = Constraint(model.PrecedencePairs, rule=precedence_rule)
        model.station_type = Constraint(model.STATIONS, rule=station_type_rule)
        model.station_compatibility = Constraint(model.TASKS, model.STATIONS, rule=station_compatibility_rule)
        model.incompatible_tasks = Constraint(model.IncompatiblePairs, model.STATIONS, rule=incompatible_tasks_rule)
        model.same_station_tasks = Constraint(model.SameStationPairs, model.STATIONS, rule=same_station_tasks_rule)
        model.precedence_within_station = Constraint(model.PrecedencePairs, rule=precedence_within_station_rule)
        model.task_order_assignment = Constraint(model.TASKS, model.STATIONS, rule=task_order_assignment_rule)
        model.parallel_station_limit = Constraint(rule=parallel_station_limit_rule)
        model.linearity_constraint = Constraint(model.STATIONS, model.TYPES, rule=linearity_constraint)

        return model