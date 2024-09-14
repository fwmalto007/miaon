import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS設定（クローム拡張からのリクエストを許可）
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 特定のドメインを許可したい場合はリストで指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# グローバル変数で再生時間を管理
current_time = "00:00:00"

@app.post("/update_time")
async def update_time(time: dict):
    global current_time
    current_time = time['time']
    return {"message": "Time updated"}

@app.get("/", response_class=HTMLResponse)
async def get_time():
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Real-time Video Time</title>
    </head>
    <body>
        <h1>Current Time: <span id="time"></span></h1>
        <script>
            const ws = new WebSocket('ws://localhost:8000/ws');
            ws.onmessage = function(event) {
                document.getElementById('time').textContent = event.data;
            };
        </script>
    </body>
    </html>
    """

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_text(current_time)
        await asyncio.sleep(1)
