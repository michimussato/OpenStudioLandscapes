class ComposeScopeException(Exception):
    """
    This Exception is raised when a compose_scope is unavailable.
    That means that a module might not be enabled in
    OpenStudioLandscapes.engine.constants.THIRD_PARTY
    """
    pass
