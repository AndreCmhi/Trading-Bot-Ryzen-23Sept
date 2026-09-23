from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import json
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")
CONFIG_PATH = "config.json"

def get_conf():
    if not os.path.exists(CONFIG_PATH):
        return {"exchange": "binance", "symbol": "BTC/USDT", "timeframe": "15m", "api_key": "", "api_secret": "", "order_size": 10}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "config": get_conf()})

@app.get("/config")
async def config_page(request: Request):
    return templates.TemplateResponse("config.html", {"request": request, "config": get_conf()})

@app.post("/save")
async def save(exchange: str = Form(...), symbol: str = Form(...), api_key: str = Form(...), api_secret: str = Form(...)):
    conf = get_conf()
    conf.update({"exchange": exchange, "symbol": symbol, "api_key": api_key, "api_secret": api_secret})
    with open(CONFIG_PATH, "w") as f:
        json.dump(conf, f, indent=4)
    return RedirectResponse(url="/", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
