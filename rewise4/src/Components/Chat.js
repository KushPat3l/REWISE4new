import Display from "./Display"
import ChatBar from "./ChatBar"

export default function Chat({messages, inputRef, setMessages, submitHandler, active, setInSession, onContinueDialogue, onEndDialogue, sessionId, startSession, setSessionId, learn}) {
    return (
      <div className='contentcontainer'>
        <Display messages={messages} learn={learn}/>
        <ChatBar messages={messages} setMessages={setMessages} inputRef={inputRef} submitHandler={submitHandler} active={active} setInSession={setInSession} onContinueDialogue={onContinueDialogue} onEndDialogue={onEndDialogue} sessionId={sessionId} startSession={startSession} setSessionId={setSessionId}/>
      </div>
    )
  }