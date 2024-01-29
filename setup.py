from setuptools import setup

with open("README.md", "r") as readme_file:
    long_description = readme_file.read()

exec(open("tree_utils/__init__.py").read())

setup(
    name='recurse-tree-process',
    version=__version__,
    include_package_data=True,
    python_requires='>=3',
    description='A functional util for generic recursive tree processing',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Markus Peitl",
    author_email='office@markuspeitl.com',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries"

    ],
    install_requires=[],
    entry_points={},
    packages=['tree_utils']
)
