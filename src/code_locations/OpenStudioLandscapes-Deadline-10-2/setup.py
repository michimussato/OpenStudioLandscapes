from setuptools import find_packages, setup

setup(
    name="OpenStudioLandscapes_Deadline_10_2",
    packages=find_packages(exclude=["OpenStudioLandscapes_Deadline_10_2_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
