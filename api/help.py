import asyncio
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Dict, List, Tuple
from optimization_old.model import AssemblyLineModel
from optimization_old import solver
from output.process_results import write_results

app = FastAPI()

optimization_status = {"status": "Optimization not started"}
optimization_result = None

active_connections: List[WebSocket] = []

@app.post("/start-optimization/")
async def start_optimization():
    feedback = {"status": "Optimization started"}
    asyncio.create_task(run_optimization())  # Startet die Optimierung asynchron
    asyncio.create_task(ping_clients())  # Stellt sicher, dass während der Optimierung Pings gesendet werden
    return feedback

async def ping_clients():
    """Sendet alle 30 Sekunden einen Ping an alle verbundenen Clients um Verbindung aufrecht zu halten."""
    while True:
        for connection in active_connections:
            try:
                await connection.send_text("ping")  # Sende ein Ping
            except Exception as e:
                print(f"Fehler beim Senden des Pings: {e}")
        await asyncio.sleep(30)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()  # Akzeptiere die WebSocket-Verbindung
    active_connections.append(websocket)  # Füge die Verbindung der Liste hinzu
    try:
        while True:
            data = await websocket.receive_text()  # Server Nachrichten empfangen
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

async def run_optimization():
    global optimization_status, optimization_result

    # Simuliere den Optimierungsprozess
    data = optimization_data
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
    alb_model = AssemblyLineModel()
    model = alb_model.prepare(data)
    solved_model = solver.execute(model, "gurobi", 1000)
    return solved_model

@app.get("/optimization-status/")
async def get_optimization_status():
    return optimization_status

def start_server():
    print("Starting API server...")
    uvicorn.run("api.main:app", host="127.0.0.1", port=8000)