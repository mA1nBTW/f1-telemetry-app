from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import fastf1
import pandas as pd
import os

# Creating web-app
app = FastAPI()

os.makedirs('cache_folder', exist_ok=True)

# Allowing cross adress gets
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_driver_data(session, driver_code):
    try:
        fastest_lap = session.laps.pick_drivers(driver_code).pick_fastest()
        
        tel = fastest_lap.get_telemetry()

        result = {
            "lap_time":  format_lap_time(fastest_lap['LapTime']),
            "distance":  tel['Distance'].tolist(),
            "speed":     tel['Speed'].tolist(),
            "throttle":  tel['Throttle'].tolist(),
            "brake":     tel['Brake'].tolist(),
            "gear":      tel['nGear'].tolist(),
            "x":         tel['X'].tolist(),
            "y":         tel['Y'].tolist()
        }

        return result

    except Exception as e:
        print(f"[ERROR] get_driver_data({driver_code}): {e}")
        return {"error": f"Driver {driver_code} did not drive a single lap."}

def format_lap_time(lap_time_timedelta):
    if str(lap_time_timedelta) == "NaT": # If there is no time
        return "No time"
    
    # Seconds
    total_seconds = lap_time_timedelta.total_seconds()
    minutes = int(total_seconds // 60)
    seconds = total_seconds % 60
    
    # Formatting
    return f"{minutes}:{seconds:06.3f}"

def get_h2h_telemetry(year, track, session_name, driver1, driver2):
    fastf1.Cache.enable_cache('cache_folder') 
    
    session = fastf1.get_session(year, track, session_name)
    session.load(telemetry=True, weather=False, messages=False) 
    
    result = {
        driver1: get_driver_data(session, driver1),
        driver2: get_driver_data(session, driver2)
    }

    # Compute time delta between the two fastest laps
    try:
        lap_d1 = session.laps.pick_drivers(driver1).pick_fastest()
        lap_d2 = session.laps.pick_drivers(driver2).pick_fastest()

        # delta_time > 0 means driver1 is ahead (gaining), < 0 means driver2 is gaining
        delta_time, ref_tel, _ = fastf1.utils.delta_time(lap_d1, lap_d2)

        result['delta'] = {
            'distance': ref_tel['Distance'].tolist(),
            'delta': delta_time.tolist()
        }
    except Exception as e:
        result['delta'] = {'error': str(e)}

    return result

import pandas as pd

@app.get("/api/drivers")
def get_drivers(year: int, track: int, session: str):
    fastf1.Cache.enable_cache('cache_folder')
    
    sess = fastf1.get_session(year, track, session)
    sess.load(telemetry=False, laps=False, weather=False, messages=False)
    
    result = []
    for _, row in sess.results.iterrows():
        color = f"#{row['TeamColor']}" if pd.notna(row['TeamColor']) and row['TeamColor'] else "#888888"
        
        result.append({
            "code": row['Abbreviation'],
            "name": row['FullName'],
            "color": color
        })
        
    return result

@app.get("/api/schedule")
def get_schedule(year: int):
    fastf1.Cache.enable_cache('cache_folder') 
    print(f"Запрашиваю календарь для {year} года...")
    schedule = fastf1.get_event_schedule(year)
    races = schedule[schedule['RoundNumber'] > 0]
    
    session_map = {
        'Practice 1': 'FP1',
        'Practice 2': 'FP2',
        'Practice 3': 'FP3',
        'Qualifying': 'Q',
        'Sprint Qualifying': 'SQ',
        'Sprint Shootout': 'SQ',
        'Sprint': 'S',
        'Race': 'R'
    }
    
    result = []
    for _, row in races.iterrows():
        sessions = []
        for i in range(1, 6):
            s_name = row.get(f'Session{i}')
            if pd.notna(s_name) and s_name:
                sessions.append({
                    "code": session_map.get(s_name, s_name), 
                    "name": s_name
                })
                
        result.append({
            "id": row['RoundNumber'],
            "name": f"{row['Country']} — {row['Location']}",
            "sessions": sessions
        })
        
    return result

# Creating route (API endpoint)
@app.get("/api/telemetry")
def get_telemetry(year: int, track: int, session: str, driver1: str, driver2: str):
    print(f"Пришел запрос: {year} {track} {session} | {driver1} vs {driver2}")
    # Return result. FastAPI creates JSON from it.
    return get_h2h_telemetry(year, track, session, driver1, driver2)

@app.get("/")
def serve_frontend():
    return FileResponse("index.html")