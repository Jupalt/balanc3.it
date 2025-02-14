def print_results(model):
    station_results = {}

    # Iterate over all stations
    for j in model.STATIONS:
        for i in model.TASKS:
            for k in model.TYPES:
                for p in model.PARALLELS:
                    if model.x[i, j, k, p].value == 1:
                        if j not in station_results:
                            station_results[j] = {
                                "station_type": k,  # Setze den station_type
                                "assigned_tasks": [i],  # Initialisiere die Liste mit der aktuellen Aufgabe
                                "parallel_stations": p,  # Setze parallel_stations
                            }
                        else:
                            # Falls station_results[j] schon existiert, füge die Aufgabe hinzu
                            station_results[j]["assigned_tasks"].append(i)
    
    # Print results
    count = 1
    print("Result: ")
    for station_index, info in station_results.items():
        print(
            f"Station {count} with type {info['station_type']} and parallel station {info['parallel_stations']}: {info['assigned_tasks']}"
        ) 
        count += 1