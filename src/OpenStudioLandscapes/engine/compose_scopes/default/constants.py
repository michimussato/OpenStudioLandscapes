import os

ATTACH_PANGOLIN_SITE_TO_COMPOSE_SCOPE = bool(
    int(
        os.environ.get(
            "OPENSTUDIOLANDSCAPES__ATTACH_PANGOLIN_SITE_TO_COMPOSE_SCOPE", 0
        )
    )
)

COMPOSE_SCOPE_GROUP_PREFIX = "ComposeScope"
