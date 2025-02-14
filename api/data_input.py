import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, List, Tuple
from optimization_old.model import AssemblyLineModel
from optimization_old import solver
from output.process_results import write_results

app = FastAPI()

# Global Dict to save the input data
optimization_data: Dict[str, any] = {}

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