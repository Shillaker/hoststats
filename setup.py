import setuptools

PKG_NAME = "hoststats"
PKG_VERSION = "0.0.2"

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=PKG_NAME,
    version=PKG_VERSION,
    author="Simon Shillaker",
    author_email="foo@bar.com",
    description="Host stats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Shillaker/hoststats",
    packages=["hoststats"],
    python_requires=">=3.6",
    entry_points={"console_scripts": ["hoststats = hoststats.cli:main"]},
)
