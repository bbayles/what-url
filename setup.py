from setuptools import Distribution, setup

class ExtensionDistribution(Distribution):
    def has_ext_modules(*args, **kwargs):
        return True

setup(distclass=ExtensionDistribution)
