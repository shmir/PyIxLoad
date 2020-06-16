from setuptools import setup, find_packages


def main():

    with open('requirements.txt') as f:
        install_requires = f.read().splitlines()
    with open('README.rst') as f:
        long_description = f.read()

    setup(
        name='pyixload',
        description='Python OO API package to automate Ixia IxLoad traffic generator',
        url='https://github.com/shmir/PyIxLoad/',
        use_scm_version={
            'root': '.',
            'relative_to': __file__,
            'local_scheme': 'node-and-timestamp'
        },
        license='Apache Software License',

        author='Yoram Shamir',
        author_email='yoram@ignissoft.com',

        long_description=long_description,

        platforms='any',
        install_requires=install_requires,
        packages=find_packages(exclude=['tests']),
        include_package_data=True,

        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Natural Language :: English',
            'Topic :: Software Development :: Testing :: Traffic Generation',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
        ],
        keywords='ixload l4l7 test tool ixia automation',
    )


if __name__ == '__main__':
    main()
