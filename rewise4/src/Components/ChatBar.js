export default function ChatBar({messages, inputRef, setMessages, submitHandler, active, setInSession, onContinueDialogue, onEndDialogue, sessionId, startSession, setSessionId}) {
    return (
      <form className='textinput'>
        <button className="chatbutton" onClick={(e) => {e.preventDefault(); startSession();}} disabled={!!sessionId} type="button">SS</button>
        <input className="chatinputbar" ref={inputRef} placeholder="Talk to REWISE4..."/>
        <button className="chatbutton" onClick={submitHandler} disabled={!active} type="submit">S</button>
        <button className="chatbutton" onClick={onContinueDialogue} disabled={!active}>CD</button>
        <button className="chatbutton" onClick={onEndDialogue} disabled={!active}>ED</button>
      </form>
    );
  }
  