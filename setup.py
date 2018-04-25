from distutils.core import setup

setup(
    name='SeleniumDrivers',
    packages=['SeleniumDrivers'],  # this must be the same as the name above
    version='0.2',
    description='A Python library or utility to download/update Selenium Driver files',
    author='Naveenchandar',
    author_email='naveen_sty@yahoo.in',
    # use the URL to the github repo
    url='https://github.com/navchandar/SeleniumDrivers',
    download_url='https://github.com/navchandar/SeleniumDrivers/archive/0.2.tar.gz',
    license='GPL3',
    keywords=['testing', 'selenium', 'driver', 'webdrivers', 'update', 'automation'],  # arbitrary keywords
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers, Testers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: GPL3 License',

        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'],
)
