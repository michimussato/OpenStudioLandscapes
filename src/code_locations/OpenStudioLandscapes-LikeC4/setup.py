from setuptools import find_packages, setup

setup(
    name="OpenStudioLandscapes_LikeC4",
    packages=find_packages(exclude=["OpenStudioLandscapes_LikeC4_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
