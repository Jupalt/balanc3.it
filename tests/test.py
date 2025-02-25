def build(results, table_data):
    html_output = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ALB Report</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            display: flex;
            flex-direction: column;
            align-items: center; /* Zentriert alles auf der Seite */
            padding-top: 40px;
            padding-bottom: 80px;
        }

        h1 {
            font-size: 48px;
            text-align: center;
            margin: 0;
        }

        .image-container {
            display: grid;
            grid-template-columns: repeat(2, 1fr); /* 2 Spalten */
            gap: 20px; /* Abstand zwischen den Bildern */
            width: 90%;
            margin-top: 20px; /* Abstand zum Titel */
        }

        .image-container img {
            width: 100%; /* Bilder füllen die Zellen des Grids */
            height: auto; /* Seitenverhältnis beibehalten */
            border-radius: 8px;
            box-shadow: 2px 2px 8px rgba(0, 0, 0, 0.1);
        }

        /* Styling für die Tabelle */
        table {
            width: 80%;
            margin-top: 40px;
            border-collapse: collapse;
            text-align: center;
            background-color: #fff;
            border-radius: 10px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }

        table, th, td {
            border: 1px solid #e0e0e0;
        }

        th, td {
            padding: 15px;
            font-size: 16px;
            color: #555;
        }

        th {
            background-color: #0E9682;
            color: white;
        }

        td {
            background-color: #f9f9f9;
        }

        /* Styling für die Buttons */
        .button-container {
            margin-top: 40px;
            text-align: center;
        }

        .objective-button {
            background-color: #fff;
            border: 2px solid #000;
            color: #000;
            padding: 10px 20px;
            font-size: 18px;
            font-weight: bold;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease, color 0.3s ease;
            margin: 10px;
        }

        .objective-button.selected {
            background-color: #0E9682;
            color: white;
        }

    </style>
</head>
<body>

    <h1>Assembly Line Balancing Report</h1>
    <div class="image-container">
        <img src="minimize_costs_result_graph.png" alt="Graph 1">
        <img src="minimize_fix_costs_result_graph.png" alt="Graph 2">
        <img src="minimize_stations_result_graph.png" alt="Graph 3">
        <img src="maximize_automation_result_graph.png" alt="Graph 4">
    </div>

    <table>
        <thead>
            <tr>
                <th>Objective</th>
                <th>Number of Stations</th>
                <th>Total Cost of Ownership</th>
                <th>Fixed Costs</th>
                <th>Labor Costs</th>
            </tr>
        </thead>
        <tbody>
    """
    for objective, data in table_data.items():
        html_output += f"""
        <tr>
            <td><b>{objective.replace('_', ' ').title()}</b></td>
            <td>{data['number_of_stations']}</td>
            <td>{data['cost_of_ownership']}¥</td>
            <td>{data['fix_costs']}¥</td>
            <td>{data['labor_costs']}¥</td>
        </tr>
        """
    html_output += """
        </tbody>
    </table>

    <!-- Buttons for selecting objectives -->
    <div class="button-container">
        <button class="objective-button selected" id="minimized-costs" onclick="selectObjective('minimized-costs')">Minimize Costs</button>
        <button class="objective-button" id="minimized-fixed-costs" onclick="selectObjective('minimized-fixed-costs')">Minimize Fixed Costs</button>
        <button class="objective-button" id="minimized-stations" onclick="selectObjective('minimized-stations')">Minimize Stations</button>
        <button class="objective-button" id="maximize-automation" onclick="selectObjective('maximize-automation')">Maximize Automation</button>
    </div>
        <script>
        function selectObjective(objectiveId) {
            // Alle Buttons zurücksetzen
            let buttons = document.querySelectorAll('.objective-button');
            buttons.forEach(button => {
                button.classList.remove('selected');
            });

            // Den angeklickten Button hervorheben
            let selectedButton = document.getElementById(objectiveId);
            selectedButton.classList.add('selected');
        }
    </script>
</body>
</html>
    """
    with open("report.html", "w") as file:
        file.write(html_output)


table_data = {
    "minimized_costs": {
        "number_of_stations": 5,
        "cost_of_ownership": 25000,
        "fix_costs": 12000,
        "labor_costs": 13000
    },
    "minimized_fixed_costs": {
        "number_of_stations": 4,
        "cost_of_ownership": 22000,
        "fix_costs": 8000,
        "labor_costs": 14000
    },
    "minimized_stations": {
        "number_of_stations": 6,
        "cost_of_ownership": 26000,
        "fix_costs": 15000,
        "labor_costs": 11000
    },
    "maximize_automation": {
        "number_of_stations": 3,
        "cost_of_ownership": 23000,
        "fix_costs": 10000,
        "labor_costs": 13000
    }
}

build(table_data)