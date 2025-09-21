import os
import requests
from typing import List, Dict, Any, Optional


class WebSearchTool:
    """
    Tavily Search API
    Docs: https://docs.tavily.com/  (free tier available)
    Set env var: TAVILY_API_KEY
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")

    def search(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        if not self.api_key:
            return [{"title": "Search disabled", "url": "", "content": "TAVILY_API_KEY not set"}]
        payload = {
            "api_key": self.api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": False,
            "max_results": max_results
        }
        resp = requests.post("https://api.tavily.com/search", json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("results", [])


class WeatherTool:
    """
    OpenWeather Current + Forecast
    Docs: https://openweathermap.org/api
    Set env var: OPENWEATHER_API_KEY
    """
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")

    def current_weather(self, city: str, country_code: str = "", units: str = "metric") -> Dict[str, Any]:
        if not self.api_key:
            return {"status": "disabled", "message": "OPENWEATHER_API_KEY not set"}
        q = f"{city},{country_code}" if country_code else city
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {"q": q, "appid": self.api_key, "units": units}
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        return r.json()

    def daily_forecast(self, city: str, country_code: str = "", units: str = "metric", cnt: int = 5) -> Dict[str, Any]:
        """
        Uses 'forecast' (3h step) and compresses to daily high/low + conditions (simple).
        """
        if not self.api_key:
            return {"status": "disabled", "message": "OPENWEATHER_API_KEY not set"}
        q = f"{city},{country_code}" if country_code else city
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {"q": q, "appid": self.api_key, "units": units}
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        raw = r.json()

        # Compress by date
        from collections import defaultdict
        by_day = defaultdict(list)
        for it in raw.get("list", []):
            dt_txt = it["dt_txt"][:10]  # YYYY-MM-DD
            by_day[dt_txt].append(it)

        daily = []
        for day, items in list(by_day.items())[:cnt]:
            temps = [x["main"]["temp"] for x in items]
            descs = [x["weather"][0]["description"] for x in items if "weather" in x and x["weather"]]
            daily.append({
                "date": day,
                "temp_min": min(temps) if temps else None,
                "temp_max": max(temps) if temps else None,
                "summary": max(set(descs), key=descs.count) if descs else None
            })

        return {"city": raw.get("city", {}), "daily": daily}
