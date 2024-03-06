import argparse

class SnakeBuildSystem:
    def __init__(self):
        self.argumentParser = argparse.ArgumentParser(description="build.py arguments")
        self.argumentParser.add_argument('--configuration', type=str, help='Project configuration (Debug, Release, etc)', default="Debug")
        self.argumentParser.add_argument('--platform', type=str, help='Project platform (Windows, Linux, etc)', default="Windows")
        self.argumentParser.add_argument('--forceRebuild', action='store_true', help='Force rebuild this project', default=False)

        self.args, self.unknownArgs = self.argumentParser.parse_known_args()

    @property
    def configuration(self):
        return self.args.configuration

    @property
    def platform(self):
        return self.args.platform
    
    @property
    def forceRebuild(self):
        return self.args.forceRebuild


