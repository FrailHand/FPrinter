from setuptools import setup, find_packages

requires=[
    'pyramid',     
    'waitress',
    'pyglet',
    'cairosvg'
    ]


setup(
    name='fprinter',
    version='0.1',
    packages=find_packages(),
    description='3D DLP printer controller for Raspberry Pi',
    author='electroLAB (UMONS)',
    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.txt', '*.rst', '*.md'],
        },
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=requires,
    entry_points={
          'console_scripts': [
              'fprinter_backend = fprinter.backend:main',             
          ],
           'paste.app_factory': [
              'main = fprinter.frontend:main',
          ],
              
      },
)
