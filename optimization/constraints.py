"""
This module contains the definitions of the constraints applied to the optimization model.
Each function in this module represents a specific constraint. 
"""

# Task Assignment: Each task is assigned to exactly one station
def task_assignment_rule(model, i):
    return sum(model.x[i, j] for j in model.STATIONS) == 1

# Open Stations: Tasks can only be assigned to open stations
def open_station_rule(model, i, j):
    return model.x[i, j] <= model.z[j]

# The sum of task times at a station time must be less than the cycle time 
def cycle_time_constraint(model, j):
    return sum(model.t[i, k] * model.x[i, j] * model.r[i] * model.y[j, k]
                for i in model.TASKS
                for k in model.TYPES) <= model.c * model.z[j] * (1+model.p[j])

# Precedence relations
def precedence_rule(model, g, h):
    return sum(j * model.x[g, j] for j in model.STATIONS) <= sum(j * model.x[h, j] for j in model.STATIONS)

# Station Type Assignment: Each station has exactly one type
def station_type_rule(model, j):
    return sum(model.y[j, k] for k in model.TYPES) == model.z[j]

# Station Type Compatibility. A task can only be assigned to a station of a compatible type
def station_compatibility_rule(model, i, j):
    return model.x[i, j] <= sum(model.F[i, k] * model.y[j, k] for k in model.TYPES)

# Incompatible Tasks: Task d and f cant be assigned to the same station because they are incompatible
def incompatible_tasks_rule(model, d, f, j):
    return model.x[d, j] + model.x[f, j] <= 1

# Same Station Tasks: Task m and n must be assigned to the same station
def same_station_tasks_rule(model, m, n, j):
    return model.x[m, j] == model.x[n, j]

# Ensures that the precedence relations are satisfied within a station
def precedence_within_station_rule(model, g, h):
    return sum(model.x[g, j] * model.task_order[g, j] for j in model.STATIONS) \
        <= sum(model.x[h, j] * model.task_order[h, j] for j in model.STATIONS) - 1

# The order of task i at station j is meaningful only if task i is assigned to station j
def task_order_assignment_rule(model, i, j):
    return model.task_order[i, j] <= 100 * model.x[i, j]

# The total number of parallel stations must be smaller than total_parallel_stations
def parallel_station_limit_rule(model):
    return sum(model.p[j] for j in model.STATIONS) <= 2

# Ensures linearity of the objective function
def linearity_constraint(model, j, k):
    return model.l[j, k] == (model.y[j, k] * (1+model.p[j]))