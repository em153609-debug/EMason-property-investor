"""Safe geographic helpers. Coordinates are optional; no invented proximity."""
from math import radians, sin, cos, atan2, sqrt, isfinite


def coords(record):
    if not isinstance(record, dict):
        return None
    lat = record.get('latitude', record.get('lat'))
    lon = record.get('longitude', record.get('lon', record.get('lng')))
    try:
        lat, lon = float(lat), float(lon)
    except (TypeError, ValueError):
        return None
    if not all(map(isfinite, (lat, lon))) or not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return (lat, lon)


def miles_between(start, end):
    if start is None or end is None:
        return None
    lat1, lon1 = map(radians, start)
    lat2, lon2 = map(radians, end)
    a = sin((lat2 - lat1) / 2)**2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2)**2
    return 3958.7613 * 2 * atan2(sqrt(max(a, 0)), sqrt(max(0, 1 - a)))


def attach_distances(rows, subject_coordinates):
    result = []
    for row in rows:
        item = dict(row)
        if item.get('distance_miles') is None:
            comp_coord = coords(item)
            item['distance_miles'] = round(miles_between(subject_coordinates, comp_coord), 2) if subject_coordinates and comp_coord else None
        result.append(item)
    return result
