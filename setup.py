import os
import sys
from setuptools import setup, find_packages

# prepend the directory containing this file to sys.path
path = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, path)

name = 'palette'
package = __import__(name)

setup(name=name,
      version=package.__version__,
      url=package.__url__,
      maintainer=package.__maintainer__,
      maintainer_email=package.__email__,
      install_requires = ['requests'],
      packages=find_packages()
)
