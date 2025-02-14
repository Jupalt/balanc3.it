from fastapi import FastAPI, BackgroundTasks, WebSocket
import time
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

@app.get("/optimization-status/")
async def get_optimization_status():
    return optimization_status

# Route, die die Hintergrundaufgabe startet
@app.post("/start-optimization/")
async def start_optimization(background_tasks: BackgroundTasks):
    # Starte die Optimierung im Hintergrund
    background_tasks.add_task(run_optimization)
    return {"status": "Optimization started"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

def start_server():
    print("Starting API server...")
    uvicorn.run("api.test_main:app", host="127.0.0.1", port=8001)