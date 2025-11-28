from dagster import (
    Backoff,
    Jitter,
    RetryPolicy,
)

build_docker_image_retry_policy = RetryPolicy(
    # I've seen it many times that (mostly push) operations
    # fail due to temporary network issues. Mostly because
    # DNS resolution fails. Is Pihole the bottleneck here?
    # Can we make it become more responsive?
    # Investigate:
    # - tail --follow=name -n +63 /var/log/pihole/FTL.log
    # - /usr/bin/pihole-FTL no-daemon
    max_retries=3,
    delay=0.2,  # 200ms
    backoff=Backoff.EXPONENTIAL,
    jitter=Jitter.PLUS_MINUS,
)
