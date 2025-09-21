# AI Task Planner

A lightweight AI-powered planning assistant that:
- Accepts a natural language goal
- Decomposes it into actionable steps
- Enriches steps with web search + weather data
- Outputs a clear day-by-day plan
- Saves each plan in a database (SQLite)
- Provides a simple web UI (new goal, view plan, browse history)

---

## How It Works

**Flow Diagram**

```
[ UI ] -> [ Flask Routes ] ->[ PlannerAgent ]
                         |                 |
                  [ Tavily Search ]     [ OpenWeather ]
                         |                 |
                           [ LLM (OpenAI) ]
                                   |
                           [ Plan JSON + MD ]
                                   |
                            [ SQLite Storage ]
```

---

## Setup Instructions

1. **Clone the repo**
   ```bash
   git clone https://github.com/Jayanth026/AI_Task_Planner.git
   cd ai-task-planner
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   - `.env`
   - Fill in your keys:
     - `OPENAI_API_KEY`
     - `TAVILY_API_KEY`
     - `OPENWEATHER_API_KEY`

4. **Run the app**
   ```bash
   python -m app.main
   ```
   Then open [http://127.0.0.1:5000](http://127.0.0.1:5000)

5. **Run in PyCharm or vscode**
   - Open folder in PyCharm or vscode
   - Add Python interpreter `.venv`
   - Run `app/main.py` with env vars loaded

---

## Example Goals & Outputs

### Example 1
**Goal:** “Plan a 2-day vegetarian food tour in Hyderabad.”

- **Day 1:** Breakfast at Chutneys -> Charminar street food -> Lunch at Paradise veg biryani -> Explore markets -> Dinner at Gokul Chat  
- **Day 2:** Breakfast at Sarvi -> Walk at KBR Park -> Lunch at Gharonda -> Hussain Sagar snacks -> Dinner at Chaat Bandaar  
- **Notes:** Expect light rain; carry umbrella  
- **Sources:** Clickable links to itineraries, TripAdvisor, Holidify, etc.

---

### Example 2
**Goal:** “Organise a 5-step daily study routine for learning Python.”

- Step 1: Focused reading + notes (60m)  
- Step 2: Hands-on coding practice (90m)  
- Step 3: Flashcards for syntax (30m)  
- Step 4: Mini-project iteration (45m)  
- Step 5: Reflection + backlog (15m)

---

## Tech Stack

- **Backend:** Flask (Python)  
- **AI:** OpenAI GPT (goal -> steps -> JSON plan)  
- **Tools:** Tavily Web Search API, OpenWeather API  
- **Database:** SQLite (via SQLAlchemy ORM)  
- **Frontend:** Flask + Jinja2 + Tailwind-inspired CSS

---

## Features

- Natural language -> structured multi-day plan  
- Weather-aware recommendations  
- Web-enriched itinerary steps  
- Clickable sources list  
- History of all past plans  

---

## AI Help

Frontend development: Built HTML templates and CSS for a clean, easy-to-use interface (new plan, view plan, history).
Error handling: Added clear error messages for API failures or unavailable sources, so the app stays user-friendly.
---

## Demo
Demo video showing entering a goal → getting a plan → viewing it later can be visiable in Demo_video.mp4 file

