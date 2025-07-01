import setuptools
import os
import yaml  # This library is needed to parse YAML files


# Function to read pip requirements from environment.yml
def read_conda_pip_dependencies():
    """
    Reads the list of pip requirements from the 'pip:' section of environment.yml.
    Note: setuptools 'install_requires' is for pip-installable packages.
    Conda-specific packages will not be installed via setup.py.
    """
    try:
        with open('environment.yml', 'r', encoding='utf-8') as f:
            env_data = yaml.safe_load(f)

        dependencies = env_data.get('dependencies', [])
        pip_dependencies = []

        for dep in dependencies:
            if isinstance(dep, dict) and 'pip' in dep:
                # This block handles the 'pip:' section within environment.yml
                for pip_req in dep['pip']:
                    pip_dependencies.append(pip_req.strip())
                break  # Assuming only one 'pip:' section

        return pip_dependencies
    except FileNotFoundError:
        print("Warning: environment.yml not found. No pip dependencies will be installed via setup.py.")
        return []
    except yaml.YAMLError as e:
        print(f"Error parsing environment.yml: {e}. No pip dependencies will be installed.")
        return []


# Read the README.md for the long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define the package name
package_name = "MedScore"

setuptools.setup(
    name=package_name,
    version="0.1.0",  # Initial version, consider updating this in your project
    author="Heyuan Huang and Alexandra DeLucia",  # Extracted from GitHub profile
    author_email="hhuan134@jh.edu",  # Placeholder, replace with actual email if available
    description="A framework for factuality scoring in medical responses",  # From README.md
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Heyuan9/MedScore",
    packages=setuptools.find_packages(where='.', include=[f'{package_name}*']),
    # 'where' specifies the root directory of the packages
    # 'include' specifies which packages to include (e.g., 'MedScore' and its sub-packages)

    # Dynamically load pip requirements from environment.yml
    install_requires=read_conda_pip_dependencies(),

    # Include non-Python files (like data files)
    include_package_data=True,
    package_data={
        package_name: ['data/*.csv'],  # Include all .csv files in the MedScore/data directory
    },

    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Assuming MIT License based on LICENSE file
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",  # Adjust as your project matures
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Medical Science Apps",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.12",  # Specify minimum Python version
)
