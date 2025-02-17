from setuptools import find_packages, setup

setup(
    name="OpenStudioLandscapes_Grafana",
    packages=find_packages(exclude=["OpenStudioLandscapes_Grafana_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
