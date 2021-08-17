import setuptools

PKG_NAME = "hoststats"

with open("VERSION", "r") as fh:
    pkg_ver = fh.read().strip()

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name=PKG_NAME,
    version=pkg_ver,
    author="Simon Shillaker",
    author_email="foo@bar.com",
    description="Host stats",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Shillaker/hoststats",
    packages=["hoststats"],
    install_requires=[
        "click",
        "flask",
        "numpy",
        "pandas",
        "psutil",
        "requests",
    ],
    python_requires=">=3.6",
    entry_points={"console_scripts": ["hoststats = hoststats.cli:main"]},
)
