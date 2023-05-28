from setuptools import setup

#with open("README.md", "r") as f:
#    long_description = f.read()

setup(
    name="hotspot-detection",
    version="1.0",
    description="create the hotspot-ratio of a given set of hotspot-analysis results",
    license="MIT",
    author="Technical University of Darmstadt, Department of Computer Science, Laboratory for Parallel Programming",
    author_email="discopop@lists.parallel.informatik.tu-darmstadt.de",
    url="https://www.discopop.tu-darmstadt.de/",
    packages=["hotspot_detection"],
    install_requires=[],
    python_requires=">=3.6",
    entry_points={"console_scripts": ["hotspot_detection=hotspot_detection.__main__:main"]},
    include_package_data=True,
)
