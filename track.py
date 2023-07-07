from IPython.display import display, Markdown
from langchain.vectorstores import Chroma

from langchain.embeddings.openai import OpenAIEmbeddings
openai_embedding = OpenAIEmbeddings(
    model="text-embedding-ada-002",
    openai_api_key="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"
)

from getFrom.getDatasFrom import getDatasFrom
all_data = getDatasFrom("Data\Chapter1")
datas = [d.get('data') for d in all_data]
ids = [d.get('id') for d in all_data]
metadatas = []
source = [d.get('path') for d in all_data]
chapters = [d.get('chapter') for d in all_data]

for i, p in enumerate(source):
    scope = []
    if (chapters[i] == 'Chapter1'):
        scope = "软件安装、账号绑定及登录相关问题"
    m_dict = dict(source=p, chapter=chapters[i], scope=scope)
    metadatas.append(m_dict)

db = Chroma.from_texts(datas, openai_embedding, metadatas, ids=ids)

from langchain.chat_models import ChatOpenAI
chat = ChatOpenAI(
    openai_api_key='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',
    temperature=0
)

from langchain.chains import ConversationalRetrievalChain, LLMChain
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
memory = ConversationBufferMemory(memory_key="chat_history", input_key='question', output_key='answer', return_messages=True)
CONDENSE_QUESTION_PROMPT = PromptTemplate(
    input_variables=['chat_history', 'question'], 
    output_parser=None, partial_variables={}, 
    template='''
    Given the following conversation and a follow up question,
    rephrase the follow up question to be a standalone question,
    in its original language.\n\n 
    
    Chat History:\n{chat_history}\n
    Follow Up Input: {question}\n
    Standalone question:
    ''', 
    template_format='f-string', 
    validate_template=True
)
question_generator = LLMChain(llm=chat, prompt=CONDENSE_QUESTION_PROMPT, verbose=True)
docs_chain = load_qa_with_sources_chain(llm=chat, chain_type='stuff', verbose=True)
qa = ConversationalRetrievalChain(
    memory=memory,
    retriever=db.as_retriever(),
    question_generator=question_generator,
    combine_docs_chain=docs_chain,
    return_generated_question=True,
    verbose=True
)

def q(query):
    return qa({'question':query})['answer']

import gradio as gr
demo = gr.Interface(fn=q, inputs="text", outputs="text")
demo.launch()