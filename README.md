It's sort of like a makefile, but written in Python instead of whatever the quasi-language is that makefiles use. 

The overall goal is to make it super easy to both use and extend.  Eventually I want to include various compiler backends and support distributed builds.

It's already super nice to be able to just throw a break point in and step through the make file.

Here's a simple example:

```
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
```
