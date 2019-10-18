import os
import math
import sys
import argparse
from pathlib import Path

class Tree:
    completedDirPaths = set()
    options = {
        "all": False,
        "level": math.inf,
        "dirOnly": False,
        "fullPathPrefix": False
    }

    def __init__(self, dirName, options={}):
        self.dirName = dirName
        self.options.update(options)
        self.dirCount = 0
        self.fileCount = 0

        if self.options["level"] < 1:
            raise Exception("tree : Invalid level must be greater than 0")
    
    def registerPath(self, path):
        if path.is_dir():
            self.dirCount += 1
        else:
            self.fileCount += 1
    
    def summary(self):
        print(f"{self.dirCount} directories, {self.fileCount} files")
    
    def traverse(self):
        path = Path(self.dirName)
        
        # Check whether the path exists
        if path.exists() is False:
            print(f"{self.dirName}: Path not found")
            return

        # Check whether the path is a directory
        if path.is_dir() is False:
            print(f"{self.dirName} [error opening dir]")
            return

        print(self.dirName)

        self.__traverse(path, 1)
    
    def parents(self, path, level):
        parents = []
        for l in range(level - 1):
            path = path.parent
            parents.append(path)
        parents.reverse()

        return parents

    def __traverse(self, path, level):
        maxLevel = self.options["level"]
        
        if level > maxLevel:
            return

        # Check whether next level is maxLevel
        isLastLevel = ( level == maxLevel )

        entries = sorted(path.iterdir())

        if self.options["all"] is False:
            entries = list(filter(lambda e: e.name[0] != ".", entries))
        
        if self.options["dirOnly"] is True:
            entries = list(filter(lambda e: e.is_dir(), entries))

        entriesLength = len(entries)

        parents = None
        for index, entry in enumerate(entries):
            self.registerPath(entry)

            path = Path(entry)

            isLastEntry = True if (index + 1) == entriesLength else False
            isReadable = os.access(entry.__str__(), os.R_OK)
            errorMessage = "[error opening dir]" if entry.is_dir() and not os.access(entry.__str__(), os.R_OK) and not isLastLevel else ""
            entryName = entry if self.options["fullPathPrefix"] else entry.name

            # Print spaces or vertical lines
            if parents is None:
                parents = self.parents(path, level)
            
            for parent in parents:
                if parent not in self.completedDirPaths:
                    print("│   ", end="")
                else:
                    print("    ", end="")
            
            # Print entry name
            print("└── ", end="") if isLastEntry else print("├── ", end="")
            print(f"{entryName} {errorMessage}")

            # Update completedDirectoryPaths
            if isLastEntry:
                self.completedDirPaths.add(path)

            # Traverse direcorty
            if entry.is_dir() and isReadable:
                self.__traverse(path, level + 1)

def parseArguments():
    parser = argparse.ArgumentParser(description='Directory tree')

    parser.add_argument('-a', action="store_true", default=False, dest="all", help="include hidden entries")
    parser.add_argument('-d', action="store_true", default=False, dest="dirOnly", help="list only directories")
    parser.add_argument('-L', action="store", dest="level", default=math.inf, type=int, help="maximum level to traverse")
    parser.add_argument('-f', action="store_true", dest="fullPathPrefix", default=False, help="print full path prefix")

    options, dirs = parser.parse_known_args()

    return vars(options), dirs

if __name__ == "__main__":
    options, dirs = parseArguments()

    if len(dirs) == 0:
        dirs = ["."]
    
    for dir in dirs:
        try:
            tree = Tree(dir, options)
            tree.traverse()
            tree.summary()
        except BaseException as e:
            print(e)