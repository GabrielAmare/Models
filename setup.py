import setuptools
import pkg_resources

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = list(map(str, pkg_resources.parse_requirements(fh.read())))

setuptools.setup(
    name="models-gamare",
    version="1.0.10",
    author="Gabriel Amare",
    author_email="gabriel.amare.31@gmail.com",
    description="Package to help implement complex object structures within your project",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=requirements,
    url="https://github.com/GabrielAmare/Models",
    packages=['models', 'models.utils', 'models.errors', 'models.serializers'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
