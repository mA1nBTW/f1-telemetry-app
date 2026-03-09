import fastf1

def get_h2h_telemetry(year, track, session_name, driver1, driver2):
    fastf1.Cache.enable_cache('cache_folder') 
    
    print(f"Загружаю сессию: {year} {track} {session_name}...")
    # Optimization: weather and race director turned off
    session = fastf1.get_session(year, track, session_name)
    session.load(telemetry=True, weather=False, messages=False) 
    
    # Fastest laps
    lap_d1 = session.laps.pick_drivers(driver1).pick_fastest()
    lap_d2 = session.laps.pick_drivers(driver2).pick_fastest()
    
    # Getting the telemetry
    tel_d1 = lap_d1.get_car_data().add_distance()
    tel_d2 = lap_d2.get_car_data().add_distance()
    
    # Packing into dictionary (future JSON)
    # Method .tolist() setting Pandas table to python-list
    data = {
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
    
    return data

# Test
if __name__ == "__main__":
    # LEC vs RUS
    result = get_h2h_telemetry(2026, 1, 'Q', 'ANT', 'RUS')
    
    print("\n--- DATA IS HERE ---")
    print(f"Количество точек телеметрии у ANT: {len(result['ANT']['distance'])}")
    print(f"Первые 5 значений скорости ANT: {result['ANT']['speed'][:5]}")
    print(f"Первые 5 значений скорости RUS: {result['RUS']['speed'][:5]}")