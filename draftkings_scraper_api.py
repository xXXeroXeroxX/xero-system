
from fastapi import FastAPI
import requests
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()

# DraftKings URLs
MASTER_EVENTGROUP_URL = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups?format=json"
EVENTGROUP_BASE_URL = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/eventgroups/{id}?format=json"
EVENTMARKET_BASE_URL = "https://sportsbook.draftkings.com/sites/US-SB/api/v5/events/{event_id}?format=json"

@app.get("/props/all-sports")
def get_all_sports():
    try:
        master_res = requests.get(MASTER_EVENTGROUP_URL)
        master_data = master_res.json()

        event_groups = master_data.get("eventGroup", {}).get("offerCategories", [])[0].get("offerSubcategoryDescriptors", [])
        sports = {}

        for sport in event_groups:
            label = sport.get("name")
            group_id = sport.get("id")
            if label and group_id:
                sports[label.lower()] = group_id

        return {"sports": sports}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/props/all-today")
def get_all_today():
    try:
        master_res = requests.get(MASTER_EVENTGROUP_URL)
        master_data = master_res.json()
        today = datetime.utcnow().date().isoformat()
        all_sports_data = {}

        event_groups = master_data.get("eventGroup", {}).get("offerCategories", [])[0].get("offerSubcategoryDescriptors", [])

        for sport in event_groups:
            sport_name = sport.get("name")
            sport_id = sport.get("id")

            if not sport_id or not sport_name:
                continue

            url = EVENTGROUP_BASE_URL.format(id=sport_id)
            response = requests.get(url)
            data = response.json()

            games = []
            for event in data.get('eventGroup', {}).get('events', []):
                start_time = event.get("startDate")
                if start_time and today in start_time:
                    games.append({
                        "teams": f"{event.get('team1')} vs {event.get('team2')}",
                        "start_time": start_time,
                        "event_id": event.get("eventId")
                    })

            if games:
                all_sports_data[sport_name.lower()] = games

        return {"date": today, "sports": all_sports_data}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/markets/{event_id}")
def get_event_markets(event_id: str):
    try:
        url = EVENTMARKET_BASE_URL.format(event_id=event_id)
        response = requests.get(url)
        data = response.json()

        markets = []
        for category in data.get("event", {}).get("markets", []):
            market_data = {
                "market_name": category.get("marketType"),
                "outcomes": []
            }
            for outcome in category.get("outcomes", []):
                market_data["outcomes"].append({
                    "label": outcome.get("label"),
                    "odds": outcome.get("oddsAmerican")
                })
            markets.append(market_data)

        return {"event_id": event_id, "markets": markets}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/props/live-now")
def get_live_now():
    try:
        master_res = requests.get(MASTER_EVENTGROUP_URL)
        master_data = master_res.json()
        live_games = {}

        event_groups = master_data.get("eventGroup", {}).get("offerCategories", [])[0].get("offerSubcategoryDescriptors", [])

        for sport in event_groups:
            sport_name = sport.get("name")
            sport_id = sport.get("id")

            if not sport_id or not sport_name:
                continue

            url = EVENTGROUP_BASE_URL.format(id=sport_id)
            response = requests.get(url)
            data = response.json()

            live_events = []
            for event in data.get('eventGroup', {}).get('events', []):
                if event.get("liveStatus") == "LIVE":
                    live_events.append({
                        "teams": f"{event.get('team1')} vs {event.get('team2')}",
                        "start_time": event.get("startDate"),
                        "event_id": event.get("eventId")
                    })

            if live_events:
                live_games[sport_name.lower()] = live_events

        return {"live_games": live_games}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Run with: uvicorn draftkings_scraper_api:app --reload
