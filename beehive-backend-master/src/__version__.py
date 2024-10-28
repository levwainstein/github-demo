from packaging import version


__title__ = 'beehive_backend'
__version__ = '1.0.0'

_parsed = version.parse(__version__)
__major__ = _parsed.major
__minor__ = _parsed.minor
__micro__ = _parsed.micro
