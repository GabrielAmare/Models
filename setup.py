import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="models-gamare",
    version="1.0.0",
    author="Gabriel Amare",
    author_email="gabriel.amare.31@gmail.com",
    description="Package to help implement complex object structures within your project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GabrielAmare/Beans",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
