import os
from getFrom.getContentsFrom import getContentsFrom

def getDatasFrom(root_dir_path):
    datas = []
    substr_to_remove = [".md", "Chapter"]
    for root, dirnames, filenames in os.walk(root_dir_path):
        # filter the directory names
        dirnames[:] = [d for d in dirnames if ("Chapter" in d)]
        for filename in filenames:
            # for each .md file
            if (".md" in filename):
                # get data
                with open(root+'\\'+filename, 'r', encoding='utf-8') as file:
                    data = file.read()
                    datas.append(data)
    # get question and metadatas
    contents = getContentsFrom(root_dir_path)
    for i, data in enumerate(datas):
        contents[i].update({'data':data})
    return contents