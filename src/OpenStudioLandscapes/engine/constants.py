__all__ = [
    "DOCKER_USE_CACHE",
    "MONGODB_INSIDE_CONTAINER",
    "KITSUDB_INSIDE_CONTAINER",
    "BUILD_FROM_GOOGLE_DRIVE_10_2",
    "THIRD_PARTY",
]


DOCKER_USE_CACHE = False
MONGODB_INSIDE_CONTAINER = False
KITSUDB_INSIDE_CONTAINER = False
BUILD_FROM_GOOGLE_DRIVE_10_2 = False


THIRD_PARTY = [
    "OpenStudioLandscapes.Ayon.definitions",
    "OpenStudioLandscapes.Dagster.definitions",
    "OpenStudioLandscapes.Deadline_10_2.definitions",
    "OpenStudioLandscapes.filebrowser.definitions",
    "OpenStudioLandscapes.Grafana.definitions",
    "OpenStudioLandscapes.Kitsu.definitions",
    # "OpenStudioLandscapes.LikeC4.definitions",  # Errors atm; minor issue
]
