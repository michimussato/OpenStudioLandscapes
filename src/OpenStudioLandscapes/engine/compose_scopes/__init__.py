from OpenStudioLandscapes.engine.discovery import discovery

GRAFANA_AVAILABLE: bool = "OpenStudioLandscapes.Grafana" in discovery.DISCOVERED_MODELS.keys()
