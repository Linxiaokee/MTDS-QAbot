import os
from getFrom.getQuestionsFrom import getQuestionsFrom

def getContentsFrom(root_dir_path):
    contents = []
    substr_to_remove = [".md", "Chapter"]
    for root, dirnames, filenames in os.walk(root_dir_path):
        # filter the directory names
        dirnames[:] = [d for d in dirnames if ("Chapter" in d)]
        for filename in filenames:
            # for each .md file
            if (".md" in filename):
                # get content
                with open(root+'\\'+filename, 'r', encoding='utf-8') as file:
                    next(file)
                    content = file.read()
                    contents.append(content)
    # get question and metadatas
    questions = getQuestionsFrom(root_dir_path)
    for i, content in enumerate(contents):
        questions[i].update({'content':content})
    return questions