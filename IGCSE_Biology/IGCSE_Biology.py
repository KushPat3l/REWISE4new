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
m = MemoryClient(api_key = mem0_api)
idx = "random@random.random"
user_memories = m.get_all(user_id="random@random.random")
m_texts = [item['memory'] for item in user_memories]
all_memories_as_string = ". ".join(m_texts)


langchain_tracing_v2 = os.getenv("LANGCHAIN_TRACING_V2")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
open_ai_apikey = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o-mini", max_tokens=50)
#
file_path = os.getenv("IGCSEBIO_PATH")
loader = PyPDFLoader(file_path)
pages = loader.load_and_split()

vectorstore = Chroma.from_documents(documents=pages, embedding=OpenAIEmbeddings())

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})

system_prompt = (
    f"PLEASE SPEAK LIKE SPONGEBOB! You are an IGCSE Biology teacher answering student questions. Please remember useful information from previous session which is: {all_memories_as_string}"
    "\n\n"
    "{context}"
)


contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."

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

config = {"configurable": {"session_id": "abc2"}}

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

SEED_PHRASE = os.getenv("AGENTSEED")
AGENT_MAILBOX_KEY = os.getenv("MAILROOMKEY")
API_KEY = os.getenv("ALPHAVANTAGEAPI")

learnerAgent = Agent(
      name="learnerAgent",
      seed=SEED_PHRASE,
      mailbox=f"{AGENT_MAILBOX_KEY}@https://agentverse.ai",
)

fund_agent_if_low(learnerAgent.wallet.address())

print(learnerAgent.address)

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
    storage=learnerAgent.storage,
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
    m.add(f"{msg.user_message}", user_id=idx)

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

learnerAgent.include(chitchat_dialogue, publish_manifest=True)
learnerAgent.run()