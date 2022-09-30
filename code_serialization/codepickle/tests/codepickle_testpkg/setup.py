from distutils.core import setup


dist = setup(
    name='codepickle_testpkg',
    version='0.0.0',
    description='Package used only for codepickle testing purposes',
    author='Cloudpipe',
    author_email='cloudpipe@googlegroups.com',
    license='BSD 3-Clause License',
    packages=['_codepickle_testpkg'],
    python_requires='>=3.5',
)
