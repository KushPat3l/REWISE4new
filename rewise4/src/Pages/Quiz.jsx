import '../App.css';
import '../Styles/Learn.css';
import { useState, useRef } from "react";
import axios from 'axios';
import Chat from '../Components/Chat.js';
import About from "./About.jsx";
import { Routes, Route } from 'react-router-dom';
import { sleep } from "../actions.js";
import { v4 as uuidv4 } from 'uuid';


function Interface() {
  const [globalMessageId, setGlobalMessageId] = useState('')
  const [messages, setMessages] = useState([]);
  const [active, setActive] = useState(true);
  const [sessionId, setSessionId] = useState(null);
  const [error, setError] = useState(null);
  const inputRef = useRef();

  async function scrollToBottom() {
    await sleep(50);
    document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
  }

  async function startSession() {
    try {
        setActive(false);
        
        // Step 1: Start the session and get the session ID from the response
        const response = await axios.post('http://localhost:5000/api/start_session');
        
        const sessionId = response.data.session_id;
        console.log("Session ID from response:", sessionId);

        // Step 2: Set the session ID in the state
        setSessionId(sessionId);
        setError(null); // Clear any previous errors

        // Step 3: Submit the objective using the session ID from the response
        const objectiveMessage = 'I want to do a quiz!';
        setMessages(prevMessages => [...prevMessages, { message: objectiveMessage, person: 0 }]);
        scrollToBottom();

        await axios.post('http://localhost:5000/api/submit_objective', {
            objective: objectiveMessage,
            context: `User full Name: Test User\nUser email: kush.patel@fetch.ai\nUser location: latitude=51.5072, longitude=0.1276\n`,
            session_id: sessionId
        });

        // Step 4: Wait for 5 seconds
        await sleep(5000);

        // Step 5: Get the agent response and parse it
        try {
            const response = await axios.get('http://localhost:5000/api/get_messages', {
                params: { 
                    session_id: sessionId
                },
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            console.log("API Response:", response.data);

            const { agent_response } = response.data;
            let lastMessageId = '';

            if (agent_response && agent_response.length) {
                const parsedMessages = agent_response.map(res => JSON.parse(res));

                parsedMessages.forEach(parsedMessage => {
                    let messageText = '';

                    if (parsedMessage.type === 'agent_info') {
                        messageText = parsedMessage.agent_info || '';
                    } else if (parsedMessage.type === 'agent_json') {
                        messageText = parsedMessage.agent_json?.text || '';
                        const options = parsedMessage.agent_json?.options || [];

                        const formattedOptions = options.length
                            ? options.map(opt => `${opt.key}: ${opt.value}`).join('\n')
                            : '';

                        if (formattedOptions) {
                            messageText += `\nOptions:\n${formattedOptions}`;
                        }
                    } else if (parsedMessage.type === 'agent_log') {
                        messageText = parsedMessage.message || '';
                    }

                    if (messageText) {
                        setMessages(prevMessages => [
                            ...prevMessages, 
                            { message: messageText, person: 1 }
                        ]);
                        scrollToBottom();
                    }

                    lastMessageId = parsedMessage.message_id; // Update the last message ID
                });

                setGlobalMessageId(lastMessageId); // Store the last message ID globally

                // Wait 5 seconds before sending user choice
                await sleep(5000);

                const randomUuid = uuidv4();
                const functionSelectionPayload = {
                    payload: {
                        message_id: randomUuid,
                        referral_id: lastMessageId,
                        type: "user_json",
                        user_json: {
                            type: "task_list",
                            selection: 0,
                        },
                        session_id: sessionId,
                    }
                };

                // Add the user choice message as person 0
                setMessages(prevMessages => [
                    ...prevMessages,
                    { message: "User selected: Quiz Agent", person: 0 }
                ]);
                scrollToBottom();

                try {
                    const response1 = await axios.post('http://localhost:5000/api/send_user_choice', functionSelectionPayload);
                    console.log('Choice submission response:', response1.data);

                    // Wait 10 seconds before fetching new messages
                    await sleep(10000);

                    // Fetch new messages after submitting user choice
                    const response2 = await axios.get('http://localhost:5000/api/get_messages2', {
                        params: {
                            session_id: sessionId,
                            last_message_id: lastMessageId, // Use the correct last message ID here
                        }
                    });

                    console.log('Fetched messages after user choice:', response2.data);

                    const fetchedMessages = response2.data.agent_response.map(res => {
                        const parsedMessage = JSON.parse(res);
                        let messageText = parsedMessage.agent_info || parsedMessage.agent_json?.text || parsedMessage.message || 'No content';
                        
                        const options = parsedMessage.agent_json?.options || [];
                        const formattedOptions = options.length
                            ? options.map(opt => `${opt.key}: ${opt.value}`).join('\n')
                            : '';

                        if (formattedOptions) {
                            messageText += `\nOptions:\n${formattedOptions}`;
                        }

                        return {
                            message: messageText,
                            options: options,
                            person: 1 // Received messages are person 1
                        };
                    });

                    setMessages(prevMessages => [
                        ...prevMessages,
                        ...fetchedMessages
                    ]);
                    setActive(true);
                    scrollToBottom();

                } catch (error) {
                    console.error('Error sending user choice:', error);
                }
            }

        } catch (error) {
            console.error('Error fetching messages:', error);
        }

    } catch (error) {
        console.error("Error starting session or submitting objective:", error);
        setError(error.message);
    }
}

async function submitHandler(e) {
  e.preventDefault();
  const input = inputRef.current.value.trim();
  inputRef.current.value = "";

  if (!sessionId) {
      console.error("Session not initialized.");
      return;
  }

  setActive(false);

  try {
      const lastMessageId = globalMessageId;
      console.log("Initial lastMessageId:", lastMessageId);

      // First GET request: Fetch the latest messages, but don't display them yet
      const firstResponse = await axios.get('http://localhost:5000/api/get_messages2', {
          params: { session_id: sessionId, last_message_id: lastMessageId }
      });

      console.log("First API Response:", firstResponse.data);

      const { agent_response: initialAgentResponse } = firstResponse.data;
      if (initialAgentResponse && Array.isArray(initialAgentResponse) && initialAgentResponse.length) {
          // Process the messages but do not display them
          const formattedMessages = initialAgentResponse.map(res => {
              try {
                  const parsedMessage = JSON.parse(res);
                  return {
                      message_id: parsedMessage.message_id,
                      type: parsedMessage.type,
                      text: parsedMessage.agent_json?.text || parsedMessage.agent_message || parsedMessage.message || '',
                      options: parsedMessage.agent_json?.options || [],
                      contextArgs: parsedMessage.agent_json?.context_json?.args || null,
                  };
              } catch (error) {
                  console.error("Error parsing message:", res, error);
                  return null;
              }
          }).filter(msg => msg !== null);

          if (formattedMessages.length) {
              const latestMessage = formattedMessages[formattedMessages.length - 1];
              const { message_id, type, options, contextArgs } = latestMessage;

              // Update global message ID
              setGlobalMessageId(message_id);
              console.log("Updated globalMessageId:", message_id);

              // Now handle user input based on the latest message received
              if (input) {
                  if (type === 'agent_json' && options.length > 0) {
                      const inputAsNumber = Number(input); // Convert input to number if possible
                      console.log("User input:", input);
                      console.log("Available options:", options);

                      const userChoice = options.find(opt => {
                          const key = typeof opt.key === 'number' ? Number(opt.key) : opt.key;
                          console.log(`Comparing input (${input}) with option key (${key})`);
                          return key === input || key === inputAsNumber;
                      });

                      if (userChoice) {
                          setMessages(prevMessages => [...prevMessages, { message: `User selected: ${userChoice.value}`, options: [], person: 0 }]);
                          scrollToBottom();

                          await axios.post('http://localhost:5000/api/send_user_choice2', {
                              payload: {
                                  message_id: uuidv4(),
                                  referral_id: message_id,
                                  type: "user_json",
                                  user_json: {
                                      type: "options",
                                      selection: userChoice.key,
                                  },
                                  session_id: sessionId,
                              }
                          });
                          console.log("User choice sent.");
                      } else {
                          console.error("Invalid choice. Available options:", options);
                      }

                  } else if (type === 'agent_message') {
                      const userMessage = input;

                      if (userMessage) {
                          setMessages(prevMessages => [...prevMessages, { message: userMessage, options: [], person: 0 }]);
                          scrollToBottom();

                          await axios.post('http://localhost:5000/api/send_user_message', {
                              payload: {
                                  message_id: uuidv4(),
                                  referral_id: message_id,
                                  type: "user_message",
                                  user_message: userMessage,
                                  session_id: sessionId,
                              }
                          });
                          console.log("User message sent.");
                      }
                  }
              }

              // Second GET request: Fetch the latest messages and display them
              await sleep(10000); // Optional delay before the second request

              const secondResponse = await axios.get('http://localhost:5000/api/get_messages2', {
                  params: { session_id: sessionId, last_message_id: message_id }
              });

              console.log("Second API Response:", secondResponse.data);

              const { agent_response: finalAgentResponse } = secondResponse.data;
              if (finalAgentResponse && Array.isArray(finalAgentResponse) && finalAgentResponse.length) {
                  // Process and display the final messages
                  finalAgentResponse.forEach(res => {
                      try {
                          const parsedMessage = JSON.parse(res);
                          const displayMessage = {
                              message_id: parsedMessage.message_id,
                              type: parsedMessage.type,
                              text: parsedMessage.agent_json?.text || parsedMessage.agent_message || parsedMessage.message || '',
                              options: parsedMessage.agent_json?.options || [],
                              contextArgs: parsedMessage.agent_json?.context_json?.args || null,
                          };

                          // Check if the message has contextArgs and display only the answer
                          if (displayMessage.contextArgs && displayMessage.contextArgs.answer) {
                              setMessages(prevMessages => [...prevMessages, { message: displayMessage.contextArgs.answer, options: [], person: 1 }]);
                              scrollToBottom();
                          } else {
                              // Otherwise, display the full text and options if available
                              setMessages(prevMessages => [...prevMessages, { message: displayMessage.text, options: displayMessage.options, person: 1 }]);
                              scrollToBottom();

                              // If the message has options, display them as well
                              if (displayMessage.options.length > 0) {
                                  const formattedOptions = displayMessage.options.map(opt => `${opt.key}: ${opt.value}`).join('\n');
                                  setMessages(prevMessages => [...prevMessages, { message: `Please select an option:\n${formattedOptions}`, options: [], person: 1 }]);
                                  scrollToBottom();
                              }
                          }

                      } catch (error) {
                          console.error("Error parsing message:", res, error);
                      }
                  });
              }
          } else {
              console.log("No new messages.");
          }
      } else {
          console.error("Invalid response data format:", firstResponse.data);
      }

  } catch (error) {
      console.error("Error submitting objective or getting messages:", error);
  } finally {
      setActive(true);
  }
}

  async function handleContinueDialogue() {
    const input = 'Continue dialogue';
    inputRef.current.value = input;
    await submitHandler({ preventDefault: () => {} }); // Simulate form submission
  }

  async function handleEndDialogue() {
    const input = 'End dialogue';
    inputRef.current.value = input;
    await submitHandler({ preventDefault: () => {} });
  }
  

  return (
    <div>
      <Chat messages={messages} setMessages={setMessages} inputRef={inputRef} submitHandler={submitHandler} active={active} onContinueDialogue={handleContinueDialogue} onEndDialogue={handleEndDialogue} sessionId={sessionId} startSession={startSession} setSessionId={setSessionId} learn={false}/>
    </div>
  );
}

export default function Learn() {
  return (
    <div>
      <Routes>
        <Route path="/About" element={<About />} />
        <Route path="/" element={<Interface />} />
      </Routes>
    </div>
  );
}
