from uagents import Agent, Model, Context, Protocol
from ai_engine import UAgentResponse, UAgentResponseType

ConnectorAgent = Agent()

class ConnectionRequest(Model):
    subject : str
    answer: str

ConnectorAgent_Protocol = Protocol('Learning Agent protocol')

@ConnectorAgent_Protocol.on_message(model=ConnectionRequest, replies=UAgentResponse)
async def on_youtube_request(ctx: Context, sender: str, msg: ConnectionRequest):
    ctx.logger.info(f"Received Request from {sender} with subject request")
    ctx.logger.info(msg.subject)
    await ctx.send(sender, UAgentResponse(message="Thank you for studying with REWISE4. You can connect with me anytime", type=UAgentResponseType.FINAL))

ConnectorAgent.include(ConnectorAgent_Protocol)

ConnectorAgent.run()