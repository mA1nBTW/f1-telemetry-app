# F1 Telemetry H2H 🏎️

A web tool for head-to-head comparison of Formula 1 driver telemetry. Select any two drivers from any session across multiple seasons and circuits — and see exactly where the time is gained or lost.

---

## What it does

The app loads official F1 session data via the [FastF1](https://github.com/theOehrly/Fast-F1) library and visualizes the fastest laps of two selected drivers side by side. You can explore:

- **Speed trace** — km/h over the course of the lap
- **Throttle & brake** — application inputs throughout the lap
- **Gear shifts** — gear number by distance
- **Track map** — racing line colored by speed
- **Time delta** — cumulative gap between the two drivers at every point on track

---

## Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| F1 Data | FastF1 |
| Frontend | Vanilla JS, Plotly.js |
| Fonts | Barlow Condensed |

No framework, no build step — just a single `index.html` served by FastAPI.

---

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/your-username/f1-telemetry-h2h.git
cd f1-telemetry-h2h
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn fastf1 pandas
```

### 3. Run the server

```bash
uvicorn main:app --reload
```

Then open [http://localhost:8000](http://localhost:8000) in your browser.

> The first time you load a session, FastF1 will download and cache the data. Subsequent loads are instant.

---

## How to use

1. Select a **year** from the dropdown
2. Choose a **Grand Prix** from the calendar
3. Pick a **session** (FP1, FP2, FP3, Q, Sprint, Race)
4. Select **Driver 1** and **Driver 2**
5. Hit **Compare** — charts load automatically

---

## Project structure

```
f1-telemetry-h2h/
├── main.py        # FastAPI backend — data fetching & API endpoints
├── index.html     # Frontend — UI and chart rendering
└── cache_folder/  # Auto-created by FastF1 for local data cache
```

### API endpoints

| Endpoint | Params | Description |
|---|---|---|
| `GET /api/schedule` | `year` | Returns the race calendar for a given year |
| `GET /api/drivers` | `year`, `track`, `session` | Returns the driver list for a session |
| `GET /api/telemetry` | `year`, `track`, `session`, `driver1`, `driver2` | Returns full telemetry + time delta for two drivers |

---

## Notes

- Data availability depends on FastF1 — sessions from 2018 onward are generally well supported
- Telemetry is based on each driver's **personal fastest lap** in the selected session
- The time delta is computed using `fastf1.utils.delta_time`: positive values mean Driver 1 is ahead at that point on track
