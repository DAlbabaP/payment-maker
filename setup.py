from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="paymentmaker",
    version="1.0.0",
    author="Daniil Pohodnyak",
    author_email="dan@pohodnyak.ru",
    description="Автоматизация создания счетов и актов для транспортных услуг",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/daniilpohodnyak/paymentmaker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Accounting",
        "Topic :: Office/Business",
        "Natural Language :: Russian",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "paymentmaker=paymentmaker.app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "paymentmaker": ["resources/**/*"],
    },
)