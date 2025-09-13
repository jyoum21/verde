from setuptools import setup, find_packages

setup(
    name="verde-frontend",
    version="1.0.0",
    description="Frontend API for Verde - vegetarian recipe app for HackMIT 2025",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "python-multipart==0.0.6",
        "requests==2.31.0",
        "python-dotenv==1.0.0",
    ],
    python_requires=">=3.8",
)
