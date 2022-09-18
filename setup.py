from setuptools import find_packages, setup
setup(
    name='dial-clean',
    packages=find_packages(include=['dial_clean']),
    package_data = {
        'dial_clean': ['tool_data/*']
    },
    version='0.1.0',
    description='My first Python library',
    author='Songyi',
    license='MIT',
    install_requires=['numpy==1.19.5'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==7.0.1'],
    test_suite='tests',
    entry_points={
        'console_scripts':[
            'dial-clean = dial_clean.main:main'
        ]
    }
)