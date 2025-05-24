
from fastapi import FastAPI
import requests
from fastapi.responses import JSONResponse

app = FastAPI()

# The Odds API Key
API_KEY = "c8062fba25bf5dc48dfad2a3d8245663"
BASE_URL = "https://api.the-odds-api.com/v4"

@app.get("/hello")
def hello():
    return {"message": "Xero System is live with The Odds API!"}

@app.get("/props/all-sports")
def get_all_sports():
    try:
        url = f"{BASE_URL}/sports/?apiKey={API_KEY}"
        res = requests.get(url)
        if res.status_code != 200:
            return JSONResponse(content={"error": f"The Odds API responded with status {res.status_code}"}, status_code=500)

        sports = res.json()
        sport_map = {sport['title']: sport['key'] for sport in sports}

        return {"sports": sport_map}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/props/draftkings-odds")
def get_draftkings_odds():
    try:
        url = f"{BASE_URL}/sports/americanfootball_nfl/odds/?apiKey={API_KEY}&regions=us&markets=h2h,spreads,totals&bookmakers=draftkings"
        res = requests.get(url)
        if res.status_code != 200:
            return JSONResponse(content={"error": f"The Odds API responded with status {res.status_code}"}, status_code=500)

        odds_data = res.json()
        return {"odds": odds_data}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
