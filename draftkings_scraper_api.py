
from fastapi import FastAPI
import requests
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()

HEADERS = {"User-Agent": "Mozilla/5.0"}

# DraftKings URLs
MASTER_EVENTGROUP_URL = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups?format=json"
EVENTGROUP_BASE_URL = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/{id}?format=json"
EVENTMARKET_BASE_URL = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/events/{event_id}?format=json"

@app.get("/hello")
def hello():
    return {"message": "Xero System is live!"}

@app.get("/props/all-sports")
def get_all_sports():
    try:
        master_res = requests.get(MASTER_EVENTGROUP_URL, headers=HEADERS)
        if master_res.status_code != 200:
            return JSONResponse(content={"error": f"DraftKings responded with status {master_res.status_code}"}, status_code=500)

        master_data = master_res.json()

        event_group = master_data.get("eventGroup", {})
        categories = event_group.get("offerCategories", [])
        if not categories:
            return JSONResponse(content={"error": "No offerCategories found in response"}, status_code=500)

        event_groups = categories[0].get("offerSubcategoryDescriptors", [])
        sports = {}

        for sport in event_groups:
            label = sport.get("name")
            group_id = sport.get("id")
            if label and group_id:
                sports[label.lower()] = group_id

        return {"sports": sports}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
