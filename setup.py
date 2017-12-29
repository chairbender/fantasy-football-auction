from setuptools import setup

setup(name='fantasy_football_auction',
      packages=['fantasy_football_auction'],
      version='0.9.2',
      description='Python library simulating a fantasy football auction. Intended to be used for AI, but you should be '
                  'able to use this for other purposes as well. This task assumes that each draftable player has a '
                  'specific value (for example, looking at the ratings from FantasyPros).',
      author='Kyle Hipke',
      author_email='kwhipke1@gmail.com',
      url='https://github.com/chairbender/fantasy-football-auction',
      download_url='https://github.com/chairbender/fantasy-football-auction/archive/0.9.1.tar.gz',
      keywords=['AI', 'football', 'fantasy', 'auction'],
      classifiers=[],
      python_requires=">=3.6",
      install_requires=[]
      )
