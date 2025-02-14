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
        
        model = ConcreteModel()

        objective = "minimize_stations"
        max_stations = 72

        model.TASKS = Set(initialize=tasks)
        model.STATIONS = Set(initialize=list(range(1, max_stations + 1))) # Initialize STATIONS with an upper bound
        model.TYPES = Set(initialize=station_types)
        model.PARALLELS = Set(initialize=list(range(1, 4))) # Maximum number of parallel stations
        model.PRODUCTS = Set(initialize=products)
        model.PrecedencePairs = Set(initialize=precedence_relations, within=model.TASKS * model.TASKS)
        model.IncompatiblePairs = Set(initialize=incompatible_tasks, within=model.TASKS * model.TASKS)
        model.SameStationPairs = Set(initialize=same_station_pairs, within=model.TASKS * model.TASKS)

        # Parameters
        model.T = Param(initialize=cycle_time) # Cycle time
        model.t = Param(model.TASKS, model.TYPES, initialize=task_time_dict) # Processing time of a task 
        model.F = Param(model.TASKS, model.TYPES, initialize=station_type_compatibility, within=Binary)
        model.C = Param(model.TYPES, initialize=station_costs) # Cost for opening a station
        model.q = Param(model.TASKS, model.TYPES, initialize=process_specific_costs) # Cost for processing a task on a station type
        model.M = Param(initialize=max_stations)
        model.labor_costs = Param(initialize=100000) # Labor costs

        # Decision Variables
        model.x = Var(model.TASKS, model.STATIONS, model.TYPES, model.PARALLELS, within=Binary)  # Task assignment
        model.y = Var(model.STATIONS, model.PARALLELS, within=Binary)  # Helper variable Parallel
        model.z = Var(model.STATIONS, model.TYPES, within=Binary)  # Station type assignment

        # Constraints
        model.task_assignment = Constraint(model.TASKS, rule=task_assignment_rule)
        model.station_type = Constraint(model.STATIONS, model.TYPES, rule=station_type_rule)
        model.station_type_helper = Constraint(model.STATIONS, rule=station_type_helper_rule)
        model.station_compatibility = Constraint(model.TASKS, model.STATIONS, model.TYPES, model.PARALLELS, rule=compatibility_rule)
        model.cycle_time = Constraint(model.STATIONS, rule=time_rule)
        model.consistent_parallelity = Constraint(model.STATIONS, model.PARALLELS, rule=consistent_parallelity_rule)
        model.parallel_helper = Constraint(model.STATIONS, rule=parallel_helper_rule)
        model.precedence_relations = Constraint(model.PrecedencePairs, rule=precedence_relations_rule)
        model.same_station_pairs_constraint = Constraint(model.SameStationPairs, model.STATIONS, rule=same_station_pairs_rule)

        # Objective
        if objective == "minimize_stations":
            model.v = Var(model.STATIONS, within=Binary)
            model.open_station = Constraint(model.STATIONS, rule=open_station)
            model.objective_function = Objective(rule=minimize_stations, sense=minimize)

        if objective == "minimize_fix_costs":
            model.w = Var(model.STATIONS, model.TYPES, model.PARALLELS, within=Binary)
            model.helper_open_station = Constraint(model.STATIONS, model.TYPES, model.PARALLELS, rule=helper_open_station)
            model.objective_function = Objective(rule=minimize_fix_costs, sense=minimize)

        if objective == "minimize_costs":
            model.w = Var(model.STATIONS, model.TYPES, model.PARALLELS, within=Binary)
            model.helper_open_station = Constraint(model.STATIONS, model.TYPES, model.PARALLELS, rule=helper_open_station)
            model.objective_function = Objective(rule=minimize_costs, sense=minimize)

        return model