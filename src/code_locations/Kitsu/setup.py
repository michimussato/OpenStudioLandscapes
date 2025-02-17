from setuptools import find_packages, setup

setup(
    name="Kitsu",
    packages=find_packages(exclude=["Kitsu_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
