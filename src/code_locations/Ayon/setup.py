from setuptools import find_packages, setup

setup(
    name="Ayon",
    packages=find_packages(exclude=["Ayon_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
