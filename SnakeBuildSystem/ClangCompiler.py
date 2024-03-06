import subprocess
import os
import io
import concurrent.futures
import json

from .SnakeBuildSystem import SnakeBuildSystem
from .Utils import *


class ClangCompiler:
    def __init__(self, snakeBuild, pathToBinDir):
        self.pathToBinDir = AddQuotes(pathToBinDir)
        self.compileFlags = []
        self.compileDefines = []
        self.includeDirs = []
        self.filesToCompile = []
        self.outputDir = "./int"
        self.forceRecompile = snakeBuild.forceRebuild

    def SetOutputDirectory(self, directory):
        self.outputDir = directory

    def GetOutputDirectory(self):
        return self.outputDir
    
    def AddDefine(self, define):
        self.compileDefines.append(f"{define}")

    def AddIncludeDirectory(self, directory):
        self.includeDirs.append(directory)
    
    def AddIncludeDirectoriesRecursive(self, rootDir):
        for dirpath, dirnames, filenames in os.walk(rootDir):
            self.includeDirs.append(dirpath)

    def AddCompileFiles(self, files):
        self.filesToCompile.extend(files)

    def AddCompileFile(self, file):
        self.filesToCompile.append(file)

    def AddCompilerFlag(self, flag):
        self.compileFlags.append(flag)

    def GenerateVSCodeCppPropertiesFile(self, filename=".vscode/c_cpp_properties.json"):
        cppStandard = "c++17"  # Default value

        # Parse the C++ standard from the compiler flags
        for flag in self.compileFlags:
            if flag.startswith("-std="):
                cppStandard = flag[5:]
                break

        config = {
            "configurations": [
                {
                    "name": "Default",
                    "includePath": [f"{path}/**" for path in self.includeDirs],
                    "defines": self.compileDefines,
                    "compilerPath": self.pathToBinDir.strip('"'),
                    "cStandard": "c11",
                    "cppStandard": cppStandard,
                    "intelliSenseMode": "clang-x64"
                }
            ],
            "version": 4
        }

        try:
            with open(filename, "w") as file:
                json.dump(config, file, indent=4)
        except IOError as e:
            print(f"Error: Unable to open or write to file '{filename}'. {str(e)}")


    def __parseDependencyOutput(self, dependencyOutputString):
        # Parse the dependency output to extract object and source files.
        lines = dependencyOutputString.strip().split('\n')
        dependencies = []
        for line in lines:
            parts = line.split(':')
            if len(parts) == 2:
                objFileName = parts[0].strip()
                sourceFileNames = parts[1].strip().split()
                #print(f"obj: {objFileName} src: {' '.join(sourceFileNames)}")
                dependencies.append((objFileName, sourceFileNames))
        return dependencies

    def __isRecompileNeeded(self, objFileName, sourceFileNames):
        # Determine if recompilation is needed based on file timestamps.
        #if force recompile
        #return True
        if self.forceRecompile:
            return True

        try:
            objModifiedTime = os.path.getmtime(os.path.join(self.outputDir, objFileName))
        except FileNotFoundError:
            return True  # Object file doesn't exist

        for file in sourceFileNames:
            try:
                if os.path.getmtime(file) > objModifiedTime:
                    return True  # A dependency is newer
            except FileNotFoundError:
                return True # There shouldn't be missing files, so recompile if there are (someone deleted it right as we ran this?)

        return False

    def __compileFile(self, compilationCommand, cppFileName, objFileName):
        # Compile a single C++ file.
        
        #if verbose
        #print(f"Running compile cmd {compilationCommand}")
        result = subprocess.run(compilationCommand, capture_output=True)
        if result.returncode != 0:
            #print(f"Compilation error in {cppFileName}")
            print(result.stdout.decode())
            print(result.stderr.decode())
        else:
            self.compiledAnything = True
        #print(f"Compiled {cppFileName} to {objFileName}")

    def __KickoffNeededCompiles(self, compilationCommand, dependencyOutputString):
        #print(f"kickoff:\n compilationCommand: {compilationCommand}\n dependencyOutputString:\n {dependencyOutputString}")       
        dependencies = self.__parseDependencyOutput(dependencyOutputString)

        self.compiledAnything = False
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for objFileName, sourceFileNames in dependencies:
                #print(f"objFileName: {objFileName} sourceFileNames: {sourceFileNames}")
                cppFileName = sourceFileNames[0]  # Assuming first source file is the .cpp file
                if self.__isRecompileNeeded(objFileName, sourceFileNames): # Todo: Should I do this in parallel too?
                    print(f"Compiling {cppFileName}")
                    
                    #if single threaded compile:
                    #self.__compileFile(f"{compilationCommand} {cppFileName} -c -o {self.outputDir}/{objFileName}" , cppFileName, objFileName)
                    futures.append(executor.submit(self.__compileFile, f"{compilationCommand} {cppFileName} -c -o {self.outputDir}/{objFileName}", cppFileName, objFileName))
                else:
                    print(f"{cppFileName} is up to date")
            # Wait for all compilation jobs to complete
            concurrent.futures.wait(futures)

        objFileNames = [objFileName for objFileName, _ in dependencies]
        return (self.compiledAnything, objFileNames)

    #def __KickoffNeededCompiles(self, compilationCommand, dependencyOutputString):
        # parse the output from clang's -MM argument to get a list of .o files, then check to see if those need to be compiled or not based on the timestamps.
        # Then kick off parallel process jobs by running clang using compilationCommand

    def StartCompileAndWait(self):
        print("Begin compile")

        if not os.path.exists(self.outputDir):
            os.makedirs(self.outputDir)

        stringBuilder = io.StringIO()

        stringBuilder.write(self.pathToBinDir)

        for define in self.compileDefines:
            stringBuilder.write(" -D" + define)

        for flag in self.compileFlags:
            stringBuilder.write(" " + flag)

        for dir in self.includeDirs:
            stringBuilder.write(" -I\"" + dir + "\"")

        # add in color diagnostic output by default
        # TODO: Add an option to disable this
        stringBuilder.write(" -fansi-escape-codes -fcolor-diagnostics")

        # Save off our command without the files
        compilationCommandWithoutFiles = stringBuilder.getvalue()

        # Add all the files for dependency checking
        for file in self.filesToCompile:
            stringBuilder.write(" " + file)

        print('Running compiler command: ' + stringBuilder.getvalue())

        # Then figure out what we actually need to compile by using -MM to output the dependencies
        result = subprocess.run(stringBuilder.getvalue() + " -MM", capture_output=True, universal_newlines=True)
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        
        #TODO: Need to also recompile if the compiler flags changed
        #self.forceRecompile = True
            
        (success,outputObjFiles) = self.__KickoffNeededCompiles(compilationCommandWithoutFiles, result.stdout)        
        print("Compile finished")
        
        return (success,outputObjFiles)