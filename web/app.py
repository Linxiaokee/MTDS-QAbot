from flask import Flask
from markupsafe import escape
from flask import render_template, send_from_directory
from flask import request
from flask import jsonify
from flask import url_for

app = Flask(__name__)
initialized = False
app.jinja_env.variable_start_string = '[['
app.jinja_env.variable_end_string = ']]'

@app.before_request
def initialize():
    global initialized
    if not initialized:
        from IPython.display import display, Markdown
        from langchain.vectorstores import Chroma
        pro_key = "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"

        #embedding
        from langchain.embeddings.openai import OpenAIEmbeddings
        openai_embedding = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            openai_api_key=pro_key
        )

        # get datas and metadatas
        from getFrom.getDatasFrom import getDatasFrom
        all_data = getDatasFrom("static\Data")

        datas = [d.get('data') for d in all_data]
        ids = [d.get('id') for d in all_data]
        metadatas = []
        source = [d.get('path') for d in all_data]
        chapters = [d.get('chapter') for d in all_data]

        for i, p in enumerate(source):
            m_dict = dict(source=p, chapter=chapters[i])
            metadatas.append(m_dict)

        # initialize db
        global db 
        db = Chroma(embedding_function=openai_embedding, persist_directory='./chroma_db')
        #db = Chroma.from_texts(datas, openai_embedding, metadatas, ids=ids, persist_directory='./chroma_db')
        #db.persist()
        # llm & chat model
        from langchain.chat_models import ChatOpenAI
        from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
        chat = ChatOpenAI(
            openai_api_key=pro_key,
            model='gpt-3.5-turbo',
            temperature=0,
            streaming="True",
            callbacks=[StreamingStdOutCallbackHandler()]
        )
        from langchain.llms import OpenAI
        llm = OpenAI(
            openai_api_key=pro_key,
            temperature=0
        )

        # constructing chain
        from langchain.chains import ConversationalRetrievalChain, LLMChain
        from langchain.chains.qa_with_sources import load_qa_with_sources_chain
        from langchain.chains.question_answering import load_qa_chain
        from langchain.memory import ConversationSummaryBufferMemory, ConversationTokenBufferMemory, ConversationBufferMemory
        from langchain.prompts import PromptTemplate
        from prompts import CONDENSE_QUESTION_PROMPT, QA_PROMPT, NONSENSE_PROMPT
        memory = ConversationTokenBufferMemory(
            llm=llm, 
            memory_key="chat_history", 
            input_key='question', 
            output_key='answer', 
            max_token_limit=4000,
            return_messages=True
        )
        question_generator = LLMChain(
            llm=llm, prompt=NONSENSE_PROMPT, verbose=True)
        docs_chain = load_qa_chain(
            llm=chat, chain_type='stuff', prompt=QA_PROMPT, output_key='answer', verbose=True)
        global qa
        qa = ConversationalRetrievalChain(
            memory=memory,
            retriever=db.as_retriever(),
            question_generator=question_generator,
            combine_docs_chain=docs_chain,
            return_generated_question=True,
            verbose=True,
            return_source_documents=True
        )
        # set the flag to true
        initialized = True

import re
def read_images(text):
    image_pattern = r'!\[.*?\]\((.*?)\)'
    image_sentences = re.findall(image_pattern, text)
    return image_sentences

@app.route('/')
def hello():
    return render_template('hello.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = (request.json)['text']
    response = qa({'question':data})
    md_contents = []
    for doc in response['source_documents']:
        file_name = doc.metadata['source']
        markdown_text = doc.page_content
        # get images in .md
        images = read_images(doc.page_content)
        folder_path = file_name.rsplit('\\', 1)[0]
        folder_path = folder_path.replace('\\' ,'/')
        markdown_images = []
        for image in images:
            image = '../' + folder_path + '/' + image
            markdown_images.append(image)
        md_contents.append({'file_name': file_name, 'markdown_text': markdown_text, 'markdown_images': markdown_images})
        print(markdown_images)
    return jsonify({'text':response['answer'], 'markdown_contents':md_contents})