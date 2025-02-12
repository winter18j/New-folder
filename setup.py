from setuptools import setup, find_packages

setup(
    name="machine_monitoring",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "flask==3.0.2",
        "flask-cors==4.0.0",
        "google-generativeai==0.3.2",
        "python-dotenv==1.0.1",
    ],
    extras_require={
        'dev': [
            'pytest==8.0.2',
            'pytest-cov==4.1.0',
            'pytest-mock==3.12.0',
        ],
    },
    python_requires='>=3.7',
    description="Industrial machine monitoring system with AI-powered analysis",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/machine-monitoring",
) 