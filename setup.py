from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="balance_integration",
    version="0.0.1",
    description="Integration between ERPNext and Balance Payment System",
    author="Selfmade Cloud Solutions",
    author_email="natnael.tilaye@earaldtradinget.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)