from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import fastf1

# Creating web-app
app = FastAPI()

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
        # Searching for the fastest lap
        fastest_lap = session.laps.pick_drivers(driver_code).pick_fastest()
        
        # Trynna get the telemetry
        tel = fastest_lap.get_car_data().add_distance()
        
        return {
            "lap_time": format_lap_time(fastest_lap['LapTime']),
            "distance": tel['Distance'].tolist(),
            "speed": tel['Speed'].tolist(),
            "throttle": tel['Throttle'].tolist(),
            "brake": tel['Brake'].tolist(),
            "gear": tel['nGear'].tolist()
        }
    except Exception as e:
        return {"error": f"Пилот {driver_code} не проехал ни одного быстрого круга."}

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
    
    return {
        driver1: get_driver_data(session, driver1),
        driver2: get_driver_data(session, driver2)
    }

# Creating route (API endpoint)
@app.get("/api/telemetry")
def get_telemetry(year: int, track: int, session: str, driver1: str, driver2: str):
    print(f"Пришел запрос: {year} {track} {session} | {driver1} vs {driver2}")
    # Return result. FastAPI creates JSON from it.
    return get_h2h_telemetry(year, track, session, driver1, driver2)