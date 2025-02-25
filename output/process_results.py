import output.generate_html as gh

def execute(results: dict):
    for objective, result in results.items():
        result.generate_station_results()
        result.print_results()
        result.build_station_time_graph()

    generate_html(results)

def get_table_data(results):
    table_data = {}

    for objective, result in results.items():
        table_data[objective] = {
            'number_of_stations': result.calculate_number_of_stations(),
            'total_number_of_stations': result.calculate_total_number_of_stations(),
            'cost_of_ownership': result.calculate_total_costs(),
            'fix_costs': result.calculate_fix_costs(),
            'labor_costs': result.calculate_labor_costs()
        }

    return table_data

def generate_html(results):
    gh.build(get_table_data(results), results)