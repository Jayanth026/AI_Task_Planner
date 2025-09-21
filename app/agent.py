import json
import os
from typing import Dict, Any, List

from app.schemas import GeneratedPlan, DayPlan
from app.tools import WebSearchTool, WeatherTool

# Use OpenAI (or compatible) SDK
from openai import OpenAI

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


SYSTEM_PROMPT = """You are a careful planning assistant.
You will:
1) Break a user's goal into ordered, actionable steps.
2) When the goal implies places or outdoor activities, incorporate city-level weather (if provided).
3) When the goal implies visiting places, enrich using any provided web search snippets.
4) Output a concise day-by-day plan. Keep it pragmatic and specific."""


class PlannerAgent:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.search = WebSearchTool()
        self.weather = WeatherTool()

    def _contextual_enrichment(self, goal: str) -> Dict[str, Any]:
        enrichment: Dict[str, Any] = {"search": [], "weather": {}}

        import re
        place = None
        m = re.search(r"\b(in|to|at)\s+([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+)*)", goal)
        if m:
            place = m.group(2)

        enrichment["search"] += self.search.search(goal, max_results=3)

        if any(k in goal.lower() for k in ["trip", "tour", "visit", "weekend", "itinerary"]):
            q = f"best places highlights {place}" if place else "best places highlights for the goal"
            enrichment["search"] += self.search.search(q, max_results=3)

        if place:
            try:
                enrichment["weather"]["forecast"] = self.weather.daily_forecast(place, cnt=4)
                enrichment["weather"]["current"] = self.weather.current_weather(place)
            except Exception as e:
                enrichment["weather"]["error"] = str(e)

        return enrichment

    def _llm_plan(self, goal: str, enrichment: Dict[str, Any]) -> GeneratedPlan:
        search_snippets = []
        for r in enrichment.get("search", []):
            snippet = f"- {r.get('title','')} | {r.get('url','')} | {r.get('content','')[:200]}"
            search_snippets.append(snippet)

        weather_summary = json.dumps(enrichment.get("weather", {}), ensure_ascii=False)[:2500]

        user_prompt = f"""Goal:
{goal}

Enrichment (search snippets):
{chr(10).join(search_snippets)}

Enrichment (weather JSON summary):
{weather_summary}

Task:
1) Produce a 2-5 day, day-by-day plan (use 'Day 1', 'Day 2', etc; for non-trip routines use 'Step 1..').
2) Each day/step: bullet actionable items (3-6 bullets).
3) Add short notes that reference weather or tips when relevant.
4) Return JSON with this structure ONLY:
{{
  "goal": "...",
  "days": [
    {{"day": "Day 1", "items": ["..."], "notes": ["..."]}},
    {{"day": "Day 2", "items": ["..."], "notes": ["..."]}}
  ],
  "metadata": {{
     "sources": ["url1","url2", "..."],
     "weather_used": true/false
  }}
}}
"""

        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )

        content = resp.choices[0].message.content.strip()
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            content = content.strip("` \n")
            content = content.replace("json\n", "").replace("JSON\n", "")
            data = json.loads(content)

        days = [DayPlan(**d) for d in data.get("days", [])]
        gp = GeneratedPlan(goal=data.get("goal", goal), days=days, metadata=data.get("metadata", {}))
        return gp

    def plan(self, goal: str) -> Dict[str, Any]:
        enrichment = self._contextual_enrichment(goal)
        gp = self._llm_plan(goal, enrichment)

        if "sources" not in gp.metadata or not gp.metadata["sources"]:
            gp.metadata["sources"] = [r.get("url", "") for r in enrichment.get("search", []) if r.get("url")]
        if "weather_used" not in gp.metadata:
            gp.metadata["weather_used"] = bool(enrichment.get("weather", {}).get("forecast"))

        md_lines = [f"# Plan for: {gp.goal}\n"]
        for d in gp.days:
            md_lines.append(f"## {d.day}")
            for it in d.items:
                md_lines.append(f"- {it}")
            if d.notes:
                md_lines.append(f"\n**Notes:**")
                for n in d.notes:
                    md_lines.append(f"- {n}")
            md_lines.append("")

        # ✅ FIXED: make sources clickable Markdown links
        if gp.metadata.get("sources"):
            md_lines.append("**Sources:**")
            for s in gp.metadata["sources"]:
                if s:
                    md_lines.append(f"- [{s}]({s})")

        plan_markdown = "\n".join(md_lines)

        return {
            "json": gp.model_dump(),
            "markdown": plan_markdown
        }
