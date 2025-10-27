from fastapi import FastAPI
from datamanager import load_items_from_json
from rich import print

app = FastAPI(title="SalesNisha API")

items = load_items_from_json()
print(items)

@app.get("/health")
def health():
    return {"status": "ok"}

