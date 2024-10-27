import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.retrieval import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains.history_aware_retriever import create_history_aware_retriever
from langchain_core.prompts import MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from mem0 import MemoryClient

load_dotenv()

mem0_api = os.getenv("MEM0")
mem0_api2 = os.getenv("MEM01")
m = MemoryClient(api_key = mem0_api)
#y = MemoryClient(api_key = mem0_api2)
idx = "random@random.random"
idy = "random2@random.random"
user_memories = m.get_all(user_id=idx)
m_texts = [item['memory'] for item in user_memories]
all_memories_as_string = ". ".join(m_texts)


langchain_tracing_v2 = os.getenv("LANGCHAIN_TRACING_V2")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
open_ai_apikey = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o-mini")
#
file_path = os.getenv("IGCSEBIO_PATH")
loader = PyPDFLoader(file_path)
pages = loader.load_and_split()

vectorstore = Chroma.from_documents(documents=pages, embedding=OpenAIEmbeddings())

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

system_prompt = (
    f"You are a Quiz generator and you must Score the User when the User completes The Quiz Questions. Give 3 questions per quiz but only send one question at a time i.e after user answers question 1, send question 2.. after user answers question 2 send question 3.. after user answers question 3 send overall score and report - then offer to do a new quiz and if user wants to learn more on something, tell user to go to Learning Agent - and remember to always offer to do a new quiz. First ask the user what subject he wants to be quizzed on and if he wants a general syllabus practice quiz or customize according to his learning sessions - for this, please remember and customize the quiz according to the useful information from user's teaching session which is: {all_memories_as_string}"
    "\n\n"
    "{context}"
)


contextualize_q_system_prompt = (
    f"Given a chat history and the latest user quiz response which might reference context in the chat history, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is. Also remember initial prompt: You are a Quiz generator and you must Score the User when the User completes The Quiz Questions. Give 3 questions per quiz but only send one question at a time i.e after user answers question 1, send question 2.. after user answers question 2 send question 3.. after user answers question 3 send overall score and report - then offer to do a new quiz and if user wants to learn more on something, tell user to go to Learning Agent - and remember to always offer to do a new quiz. First ask the user what subject he wants to be quizzed on and if he wants a general syllabus practice quiz or customize according to his learning sessions - for this, please remember and customize the quiz according to the useful information from user's teaching session which is: {all_memories_as_string}"
)

contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)


question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

store = {}

config = {"configurable": {"session_id": "abc3"}}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


from ai_engine.chitchat import ChitChatDialogue
from ai_engine.messages import DialogueMessage
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import os
from openai import OpenAI


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SEED_PHRASE = os.getenv("AGENTSEED2")
AGENT_MAILBOX_KEY = os.getenv("MAILROOMKEY2")
API_KEY = os.getenv("ALPHAVANTAGEAPI")

quiz_agent = Agent(
      name="quiz_agent",
      seed=SEED_PHRASE,
      mailbox=f"{AGENT_MAILBOX_KEY}@https://agentverse.ai",
)

fund_agent_if_low(quiz_agent.wallet.address())

print(quiz_agent.address)

class InitiateChitChatDialogue(Model):
    pass
class AcceptChitChatDialogue(Model):
    """I accept ChitChat dialogue request"""
    pass
class ChitChatDialogueMessage(DialogueMessage):
    """ChitChat dialogue message"""
    pass
class ConcludeChitChatDialogue(Model):
    """I conclude ChitChat dialogue request"""
    pass
class RejectChitChatDialogue(Model):
    """I reject ChitChat dialogue request"""
    pass

chitchat_dialogue = ChitChatDialogue(
    version="0.66",
    storage=quiz_agent.storage,
)

@chitchat_dialogue.on_initiate_session(InitiateChitChatDialogue)
async def start_chitchat(
    ctx: Context,
    sender: str,
    msg: InitiateChitChatDialogue,
):
    ctx.logger.info(f"Received init message from {sender} Session: {ctx.session}")
    await ctx.send(sender, AcceptChitChatDialogue())

@chitchat_dialogue.on_start_dialogue(AcceptChitChatDialogue)
async def accepted_chitchat(
    ctx: Context,
    sender: str,
    _msg: AcceptChitChatDialogue,
):
    ctx.logger.info(
        f"session with {sender} was accepted. This shouldn't be called as this agent is not the initiator."
    )
    
@chitchat_dialogue.on_reject_session(RejectChitChatDialogue)
async def reject_chitchat(
    ctx: Context,
    sender: str,
    msg: RejectChitChatDialogue,
):
    ctx.logger.info(f"Received conclude message from: {sender}")

@chitchat_dialogue.on_continue_dialogue(ChitChatDialogueMessage)
async def answer_question(
    ctx: Context,
    sender: str,
    msg: ChitChatDialogueMessage,
):
    ctx.logger.info(f"Received message: {msg.user_message} from: {sender}")
    answer = conversational_rag_chain.invoke(
    {"input": msg.user_message},
    config=config,  
)["answer"]
    try:
        await ctx.send(
            sender,
            ChitChatDialogueMessage(
                type="agent_message",
                agent_message=answer
            ),
        )
    except EOFError:
        await ctx.send(sender, ConcludeChitChatDialogue())

@chitchat_dialogue.on_end_session(ConcludeChitChatDialogue)
async def conclude_chitchat(
    ctx: Context,
    sender: str,
    msg: ConcludeChitChatDialogue,
):
    ctx.logger.info(f"Received conclude message from: {sender}")
    #ctx.logger.info(ctx.dialogue)

quiz_agent.include(chitchat_dialogue, publish_manifest=True)
quiz_agent.run()