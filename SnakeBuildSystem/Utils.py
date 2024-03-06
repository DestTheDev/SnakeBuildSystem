import os

def AddQuotes(string):
    if not string.startswith('"'):
        string = '"' + string
    if not string.endswith('"'):
        string = string + '"'
    return string

# goes in each directory and adds all of the files with the proper extension to the list
def RecursivelyAddFilesToArray(filesToCompile, sourceDirectory, ext: str | tuple[str, ...]):
    for root, dirs, files in os.walk(sourceDirectory):
        for file in files :
            if file.endswith(ext):
                fullFilePath = os.path.join(root, file)
                filesToCompile.append(fullFilePath)
