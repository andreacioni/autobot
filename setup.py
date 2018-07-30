import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="telegram-autobot",
    version="0.0.9",
    author="Andrea Cioni",
    author_email="cioni95@rocketmail.com",
    description="Build an interactive Telegram bot with some JSON files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andreacioni/autobot",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
