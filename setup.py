import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AirzoneCloudDaikin",
    version="0.1.0",
    author="max13fr",
    author_email="max13fr@yozo.fr",
    description="Python3 library for Daikin (DKN) Airzone Cloud API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/max13fr/AirzoneCloudDaikin",
    keywords=["airzone", "airzonecloud", "daikin", "DKN", "api"],
    packages=["AirzoneCloudDaikin"],
    install_requires=["requests"],
    classifiers=[
        "Development Status :: 3 - Alpha",  # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.5",
)