# Xero Global Prop Fetcher - DraftKings/FanDuel (Blueprint)
# This is the live scraper/API wrapper for:
# - Scanning all sports
# - Pulling all markets (moneylines, totals, spreads, player props, alt lines, novelty bets)
# - Supporting both DraftKings and FanDuel
# - Feeding props into the Jarvis Protocol optimizer

from fastapi import FastAPI
from pydantic import BaseModel
import requests
import os

app = FastAPI()

# Odds API key (set your own key in environment or directly here)
ODDS_API_KEY = os.getenv("ODDS_API_KEY", "c8062fba25bf5dc48dfad2a3d8245663")
ODDS_API_BASE = "https://api.the-odds-api.com/v4/sports"

class Prop(BaseModel):
    sport: str
    event: str
    market: str
    prop: str
    odds: float
    source: str

@app.get("/")
def root():
    return {"message": "Xero System is live!"}

@app.get("/xero/all-props-flip-scan")
def all_props_flip_scan():
    try:
        url = f"{ODDS_API_BASE}/?apiKey={ODDS_API_KEY}&all=true&regions=us&markets=all"
        response = requests.get(url)

        print("STATUS CODE:", response.status_code)
        print("RESPONSE TEXT:", response.text)

        if response.status_code != 200:
            return {"error": f"Odds API responded with status {response.status_code}"}

        data = response.json()
        results = []

        for item in data:
            sport = item.get("key", "unknown")
            home_team = item.get("home_team", "")
            away_team = item.get("away_team", "")
            event = f"{away_team} vs {home_team}" if away_team and home_team else item.get("title", "Unknown Matchup")

            for bookmaker in item.get("bookmakers", []):
                source = bookmaker.get("title", "unknown")
                for market in bookmaker.get("markets", []):
                    market_type = market.get("key", "unknown")
                    for outcome in market.get("outcomes", []):
                        results.append({
                            "sport": sport,
                            "event": event,
                            "market": market_type,
                            "prop": outcome.get("name", "unknown"),
                            "odds": outcome.get("price", 0),
                            "source": source
                        })

        return {"status": "Jarvis Protocol Raw Pull", "count": len(results), "props": results[:50]}

    except Exception as e:
        return {"error": str(e)}

