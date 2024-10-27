import os
import json
import time
import uuid
import requests
from functions_chat import post_request, get_request, extract_message_id_and_format_response, stop_session, send_user_choice_as_uuid, send_user_message
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("AIENGINE_KEY")
token = f'Bearer {api_key}'
# Initialize session and user details
session_creation_payload = {
    "email": "kush.patel@fetch.ai",
    "requestedModel": "next-gen",
    "functionGroup": "1fb30610-0698-491a-979c-68c201c09c06"
}
session_creation_response = post_request("https://agentverse.ai/v1beta1/engine/chat/sessions", session_creation_payload, {"Authorization": token})
session_id = session_creation_response.json().get('session_id')
objective = input('Hi Kush. I am REWISE4. How can I assist you?\n')
objective_payload = {
    "payload": {
        "type": "start",
        "objective": objective,
        "context": f"User full Name: Test User\nUser email: {session_creation_payload['email']}\nUser location: latitude=51.5072, longitude=0.1276\n",
        "session_id": session_id
    }
}
post_request(f"https://agentverse.ai/v1beta1/engine/chat/sessions/{session_id}/submit", objective_payload, {"Authorization": token})
time.sleep(10)
objective_get_response = get_request(f"https://agentverse.ai/v1beta1/engine/chat/sessions/{session_id}/new-messages", {"Authorization": token}).json()
message_id, formatted_objective_response = extract_message_id_and_format_response(objective_get_response)
print("Initial message details:", formatted_objective_response)
user_choice = input("Please select the tutor you want: \n")
random_uuid = uuid.uuid4()
function_selection_payload = {
    "payload": {
        "message_id": str(random_uuid),
        "referral_id": message_id,
        "type": "user_json",
        "user_json": {
            "type": "task_list",
            "selection": [user_choice]
        },
        "session_id": session_id
    }
}
response_post_task_selection = post_request(f"https://agentverse.ai/v1beta1/engine/chat/sessions/{session_id}/submit", function_selection_payload, {"Authorization": token})
last_message_id = message_id  # Initialize the last message ID


expecting_user_message = True
while True:
    time.sleep(10)
    url_template = f"https://agentverse.ai/v1beta1/engine/chat/sessions/{session_id}/new-messages?last_message_id={last_message_id}"
    headers = {"Authorization": token}
    response = get_request(url_template, headers).json()
    if 'agent_response' in response and response['agent_response']:
        for message_json in response['agent_response']:
            message = json.loads(message_json)
            current_message_id = message.get('message_id')
            if message.get('type') == 'agent_json' and 'options' in message['agent_json']:
                options_text = message['agent_json'].get('text', 'No text provided.')
                print("Agent JSON:", options_text)
                for option in message['agent_json']['options']:
                    print(f"{option['key']}: {option['value']}")
                user_choice = input("Please select an option by entering the corresponding key: ")
                send_user_choice_as_uuid(session_id, str(uuid.uuid4()), current_message_id, user_choice, token)
                last_message_id = current_message_id
                time.sleep(10)
            elif message.get('type') == 'agent_message':
                print("Agent Message:", message.get('agent_message', 'No specific message provided.'))
                if message.get('agent_message') == 'What message would you like to send to the agent?':
                    user_message = input("Please enter your message: ")
                    send_user_message(session_id, str(uuid.uuid4()), current_message_id, user_message, token)
                else:
                    continue
                last_message_id = current_message_id
                time.sleep(10)











