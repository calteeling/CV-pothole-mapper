import requests
import random
from datetime import datetime, timezone, timedelta

API_URL = "https://cv-pothole-mapper.onrender.com/api"

# Comprehensive Charlotte area coverage
charlotte_areas = [
    # West Charlotte / Beatties Ford Road
    (35.2445, -80.8712), (35.2398, -80.8698), (35.2467, -80.8734),
    (35.2512, -80.8745), (35.2389, -80.8721), (35.2478, -80.8698),
    # Thomasboro / Hoskins
    (35.2521, -80.8756), (35.2489, -80.8701), (35.2534, -80.8712),
    # North Tryon corridor
    (35.2634, -80.8423), (35.2589, -80.8401), (35.2612, -80.8445),
    (35.2698, -80.8378), (35.2756, -80.8356), (35.2812, -80.8334),
    # Enderly Park
    (35.2198, -80.8812), (35.2167, -80.8789), (35.2234, -80.8834),
    # Hidden Valley
    (35.2823, -80.8012), (35.2798, -80.7989), (35.2845, -80.8034),
    # Plaza Midwood
    (35.2156, -80.8123), (35.2134, -80.8098), (35.2178, -80.8145),
    # South End
    (35.2089, -80.8534), (35.2067, -80.8512), (35.2112, -80.8556),
    # NoDa
    (35.2456, -80.8234), (35.2434, -80.8212), (35.2478, -80.8256),
    # University City
    (35.3089, -80.7423), (35.3112, -80.7445), (35.3067, -80.7401),
    (35.3134, -80.7467), (35.3045, -80.7389),
    # Steele Creek
    (35.1734, -80.9234), (35.1712, -80.9212), (35.1756, -80.9256),
    # Ballantyne
    (35.0523, -80.8534), (35.0545, -80.8556), (35.0501, -80.8512),
    # Pineville
    (35.0834, -80.8923), (35.0812, -80.8901), (35.0856, -80.8945),
    # Matthews
    (35.1189, -80.7234), (35.1167, -80.7212), (35.1212, -80.7256),
    # Mint Hill
    (35.1823, -80.6534), (35.1801, -80.6512), (35.1845, -80.6556),
    # Cotswold
    (35.1934, -80.7934), (35.1912, -80.7912), (35.1956, -80.7956),
    # Eastland
    (35.2034, -80.7734), (35.2012, -80.7712), (35.2056, -80.7756),
    # Grier Heights
    (35.1934, -80.8134), (35.1912, -80.8112), (35.1956, -80.8156),
    # Optimist Park
    (35.2334, -80.8234), (35.2312, -80.8212), (35.2356, -80.8256),
    # Biddleville
    (35.2534, -80.8534), (35.2512, -80.8512), (35.2556, -80.8556),
    # Dilworth
    (35.2034, -80.8534), (35.2012, -80.8512), (35.2056, -80.8556),
    # Myers Park
    (35.1834, -80.8434), (35.1812, -80.8412), (35.1856, -80.8456),
    # Chantilly
    (35.2134, -80.8034), (35.2112, -80.8012), (35.2156, -80.8056),
    # Belmont
    (35.2234, -80.8034), (35.2212, -80.8012), (35.2256, -80.8056),
    # Wesley Heights
    (35.2334, -80.8634), (35.2312, -80.8612), (35.2356, -80.8656),
    # Ashley Park
    (35.2234, -80.8834), (35.2212, -80.8812), (35.2256, -80.8856),
    # Revolution Park
    (35.2134, -80.8734), (35.2112, -80.8712), (35.2156, -80.8756),
    # Seversville
    (35.2434, -80.8634), (35.2412, -80.8612), (35.2456, -80.8656),
    # Washington Heights
    (35.2634, -80.8534), (35.2612, -80.8512), (35.2656, -80.8556),
    # Lockwood
    (35.2534, -80.8334), (35.2512, -80.8312), (35.2556, -80.8356),
    # Oakhurst
    (35.1734, -80.7934), (35.1712, -80.7912), (35.1756, -80.7956),
    # Idlewild
    (35.1634, -80.7534), (35.1612, -80.7512), (35.1656, -80.7556),
    # Rama
    (35.1534, -80.7734), (35.1512, -80.7712), (35.1556, -80.7756),
]


def seed_potholes(count: int = 500):
    print(f"Seeding {count} potholes to {API_URL}...")
    success = 0

    for i in range(count):
        base_lat, base_lon = random.choice(charlotte_areas)
        lat = base_lat + random.uniform(-0.003, 0.003)
        lon = base_lon + random.uniform(-0.003, 0.003)

        confidence = round(random.uniform(0.40, 0.95), 3)

        days_ago = random.uniform(0, 30)
        timestamp = (datetime.now(timezone.utc) - timedelta(days=days_ago)).isoformat()

        response = requests.post(
            f"{API_URL}/potholes",
            json={
                "latitude": lat,
                "longitude": lon,
                "confidence": confidence,
                "timestamp": timestamp
            }
        )

        if response.status_code == 200:
            success += 1
            print(f"  [{i+1}/{count}] Logged pothole at ({lat:.4f}, {lon:.4f}) confidence={confidence}")
        else:
            print(f"  [{i+1}/{count}] Failed: {response.status_code}")

    print(f"\nDone — {success}/{count} potholes seeded successfully")


if __name__ == "__main__":
    seed_potholes(500)