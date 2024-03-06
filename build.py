import os
import shutil
from SnakeBuildSystem import *

def CopyDLLs(sourceDir, destDir):
    dllFiles = ['libunwind.dll', 'libc++.dll']
    for file in dllFiles:
        srcPath = os.path.join(sourceDir, file)
        destPath = os.path.join(destDir, file)
        if not os.path.exists(destPath): 
            try:
                shutil.copy2(srcPath, destPath)
            except shutil.Error as e:
                print(f'shutil.Error Copying {file} from {srcPath} to {destPath}: {e}')
            except IOError as e:
                print(f'IOError Copying {file} from {srcPath} to {destPath}: {e.strerror}')


# Example usage
if __name__ == "__main__":
    # Create the parser
    snakeBuild = SnakeBuildSystem() # Note, this also parses some default command line arguments for the system

    clangBinDir = "E:/Projects/llvm-mingw-20240227-ucrt-x86_64/bin/"
    compiler = ClangCompiler(snakeBuild, clangBinDir + "clang++")

    binaryToCreate = "example1.exe"
    
    sourceDirectory = './example1/src'
    intermediatesDirectory = "./example1/int"
    binariesDirectory = "./example1/bin"

    compiler.SetOutputDirectory(intermediatesDirectory)
    compiler.AddIncludeDirectoriesRecursive(sourceDirectory)
        
    filesToCompile = []
    RecursivelyAddFilesToArray(filesToCompile, sourceDirectory, ('.c', '.cpp'))
    compiler.AddCompileFiles(filesToCompile)

    if (snakeBuild.configuration == "Release"):
        compiler.AddCompilerFlag("-O3")
    else:
        compiler.AddCompilerFlag("-O0")

    if (snakeBuild.configuration != "Ship"):
        compiler.AddCompilerFlag("-g")  # ENABLE_DEBUG_INFO

    compiler.AddCompilerFlag("-std=c++17")

    (compileSuccess, objFileNames) = compiler.StartCompileAndWait()

    #TODO: Also check to see if our output file is valid.  We can compile everything, fail to link, then think we're good when we're not.
    # link we we output anything to compile
    if compileSuccess or True:
        linker = ClangLinker(clangBinDir + "clang++")
        linker.SetInputDirectory(intermediatesDirectory)
        linker.SetOutputDirectory(binariesDirectory)
        linker.AddInputFiles(objFileNames)

        linker.CreateBinary(binaryToCreate)

        CopyDLLs(clangBinDir, linker.GetOutputDirectory())
    
    print("DONE")



