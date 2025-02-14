from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
import time
import asyncio
import uvicorn

app = FastAPI()

optimization_status = {"status": "Optimization not started"}

# Eine lang laufende Aufgabe, die im Hintergrund läuft
def run_optimization():
    global optimization_status
    for i in range(100):
        print(f"Optimizing {i}...")
        optimization_status["status"] = f"Optimizing {i}..."
        time.sleep(0.1)
    optimization_status["status"] = "Optimization complete"
    print("Optimization complete!")

# Route für WebSocket-Verbindung
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Sende status updates an den Client
            await websocket.send_text(f"Status: {optimization_status['status']}")
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")

# Route, die die Hintergrundaufgabe startet
@app.post("/start-optimization/")
async def start_optimization(background_tasks: BackgroundTasks):
    # Starte die Optimierung im Hintergrund
    background_tasks.add_task(run_optimization)
    return {"status": "Optimization started"}

@app.get("/get-result/")
async def get_result():
    return {"result": "All Good"}

def start_server():
    print("Starting API server...")
    uvicorn.run("api.websocket:app", host="127.0.0.1", port=8001)
