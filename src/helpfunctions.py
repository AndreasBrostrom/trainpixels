
def get_track_path(track_path: list) -> list:
    """Extract only the LED positions from track path, excluding utils"""
    positions = []
    for step in track_path:
        if isinstance(step, list) and len(step) > 0:
            positions.append(step[0])
        else:
            positions.append(step)
    return positions


def count_track_utils(track_path: list) -> int:
    """Count the total number of utils that will be triggered in a track"""
    total_utils = 0
    for step in track_path:
        if isinstance(step, list) and len(step) > 1:
            # Second element contains utils list
            utils = step[1] if len(step) > 1 else []
            if isinstance(utils, list):
                total_utils += len(utils)
            elif utils:  # Single util (not a list)
                total_utils += 1
    return total_utils
