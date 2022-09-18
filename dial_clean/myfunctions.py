import numpy as np
def haversine(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    """
        Calculate the great circle distance between two points on the
        earth (specified in decimal degrees), returns the distance in
        meters.
        All arguments must be of equal length.
        :param lon1: longitude of first place
        :param lat1: latitude of first place
        :param lon2: longitude of second place
        :param lat2: latitude of second place
        :return: distance in meters between the two sets of coordinates
        """
    # Convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])
    # Haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km * 1000
