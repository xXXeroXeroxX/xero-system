
from fastapi import FastAPI
import requests
from fastapi.responses import JSONResponse
from datetime import datetime

app = FastAPI()

API_KEY = "c8062fba25bf5dc48dfad2a3d8245663"
BASE_URL = "https://api.the-odds-api.com/v4"

@app.get("/hello")
def hello():
    return {"message": "Xero System final protocol live — ready for DK + FD parlay flips."}

@app.get("/xero/parlay-flip-report")
def parlay_flip_report():
    try:
        sports_url = f"{BASE_URL}/sports/?apiKey={API_KEY}"
        sports_res = requests.get(sports_url)
        sports = sports_res.json()

        today = datetime.utcnow().date().isoformat()
        flip_summary = {"step_1": [], "mid_stack": [], "ladder": []}

        for sport in sports:
            sport_key = sport.get("key")
            if not sport_key:
                continue

            odds_url = f"{BASE_URL}/sports/{sport_key}/odds/?apiKey={API_KEY}&regions=us&markets=h2h,spreads,totals&bookmakers=draftkings"
            odds_res = requests.get(odds_url)
            if odds_res.status_code != 200:
                continue

            games = odds_res.json()

            for game in games:
                commence = game.get("commence_time", "")
                if not commence.startswith(today):
                    continue

                for bookmaker in game.get("bookmakers", []):
                    if bookmaker.get("key") != "draftkings":
                        continue

                    for market in bookmaker.get("markets", []):
                        market_type = market.get("key")
                        outcomes = market.get("outcomes", [])

                        if len(outcomes) < 2:
                            continue

                        label = game.get("home_team", "Game") + " vs " + game.get("away_team", "")
                        leg_data = {
                            "match": label,
                            "type": market_type,
                            "odds": [(o["name"], o["price"]) for o in outcomes]
                        }

                        if market_type == "totals":
                            flip_summary["step_1"].append(leg_data)
                        elif market_type == "spreads":
                            flip_summary["mid_stack"].append(leg_data)
                        elif market_type == "h2h":
                            flip_summary["ladder"].append(leg_data)

        return {
            "status": "Jarvis Protocol Flip Report Ready",
            "date": today,
            "step_1_flips": flip_summary["step_1"][:5],
            "mid_stack_flips": flip_summary["mid_stack"][:5],
            "ladder_setups": flip_summary["ladder"][:5]
        }

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
