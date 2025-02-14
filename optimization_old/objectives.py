# Minimizes the total number of stations
def minimize_stations(model):
    return sum(model.z[j] for j in model.STATIONS)

# Minimizes the total costs
def minimize_fix_costs(model):
    general_costs = sum(model.C[k] * model.l[j, k] for j in model.STATIONS for k in model.TYPES)

    # Prozessspezifische Kosten
    process_costs = sum(model.q[i, k] * model.x[i, j] * model.l[j, k]
                        for j in model.STATIONS 
                        for i in model.TASKS 
                        for k in model.TYPES)
    
    return general_costs + process_costs

# Maximizes the degree of automation while minimizing the number of stations
def maximize_automation(model):
    pass

def minimize_costs(model):
    labor_costs = sum(model.y[j, 'manual'] * model.labor_costs[j] for j in model.STATIONS)