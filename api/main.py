import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, List, Tuple
from optimization.model import AssemblyLineModel
from optimization import solver
from output.process_results import write_results

app = FastAPI()

optimization_status = {"status": "Optimization not started"}
optimization_result = None
active_connections = []

# Global Dict to save the input data
optimization_data: Dict[str, any] = {}

class MessageRequest(BaseModel):
    message: str

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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Akzeptiere die WebSocket-Verbindung
    active_connections.append(websocket)  # Füge die Verbindung der Liste hinzu
    try:
        while True:
            data = await websocket.receive_text()  # Hier kann der Server Nachrichten empfangen
            if data == "ping":
                print("Received ping")
                await websocket.send_text("pong")
            print(f"Received data: {data}")
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)  # Entferne die Verbindung, wenn der Client trennt
        print("Client disconnected")

async def notify_clients(message="send_status", **kwargs):
    # Sende den aktuellen Status der Optimierung an alle verbundenen Clients
    if message=="send_status":
        for connection in active_connections:
            await connection.send_text(f"Current Status: {optimization_status.get('status', 'Unknown')}")
    elif message=="send_result_graph":
        for connection in active_connections:
            await connection.send_text(f"Optimization complete. Result Graph Path: {kwargs.get('result_graph_path', 'Unknown')}")

@app.post("/start-optimization/")
async def start_optimization():
    feedback = {"status": "Optimization started"}
    asyncio.create_task(run_optimization())  # Starte die Optimierung asynchron
    return feedback

async def run_optimization():
    global optimization_status, optimization_result

    # Simuliere den Optimierungsprozess
    data = optimization_data  # Optimierungsdaten, die du verwenden möchtest
    optimization_status["status"] = "Optimizing..."
    
    # Modell erstellen und optimieren
    result = await solve_optimization_model(data)
    optimization_status["status"] = "Optimization completed"
    print("Optimization complete.")
    print()
    result_graph_path = write_results(result, data["task_time_dict"])

    # Speichere das Ergebnis und setze den Status auf abgeschlossen
    await notify_clients()
    """
    except Exception as e:
        optimization_status["status"] = f"Error: {str(e)}"
        await notify_clients()
    """

# Optimierungsmodell lösen
async def solve_optimization_model(data):
    # Dein Optimierungsmodell
    alb_model = AssemblyLineModel()
    model = alb_model.prepare(data)
    solved_model = solver.execute(model, "gurobi", 1000)
    return solved_model

@app.get("/optimization-status/")
async def get_optimization_status():
    return optimization_status

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

@app.post("/check/")
async def upload_task_relevance(request: MessageRequest):
    print(request.message)
    return {"status": "Message succesfully received"}

def start_server():
    print("Starting API server...")
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)