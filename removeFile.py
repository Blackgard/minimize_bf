"""
Delete don't work file with 'PLA' folder
"""

import os


def find_broken_file(folder: str):
    " Find don't work file in folder and delete this"
    if not folder: return None
    
    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        try:
            with open(path) as f:
                int(f.readline().split()[1])
                int(f.readline().split()[1])
                [i for i in f.readline().split()[1:]]
                [i for i in f.readline().split()[1:]]
                int(f.readline().split()[1])
                [[j for j in i.rstrip().split()] for i in f.readlines()[:-1]]
        except IndexError as err:
            delete_file(path)
        except ValueError as err:
            delete_file(path)

def delete_file(fileName: str) -> bool:
    """ Delete file on folder """
    return os.remove(fileName)


if __name__ == "__main__":
    find_broken_file('pla')
    