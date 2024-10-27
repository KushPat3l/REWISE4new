export default function Display({ messages, learn }) {
  return (
    <div className='chatmessages' id="messages">
      <div>
        {messages.map((msg, index) => (
          <div key={index} className={msg.person === 0 ? 
            (learn ? 'chatmessage sent' : 'chatmessageQ sent') : 
            (learn ? 'chatmessage rcvd' : 'chatmessageQ rcvd')}>
            {msg.message}
          </div>
        ))}
      </div>
    </div>
  );
}
