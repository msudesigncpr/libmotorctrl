from setuptools import find_packages, setup

setup(
    name="libmotorctrl",
    packages=find_packages(include=["libmotorctrl"]),
    version="0.2.0",
    description="Interface for the CMMO-ST drive controller 3-axis system",
    author="William Culhane",
    url="https://github.com/msudesigncpr/libmotorctrl",
    install_requires=["pymodbus>=3.6.3,<4.0.0"],
)
