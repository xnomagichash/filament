from setuptools import setup, find_packages

setup(
    name = "filament",
    version = "0.1a1",
    packages = find_packages(),
    author = "Brendan Kohler",
    author_email = 'brendan.kohler@pycoder.net',
    description = 'Filament is a Fabric-based deployment framework for Flask.',
    license = 'BSD',
    keywords = 'flask deployment cloud fabric',
    url = "https://github.com/xnomagichash/filament",
    install_requires = ['fabric', 'flask'],
    entry_points = {'console_scripts': ['fil = filament:main']},
    include_package_data = True,
)
