from setuptools import find_packages, setup

setup(
    name="OpenStudioLandscapes_Ayon",
    packages=find_packages(exclude=["OpenStudioLandscapes_Ayon_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
