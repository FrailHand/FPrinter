from setuptools import setup, find_packages

requires = [
    'pyramid',
    'pyramid_jinja2',
    'waitress',
    'pyglet',
    'cairosvg',
    'RPi.GPIO;platform_machine=="aarch64"',
    'smbus-cffi;platform_machine=="aarch64"',
    'fake-rpi;platform_machine=="x86_64"',
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
