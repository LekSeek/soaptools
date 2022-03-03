"""A setuptools based setup module.
See:
https://packaging.python.org/guides/distributing-packages-using-setuptools/
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

install_requires = (here / "requirements.txt").read_text().splitlines()

setup(
    name='SoapTools',  # Required
    version='0.1.0',  # Required
    description='Python soap tools',  # Optional

    # todo: fill README.md
    long_description=long_description,
    long_description_content_type='text/markdown',
    # url='https://github.com/pypa/sampleproject', todo fill url
    author="Maciej Kulesza",
    author_email='mck.kulesza@gmail.com',  # Optional

    # For a list of valid classifiers, see https://pypi.org/classifiers/
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='soap, tools, development, xsd, binding, wsdl',
    packages=find_packages(where="src"),  # Required
    package_dir={
        "": "src"
    },
    python_requires='>=3.9, <4',
    install_requires=install_requires,

    entry_points={  # Optional
        'console_scripts': [
            'sample=soaptools.__main__:main',
        ],
    },
)
