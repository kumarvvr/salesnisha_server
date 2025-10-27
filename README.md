# SalesNisha FastAPI Example

Minimal FastAPI project with routing and controllers.

Quick start (PowerShell):

```powershell
# Activate virtualenv (if present)
.\env\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --port 8000
```

Run tests:

```powershell
pytest -q
```

API endpoints
- GET /health -> health check
- GET /items/ -> list items
- POST /items/ -> create item
- GET /items/{item_id} -> get single item
