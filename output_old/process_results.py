import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import matplotlib.lines as mlines

def write_results(model, task_time_dict):
    station_results = {}

    # Iterate over all stations
    for j in model.STATIONS:
        if model.z[j].value == 1:  # Station is open
            # Find the assigned station type
            station_type = None
            number_parallel_stations = model.p[j].value
            for k in model.TYPES:
                if model.y[j, k].value == 1:  # Station type is assigned
                    station_type = k
                    break

            # Find the tasks assigned to this station and sort by task_order
            assigned_tasks = sorted(
                [
                    (i, model.task_order[i, j].value)
                    for i in model.TASKS
                    if model.x[i, j].value == 1
                ],
                key=lambda x: x[1]  # Sort by task_order
            )

            assigned_tasks = [task for task in assigned_tasks if model.r[task[0]] == 1]  # Filter out irrelevant tasks

            # Extract just the task IDs for output
            assigned_tasks = [task[0] for task in assigned_tasks]

            # Store the results for this station
            station_results[j] = {
                "station_type": station_type,
                "assigned_tasks": assigned_tasks,
                "parallel_stations": number_parallel_stations,
            }

    # Print results
    count = 1
    print("Result: ")
    for station_index, info in station_results.items():
        print(
            f"Station {count} with type {info['station_type']}: {info['assigned_tasks']}"
        ) 
        count += 1

    return build_station_time_graph(station_results, task_time_dict)
    # generate_html.build_html(station_results)

def build_station_time_graph(station_results, task_time_dict, product="E2", max_cycle_time=30, task_number=False):
    station_info = {}
    station_types = {}

    # Berechne die Zeiten für jede Station und ihre einzelnen Tasks
    station_count = 1
    for station, info in station_results.items():
        tasks = info["assigned_tasks"]
        station_type = info["station_type"]
        number_parallel_stations = info["parallel_stations"]
        task_times = [task_time_dict[(t, station_type)] for t in tasks]
        station_info[station_count] = {"task_times": task_times, "tasks": tasks, "station_type": station_type, "parallel_stations": number_parallel_stations}
        station_count += 1

    stations = list(range(1, len(station_info.keys()) + 1))
    fig, ax = plt.subplots(figsize=(10, 6))

    # Definiere Farben basierend auf Stationstypen
    station_type_colors = {
        "robot": "#0E9682",  # Farbe für Roboterstationen
        "manual": "#FF7F50",  # Farbe für manuelle Stationen
    }

    # Zeichne die Balken
    for station in stations:
        data = station_info[station]
        task_times = data["task_times"]
        tasks = data["tasks"]
        station_type = data["station_type"]
        number_parallel_stations = int(data["parallel_stations"])
        bar_color = station_type_colors.get(station_type, "#D3D3D3")  # Standardfarbe, falls kein Typ gefunden

        bottom = 0  # Startwert für die gestapelten Balken
        for task_time, task in zip(task_times, tasks):
            task_time /= ((number_parallel_stations+1) or 1)
            # Zeichne jeden Task als Teil des Balkens
            ax.bar(station, task_time, bottom=bottom, color=bar_color, edgecolor='black', linewidth=1)
            
            if task_number:
                # Schreibe die Task-Nummer in die Mitte des Abschnitts
                middle = bottom + task_time / 2
                ax.text(station, middle, str(task), ha='center', va='center', fontsize=9, color='black', fontweight='bold')

            # Update den Startpunkt für den nächsten Task
            bottom += task_time

        if number_parallel_stations > 0:
            for i in range(0, number_parallel_stations):
                line_position = station + (i/(number_parallel_stations+1))
                ax.vlines(line_position, 0, bottom, colors='black', linestyles='-', linewidth=2)

    # Horizontale Linie für die Maximalzeit
    ax.axhline(y=max_cycle_time, color='red', linestyle='--', label='Max Cycle Time')

    # Achsen und Titel
    ax.set_xticks(stations)
    ticks = np.arange(5, max_cycle_time + 10, 5)  # Erstelle Ticks alle 5 Sekunden
    ax.set_yticks(ticks)
    ax.set_xlabel('Station')
    ax.set_ylabel('Total Time (Seconds)')
    ax.set_title(f'Total Time per Station for Product {product}')
    
    # Erstelle eine benutzerdefinierte Legende
    legend_elements = [
        Patch(facecolor=color, edgecolor='black', label=station_type) 
        for station_type, color in station_type_colors.items()
    ]
    # Füge die Linie als separaten Eintrag hinzu
    max_cycle_time_line = mlines.Line2D([], [], color='red', linestyle='--', label='Max Cycle Time')
    ax.legend(handles=legend_elements + [max_cycle_time_line])

    result_graph_path = "result_graph.png"
    plt.savefig(result_graph_path, dpi=300)
    print()
    print(f"Saved result graph as '{result_graph_path}'")

    return result_graph_path