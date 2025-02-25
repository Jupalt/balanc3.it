import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Tuple
from optimization.model import AssemblyLineModel
from optimization import solver
import output.process_results as pr
from output.result import Result
import multiprocessing
import threading

app = FastAPI()

# Global Dict to save the input data
optimization_data: Dict[str, any] = {}

objectives = ["minimize_costs", "minimize_fix_costs", "minimize_stations", "maximize_automation"]
# objectives = ['minimize_costs']
results = None
optimization_status = {"status": "Optimization not started"}

def run_websocket():
    uvicorn.run(app, host="127.0.0.1", port=8001)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send status updates to the client
            await websocket.send_text(f"Status: {optimization_status['status']}")
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

class OptimizationRequest(BaseModel):
    max_time: int = 1000
    solver_name: str = "gurobi"

@app.post("/start-optimization/")
async def start_optimization(request: OptimizationRequest):
    global optimization_status

    print("Starting optimization...")
    # Start optimization in background
    run_optimization(request.max_time, request.solver_name)
    optimization_status["status"] = "Optimizing"

    return {"status": "Optimization finished"}

def run_optimization(max_time: int, solver_name: str):
    global optimization_status, results

    data = optimization_data

    processes = []
    with multiprocessing.Manager() as manager:
        shared_results = manager.dict()

        for objective in objectives:
            p = multiprocessing.Process(target=worker, args=(shared_results, objective, data, solver_name, max_time))
            processes.append(p)
            p.start()

        for p in processes:
            p.join()

        results = dict(shared_results)
        
    optimization_status["status"] = "Optimization completed"

def worker(results, objective, data, solver_name, max_time):
    results[objective] = optimization_process(objective, data, solver_name, max_time)

def optimization_process(objective, data, solver_name, max_time):
    print(f"Optimizing for objective: '{objective}'")
    alb_model = AssemblyLineModel(objective)
    model, task_time_dict = alb_model.prepare(data)
    solved_model = solver.execute(model, solver_name, max_time)
    print(f"Optimization for objective '{objective}' completed.")
    return Result(objective, solved_model, task_time_dict)

@app.get("/get-result/")
async def get_result():
    pass

@app.post("/process-results/")
async def process_results():
    pr.execute(results)
    return {"status": "HTML generated"}

@app.post("/generate-html/")
async def generate_html():
    pass

class TasksRequest(BaseModel):
    tasks: List

class CycleTimeRequest(BaseModel):
    cycle_time: int

class TaskTimesRequest(BaseModel):
    task_times: Dict[str, int]

class StationTypeCompRequest(BaseModel):
    station_type_compatibility: Dict[str, int]

class StationCostsRequest(BaseModel):
    station_costs: Dict[str, int]

class ProcessSpecificCostsRequest(BaseModel):
    process_specific_costs: Dict[str, int]

class TaskRelevanceRequest(BaseModel):
    task_relevance: Dict[int, int]

class SameStationPairsRequest(BaseModel):
    same_station_pairs: List[Tuple[int, int]]

def save_data(data_name: str, data: any):
    optimization_data[data_name] = data

def convert_dict_keys_to_tuples(json_dict):
    """Wandelt die Keys von 'x_y' Strings zurück in Tupel (x, y)."""
    return {
        (int(key.split("_")[0]), key.split("_")[1]): value
        for key, value in json_dict.items()
    }

@app.get("/")
async def read_root():
    return {"message": "Start uploading data before starting the optimization process"}

@app.post("/upload-tasks/")
async def upload_tasks(request: TasksRequest):
    save_data("tasks", request.tasks)
    return {"status": "List of tasks uploaded successfully"}

@app.post("/upload-cycle_time/")
async def upload_cycle_times(request: CycleTimeRequest):
    save_data("cycle_time", request.cycle_time)
    return {"status": "Cycle times uploaded successfully"}

@app.post("/upload-station_types/")
async def upload_station_types(station_types: List):
    save_data("station_types", station_types)
    return {"status": "Station types uploaded successfully"}

@app.post("/upload-task_times/")
async def upload_task_time(request: TaskTimesRequest):
    converted_data = convert_dict_keys_to_tuples(request.task_times)
    save_data("task_time_dict", converted_data)
    return {"status": "Task times uploaded successfully"}

@app.post("/upload-precedence_relations/")
async def upload_precedence_relations(precedence_relations: List):
    save_data("precedence_relations", precedence_relations)
    return {"status": "Precedence relations uploaded successfully"}

@app.post("/upload-incompatible_tasks/")
async def upload_incompatible_tasks(incompatible_tasks: List):
    save_data("incompatible_tasks", incompatible_tasks)
    return {"status": "Incompatible tasks uploaded successfully"}

@app.post("/upload-same_station_pairs/")
async def upload_same_station_pairs(request: SameStationPairsRequest):
    save_data("same_station_pairs", request.same_station_pairs)
    return {"status": "Same station pairs uploaded successfully"}

@app.post("/upload-station_type_compatibility/")
async def upload_station_type_compatibility(request: StationTypeCompRequest):
    converted_data = convert_dict_keys_to_tuples(request.station_type_compatibility)
    save_data("station_type_compatibility", converted_data)
    return {"status": "Station type compatibility uploaded successfully"}

@app.post("/upload-station_costs/")
async def upload_station_costs(request: StationCostsRequest):
    save_data("station_costs", request.station_costs)
    return {"status": "Station costs uploaded successfully"}

@app.post("/upload-process_specific_costs/")
async def upload_process_specific_costs(request: ProcessSpecificCostsRequest):
    converted_data = convert_dict_keys_to_tuples(request.process_specific_costs)
    save_data("process_specific_costs", converted_data)
    return {"status": "Process-specific costs uploaded successfully"}

@app.post("/upload-task_relevance/")
async def upload_task_relevance(request: TaskRelevanceRequest):
    save_data("task_relevance", request.task_relevance)
    return {"status": "Task relevance uploaded successfully"}

def start_server():
    print("Starting API server...")
    threading.Thread(target=run_websocket, daemon=True).start()
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)