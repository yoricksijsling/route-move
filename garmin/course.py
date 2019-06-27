import geopy.distance


def add_course_info(course, name, elevation_data):

    geopoints = elevation_tuples_to_geopoints(elevation_data)
    add_distances_to_geopoints(geopoints)
    elevations = list(p["elevation"] for p in geopoints)

    course["activityTypePk"] = 10
    course["boundingBox"] = calculate_bounding_box(geopoints)
    course["coordinateSystem"] = "WGS84"
    course["courseName"] = name
    course["distanceMeter"] = geopoints[-1]["distance"]
    course["elevationGainMeter"] = calculate_elevation_gain(elevations)
    course["elevationLossMeter"] = calculate_elevation_loss(elevations)
    course["geoPoints"] = geopoints
    course["rulePK"] = 2
    course["sourceTypeId"] = 3
    course["startPoint"] = pick_start_point(geopoints)


def geopoints_to_elevation_tuples(geopoints):
    """
    Convert the list of geopoints to tuples for an elevation data request.
    """
    return list([point["latitude"], point["longitude"], None] for point in geopoints)


def elevation_tuples_to_geopoints(r):
    """
    Convert a response from the elevation endpoint to a list of geopoints.
    """
    return list(
        {"distance": None, "elevation": elevation, "latitude": lat, "longitude": lon}
        for lat, lon, elevation in r
    )


def add_distances_to_geopoints(geopoints):
    """
    Calculate cumulative distances using the WGS-84 ellipsoid, and add them to
    the geopoints.
    """
    prev = None
    distance = 0  # meters
    for p in geopoints:
        cur = p["latitude"], p["longitude"]
        if prev:
            distance += geopy.distance.distance(prev, cur).m
        p["distance"] = distance
        prev = cur


def calculate_elevation_gain(elevations):
    """
    Based on the notifyNewPoint function of the elevation gain analyzer.
    See https://gist.github.com/yoricksijsling/8abe7237e9930255e2eeceb63089dc29#file-module_20-js
    and https://gist.github.com/yoricksijsling/8abe7237e9930255e2eeceb63089dc29#file-web-react_static_js_backbone_utils_elevationlossanalyzer-js
    """

    threshold = 25

    thresholdStartingPoint = elevations[0]
    gain = 0
    valueAgainstThreshold = 0

    for elevation in elevations:
        diff = elevation - thresholdStartingPoint
        valueAgainstThreshold += diff
        if abs(valueAgainstThreshold) >= threshold:
            if valueAgainstThreshold > 0:
                gain += diff
            valueAgainstThreshold = 0
            thresholdStartingPoint = elevation

    return gain


def calculate_elevation_loss(elevations):
    """
    Based on the notifyNewPoint function of the elevation loss analyzer.
    See https://gist.github.com/yoricksijsling/8abe7237e9930255e2eeceb63089dc29#file-module_20-js
    and https://gist.github.com/yoricksijsling/8abe7237e9930255e2eeceb63089dc29#file-web-react_static_js_backbone_utils_elevationlossanalyzer-js
    """

    threshold = 25

    thresholdStartingPoint = elevations[0]
    loss = 0
    valueAgainstThreshold = 0

    for elevation in elevations:
        diff = thresholdStartingPoint - elevation
        valueAgainstThreshold += diff
        if abs(valueAgainstThreshold) >= threshold:
            if valueAgainstThreshold > 0:
                loss += diff
            valueAgainstThreshold = 0
            thresholdStartingPoint = elevation

    return loss


def calculate_bounding_box(geopoints):
    lat_min = min(p["latitude"] for p in geopoints)
    lat_max = max(p["latitude"] for p in geopoints)
    lon_min = min(p["longitude"] for p in geopoints)
    lon_max = max(p["longitude"] for p in geopoints)

    return {
        "lowerLeft": {"latitude": lat_min, "longitude": lon_min},
        "lowerLeftLatIsSet": True,
        "lowerLeftLongIsSet": True,
        "upperRight": {"latitude": lat_max, "longitude": lon_max},
        "upperRightLatIsSet": True,
        "upperRightLongIsSet": True,
    }


def pick_start_point(geopoints):
    """
    Pick one point as the start point. Garmin chooses a different point from the
    list actually. I _think_ it is used as the starting point for the view of
    the map, because they pick one that is reasonably close to the center.
    """
    p = geopoints[0]
    return {
        "distance": p["distance"],
        "elevation": p["elevation"],
        "latitude": p["latitude"],
        "longitude": p["longitude"],
        "timestamp": None,
    }
