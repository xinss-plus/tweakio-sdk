from setuptools import setup, find_packages

setup(
    name="tweakio-SDK",
    version="0.1.0",
    description="A powerful Multi-Platform automation SDK using Playwright and Camoufox. Currently supporting for whatsapp",
    author="Rohit",
    author_email="",  # Update with actual email if known, else leave blank or placeholder
    packages=find_packages(),
    py_modules=[
        "ChatLoader", 
        "MessageLoader", 
        "Extra", 
        "Storage", 
        "directory", 
        "Errors", 
        "Reply", 
        "Shared_Resources", 
        "login", 
        "selector_config", 
        "unread_handler", 
        "_Humanize", 
        "_Media"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Playwright",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
