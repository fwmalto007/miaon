from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import List
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()

# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ここを必要に応じて適切なURLに設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket接続を保持するためのリスト
connections: List[WebSocket] = []

class TimeData(BaseModel):
    time: str

@app.post("/update_time")
async def update_time(data: TimeData):
    for connection in connections:
        await connection.send_text(data.time)
    return {"message": "Time updated"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received data from websocket: {data}")
    except WebSocketDisconnect:
        connections.remove(websocket)

@app.get("/")
async def get():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Real-Time Time Display</title>
        <script>
            let ws;
            function initWebSocket() {
                ws = new WebSocket("wss://miaon.onrender.com/ws");
                ws.onmessage = function(event) {
                    document.getElementById("timeDisplay").innerText = "Current Time: " + event.data;
                };
            }
            window.onload = initWebSocket;
        </script>
    </head>
    <body>
        <h1>Real-Time Time Display</h1>
        <div id="timeDisplay">Current Time: Not Available</div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
