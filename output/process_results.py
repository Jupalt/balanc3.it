import matplotlib.pyplot as plt
import numpy as np
import generate_html
from matplotlib.patches import Patch
import matplotlib.lines as mlines

def write_results(model, task_time_dict):
    station_results = {}

    # Iterate over all stations
    for j in model.STATIONS:
        if model.z[j].value == 1:  # Station is open
            # Find the assigned station type
            station_type = None
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

            # Extract just the task IDs for output
            assigned_tasks = [task[0] for task in assigned_tasks]

            # Store the results for this station
            station_results[j] = {
                "station_type": station_type,
                "assigned_tasks": assigned_tasks,
            }

    # Print results
    count = 1
    for station_index, info in station_results.items():
        print(
            f"Station {count} with type {info['station_type']}: {info['assigned_tasks']}"
        ) 
        count += 1

    build_station_time_graph(station_results, task_time_dict)
    generate_html.build_html(station_results)

def build_station_time_graph(station_results, task_time_dict, product="E2", max_cycle_time=20, task_number=True):
    station_task_times = {}
    station_types = {}

    # Berechne die Zeiten für jede Station und ihre einzelnen Tasks
    for station, info in station_results.items():
        tasks = info["assigned_tasks"]
        station_type = info["station_type"]
        task_times = [task_time_dict[(t, product)] for t in tasks]
        station_task_times[station] = {"task_times": task_times, "tasks": tasks, "station_type": station_type}

    stations = list(range(1, len(station_task_times.keys()) + 1))
    fig, ax = plt.subplots(figsize=(10, 6))

    # Definiere Farben basierend auf Stationstypen
    station_type_colors = {
        "Robot": "#0E9682",  # Farbe für Roboterstationen
        "Manual": "#FF7F50",  # Farbe für manuelle Stationen
    }

    # Zeichne die Balken
    for station in stations:
        data = station_task_times[station]
        task_times = data["task_times"]
        tasks = data["tasks"]
        station_type = data["station_type"]
        bar_color = station_type_colors.get(station_type, "#D3D3D3")  # Standardfarbe, falls kein Typ gefunden

        bottom = 0  # Startwert für die gestapelten Balken
        for task_time, task in zip(task_times, tasks):
            # Zeichne jeden Task als Teil des Balkens
            ax.bar(station, task_time, bottom=bottom, color=bar_color, edgecolor='black', linewidth=1)
            
            if task_number:
                # Schreibe die Task-Nummer in die Mitte des Abschnitts
                middle = bottom + task_time / 2
                ax.text(station, middle, str(task), ha='center', va='center', fontsize=9, color='black', fontweight='bold')

            # Update den Startpunkt für den nächsten Task
            bottom += task_time

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

    plt.savefig("result_data/result_graph.png", dpi=300)