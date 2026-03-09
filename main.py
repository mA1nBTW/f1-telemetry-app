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

def get_h2h_telemetry(year, track, session_name, driver1, driver2):
    fastf1.Cache.enable_cache('cache_folder') 
    
    session = fastf1.get_session(year, track, session_name)
    session.load(telemetry=True, weather=False, messages=False) 
    
    lap_d1 = session.laps.pick_drivers(driver1).pick_fastest()
    lap_d2 = session.laps.pick_drivers(driver2).pick_fastest()
    
    tel_d1 = lap_d1.get_car_data().add_distance()
    tel_d2 = lap_d2.get_car_data().add_distance()
    
    return {
        driver1: {
            "distance": tel_d1['Distance'].tolist(),
            "speed": tel_d1['Speed'].tolist(),
            "throttle": tel_d1['Throttle'].tolist(),
            "brake": tel_d1['Brake'].tolist(),
            "gear": tel_d1['nGear'].tolist()
        },
        driver2: {
            "distance": tel_d2['Distance'].tolist(),
            "speed": tel_d2['Speed'].tolist(),
            "throttle": tel_d2['Throttle'].tolist(),
            "brake": tel_d2['Brake'].tolist(),
            "gear": tel_d2['nGear'].tolist()
        }
    }

# Creating route (API endpoint)
@app.get("/api/telemetry")
def get_telemetry(year: int, track: int, session: str, driver1: str, driver2: str):
    print(f"Пришел запрос: {year} {track} {session} | {driver1} vs {driver2}")
    # Return result. FastAPI creates JSON from it.
    return get_h2h_telemetry(year, track, session, driver1, driver2)