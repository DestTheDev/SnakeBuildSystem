import subprocess
import os
import io
import concurrent.futures
from .Utils import *


class ClangLinker:
    def __init__(self, pathToBinDir):
        self.pathToBinDir = AddQuotes(pathToBinDir)
        self.linkerFlags = []
        self.libraryPaths = []
        self.librariesToLink = []
        self.filesToLink = []
        self.outputDir = "./bin"
        self.inputDir = "./int"

    def SetOutputDirectory(self, directory):
        self.outputDir = directory

    def GetOutputDirectory(self):
        return self.outputDir

    def SetInputDirectory(self, directory):
        self.inputDir = directory

    def GetInputDirectory(self):
        return self.inputDir

    def AddInputFiles(self, files):
        self.filesToLink.extend(files)

    def AddInputFile(self, file):
        self.filesToLink.append(file)

    def AddLibrarySearchPath(self, directory):
        self.libraryPaths.append(directory)
    
    def AddLibrary(self, library):
        self.librariesToLink.append(library)
        
    def AddLinkerFlag(self, flag):
        self.linkerFlags.append(flag)

    def CreateBinary(self, outputName):
        print(f"Begin linking {outputName}")

        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)

        stringBuilder = io.StringIO()

        stringBuilder.write(self.pathToBinDir)

        for flag in self.linkerFlags:
            stringBuilder.write(f" {flag}")

        for dir in self.libraryPaths:
            stringBuilder.write(f" -L\"{dir}\"")

        for lib in self.librariesToLink:
            stringBuilder.write(f" -l\"{lib}\"")

        # Save off our command without the files
        compilationCommandWithoutFiles = stringBuilder.getvalue()

        # Add all the files for dependency checking
        for file in self.filesToLink:
            stringBuilder.write(f" \"{self.inputDir}/{file}\"")

        stringBuilder.write(f" -o \"{self.outputDir}/{outputName}\"")

        # Then figure out what we actually need to compile by using -MM to output the dependencies
        command = stringBuilder.getvalue()
        print('Running linker command: ' + command)
        result = subprocess.run(command, capture_output=True)
        if result.returncode != 0:
            print(f"Linking error in {command}")
            print(result.stdout.decode())
            print(result.stderr.decode())
            return 1
        else:
            print(f"{self.outputDir}/{outputName} created successfully.")
        
        print("Linking finished")
        return 0