import requests
import random
from datetime import datetime, timezone, timedelta

API_URL = "https://cv-pothole-mapper.onrender.com/api"

# Major highways and interstates in Charlotte
charlotte_highways = [
    # I-77 North (from uptown to Huntersville)
    (35.2334, -80.8434), (35.2456, -80.8423), (35.2578, -80.8412),
    (35.2700, -80.8401), (35.2823, -80.8389), (35.2945, -80.8378),
    (35.3067, -80.8367), (35.3189, -80.8356), (35.3312, -80.8345),
    # I-77 South (from uptown to Pineville)
    (35.2112, -80.8445), (35.1989, -80.8456), (35.1867, -80.8467),
    (35.1745, -80.8478), (35.1623, -80.8489), (35.1501, -80.8501),
    (35.1378, -80.8512), (35.1256, -80.8523), (35.1134, -80.8534),
    # I-85 Northeast (from uptown toward Concord)
    (35.2434, -80.8134), (35.2556, -80.8012), (35.2678, -80.7889),
    (35.2801, -80.7767), (35.2923, -80.7645), (35.3045, -80.7523),
    (35.3167, -80.7401), (35.3289, -80.7278), (35.3412, -80.7156),
    # I-85 Southwest (from uptown toward Gastonia)
    (35.2112, -80.8634), (35.1989, -80.8756), (35.1867, -80.8878),
    (35.1745, -80.9001), (35.1623, -80.9123), (35.1501, -80.9245),
    (35.1378, -80.9367), (35.1256, -80.9489), (35.1134, -80.9612),
    # I-277 (inner loop around uptown)
    (35.2234, -80.8534), (35.2256, -80.8456), (35.2278, -80.8378),
    (35.2234, -80.8312), (35.2189, -80.8256), (35.2134, -80.8289),
    (35.2112, -80.8367), (35.2134, -80.8445), (35.2178, -80.8501),
    # US-74 (Independence Blvd East)
    (35.2134, -80.7934), (35.2112, -80.7756), (35.2089, -80.7578),
    (35.2067, -80.7401), (35.2045, -80.7223), (35.2023, -80.7045),
    (35.2001, -80.6867), (35.1978, -80.6689), (35.1956, -80.6512),
    # US-74 West (toward Gastonia)
    (35.2156, -80.8734), (35.2178, -80.8956), (35.2201, -80.9178),
    (35.2223, -80.9401), (35.2245, -80.9623), (35.2267, -80.9845),
    # NC-51 (Pineville-Matthews Road)
    (35.1134, -80.7734), (35.1156, -80.7912), (35.1178, -80.8089),
    (35.1201, -80.8267), (35.1223, -80.8445), (35.1245, -80.8623),
    # US-21 (Statesville Road North)
    (35.2734, -80.8534), (35.2856, -80.8523), (35.2978, -80.8512),
    (35.3101, -80.8501), (35.3223, -80.8489), (35.3345, -80.8478),
    # NC-16 (Providence Road South)
    (35.1734, -80.8234), (35.1612, -80.8212), (35.1489, -80.8189),
    (35.1367, -80.8167), (35.1245, -80.8145), (35.1123, -80.8123),
    # I-485 segments (additional highway coverage)
    (35.3434, -80.7934), (35.3367, -80.7534), (35.3234, -80.7134),
    (35.2934, -80.6734), (35.2434, -80.6434), (35.1934, -80.6634),
    (35.1434, -80.7134), (35.1034, -80.7934), (35.0834, -80.8734),
    (35.0934, -80.9534), (35.1234, -80.9934), (35.1734, -80.9934),
    (35.2234, -80.9934), (35.2734, -80.9734), (35.3134, -80.9334),
    (35.3434, -80.8934), (35.3534, -80.8434), (35.3434, -80.7934),
    # NC-24/27 (Albemarle Road)
    (35.2034, -80.7334), (35.2012, -80.7156), (35.1989, -80.6978),
    (35.1967, -80.6801), (35.1945, -80.6623), (35.1923, -80.6445),
    # Billy Graham Parkway
    (35.2134, -80.9034), (35.2001, -80.8934), (35.1867, -80.8834),
    (35.1734, -80.8734), (35.1601, -80.8634), (35.1467, -80.8534),
]


def seed_highways(count: int = 400):
    print(f"Seeding {count} potholes along Charlotte highways to {API_URL}...")
    success = 0

    for i in range(count):
        base_lat, base_lon = random.choice(charlotte_highways)
        lat = base_lat + random.uniform(-0.002, 0.002)
        lon = base_lon + random.uniform(-0.002, 0.002)

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

    print(f"\nDone — {success}/{count} highway potholes seeded successfully")


if __name__ == "__main__":
    seed_highways(400)