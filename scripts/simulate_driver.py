import asyncio
import websockets
import json
import random
import sys
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# School coordinates (center point)
SCHOOL_LAT = 10.0482921
SCHOOL_LNG = 76.328898

# Maximum distance from school (in degrees, roughly 5km)
MAX_DISTANCE = 0.05

async def simulate_driver_movement(driver_id):
    """Simulate driver movement and send location updates via WebSocket."""
    uri = f"ws://localhost:8000/ws/driver/{driver_id}/"
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                logging.info("Connected to WebSocket server")
                
                while True:
                    # Generate random location near school
                    lat = SCHOOL_LAT + (random.random() - 0.5) * MAX_DISTANCE
                    lng = SCHOOL_LNG + (random.random() - 0.5) * MAX_DISTANCE
                    
                    # Create location update
                    location_data = {
                        "latitude": round(lat, 6),
                        "longitude": round(lng, 6),
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    # Send update
                    await websocket.send(json.dumps(location_data))
                    logging.info(f"Sent location update: {location_data}")
                    
                    # Wait 10 seconds before next update
                    await asyncio.sleep(10)
                    
        except websockets.exceptions.ConnectionClosed:
            logging.error("Connection closed, attempting to reconnect...")
            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"Error: {str(e)}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python simulate_driver.py <driver_id>")
        sys.exit(1)
    
    driver_id = sys.argv[1]
    logging.info(f"Starting location simulation for driver {driver_id}")
    
    try:
        asyncio.run(simulate_driver_movement(driver_id))
    except KeyboardInterrupt:
        logging.info("Simulation stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)
