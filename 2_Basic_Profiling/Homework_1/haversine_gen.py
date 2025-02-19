import json
import random
import string
import math
import statistics

def generate_haversine_data_json():
    data = []
    cluster_min_y = random.uniform(-90, -10)
    cluster_max_y = random.uniform(10, 90)
    cluster_min_x = random.uniform(-180, -10)
    cluster_max_x = random.uniform(10, 180)

    cluster_min_y0 = random.uniform(-90, -10)
    cluster_max_y0 = random.uniform(10, 90)
    cluster_min_x0 = random.uniform(-180, -10)
    cluster_max_x0 = random.uniform(10, 180)

    for i in range(1):
        x0 = random.uniform(cluster_min_x0, cluster_max_x0)
        y0 = random.uniform(cluster_min_y0, cluster_max_y0)
        x1 = random.uniform(cluster_min_x, cluster_max_x)
        y1 = random.uniform(cluster_min_y, cluster_max_y)
        data.append({'x0': x0,'y0': y0,'x1': x1,'y1': y1})

    with open('haversine.json', 'w') as f:
        json.dump(data, f)
    return data

def calculate_haversine_distances(data):
    """
    Given a list of dictionaries, each containing:
      - x0: longitude of the first point,
      - y0: latitude of the first point,
      - x1: longitude of the second point,
      - y1: latitude of the second point,
      
    compute the haversine distance for each pair.
    
    Parameters:
      data: list of dictionaries.
    
    Returns:
      List of distances (in kilometers). If a dictionary is missing keys or an error occurs,
      the corresponding entry in the list will be None.
    """
    distances = []
    for d in data:
        # Ensure the dictionary has all required keys.
        if all(k in d for k in ("x0", "y0", "x1", "y1")):
            try:
                # Adjust these assignments if your data uses a different ordering!
                lon1, lat1 = d["x0"], d["y0"]
                lon2, lat2 = d["x1"], d["y1"]
                distance = haversine_distance(lat1, lon1, lat2, lon2)
                distances.append(distance)
            except Exception as e:
                print("Error processing dictionary:", d, "\nError:", e)
                distances.append(None)
        else:
            print("Missing keys in dictionary:", d)
            distances.append(None)
    return distances

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on Earth 
    specified in decimal degrees using the haversine formula.
    
    Parameters:
      lat1, lon1: Latitude and Longitude of point 1.
      lat2, lon2: Latitude and Longitude of point 2.
      
    Returns:
      Distance in kilometers between the two points.
    """
    # Convert decimal degrees to radians.
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula.
    dlat = lat2 - lat1 
    dlon = lon2 - lon1 
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in kilometers. For miles, use 3956 instead.
    r = 6371  
    return c * r

data = generate_haversine_data_json()
print(statistics.mean(calculate_haversine_distances(data)))  # = 20.11111111111111
