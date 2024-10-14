from setuptools import setup, find_packages

setup(
    name="martech",
    version="0.1.0",
    description="A data processing and aggregation platform with user roles",
    author="Dima Moroz",
    author_email="d1m.moroz007@gmail.com",
    url="git@github.com:d1mmm/martech.git",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "fastapi",
        "uvicorn",
        "SQLAlchemy",
        "jinja2",
        "python-jose",
        "pytest",
        "pydantic",
        "aiofiles",
        "httpx",
    ],
    entry_points={
        'console_scripts': [
            'martech=app.main:app',
        ],
    },
    python_requires='>=3.9',
)
