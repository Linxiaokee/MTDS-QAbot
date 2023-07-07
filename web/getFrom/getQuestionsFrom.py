import os

def getQuestionsFrom(root_dir_path):
    questions = []
    substr_to_remove = [".md", "Chapter"]
    for root, dirnames, filenames in os.walk(root_dir_path):
        # filter the directory names
        dirnames[:] = [d for d in dirnames if ("Chapter" in d)]
        for filename in filenames:
            # for each .md file
            if (".md" in filename):
                # get id
                file_id = filename
                for substr in substr_to_remove:
                    file_id = file_id.replace(substr, "")
                # get question
                _, _, question_no = file_id.partition('_')
                question_no = int(question_no.strip())
                with open(root+'\\'+filename, 'r', encoding='utf-8') as file:
                    first_line = file.readline()
                    _, _, q = first_line.partition(f'{question_no}、')
                    q = q.strip()
                    question, _, _ = q.partition('**')
                # get chapter
                _, _, chapter = root.partition('\\')
                chapter = chapter.strip()
                # form a dict
                q_dict = dict(id=file_id, question=question, path=root+'\\'+filename, chapter=chapter)
                questions.append(q_dict)
                
    return questions