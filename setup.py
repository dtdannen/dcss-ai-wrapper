import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dcss-ai-wrapper", # Replace with your own username
    version="0.0.8",
    author="Dustin Dannenhauer",
    author_email="dannenhauerdustin@gmail.com",
    description="API for Dungeon Crawl Stone Soup for Artificial Intelligence research.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dtdannen/dcss-ai-wrapper",
    project_urls={
        "Bug Tracker": "https://github.com/dtdannen/dcss-ai-wrapper/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=[
        "autobahn",
        "nested-lookup",
        "websockets",
    ],
)