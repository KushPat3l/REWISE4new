import json
from ai_engine.chitchat import ChitChatDialogue
from ai_engine.messages import DialogueMessage
from uagents import Agent, Context, Model
from uagents.setup import fund_agent_if_low
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

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
    response = client.chat.completions.create(
  model="gpt-4o-mini",
  messages=[
    {"role": "system", "content": "You are a helpful teacher."},
    {"role": "user", "content": msg.user_message}
  ], 
  max_tokens=50
    )
    contents = response.choices[0].message.content
    try:
        await ctx.send(
            sender,
            ChitChatDialogueMessage(
                type="agent_message",
                agent_message=contents
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
    ctx.logger.info(f"Received conclude message from: {sender}; accessing history:")
    ctx.logger.info(ctx.dialogue)

learnerAgent.include(chitchat_dialogue, publish_manifest=True)
learnerAgent.run()