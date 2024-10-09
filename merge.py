# Lets concatenate the contents of all the files in the directory of a given path and its subdirectorys into a single file callex merged.txt
# At the top of each insert add the relative filepath "// Path: <filename>".

import os

def merge_files(path):
    with open('merged.txt', 'w') as outfile:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(('.py', '.txt', '.md', '.html', '.css', '.js')):  # Fix: tuple for file extensions
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, path)  # Fix: Get the relative file path
                    with open(file_path, 'r', encoding='utf-8') as infile:  # Fix: added encoding for safety
                        outfile.write(f"// Path: {relative_path}\n")  # Use relative path in header
                        outfile.write(infile.read())
                        outfile.write("\n\n")  # Separate contents for readability

path = "./"

merge_files(path)
