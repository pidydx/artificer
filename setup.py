import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

sys.path.insert(0, '.')

import artificer

version = artificer.__version__

install_requires = [
    'artifacts',
    'pyramid',
    'pyramid_jinja2',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'PyYAML',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    ]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',  # includes virtualenv
    'pytest-cov',
    ]

setup(name='artificer',
      version=version,
      description='Artificer ForensicArtifacts Server',
      long_description=README + '\n\n' + CHANGES,
      license='Apache License, Version 2.0',
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Sean Gillespie',
      author_email='sean.gillespie.32@gmail.com',
      url='https://github.com/pidydx/',
      keywords='web wsgi bfg pylons pyramid forensics artifacts',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
      },
      install_requires=install_requires,
      entry_points="""\
      [paste.app_factory]
      main = artificer:main
      [console_scripts]
      initialize_artificer_db = artificer.scripts.initializedb:main
      """,
      )
