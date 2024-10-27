import requests
import json
# Function to handle POST requests
def post_request(url, json_data, headers):
    response = requests.post(url, json=json_data, headers=headers)
    return response
# Function to handle GET requests
def get_request(url, headers):
    response = requests.get(url, headers=headers)
    return response
# Objective response
def extract_message_id_and_format_response(response):
    # Extract and parse the JSON string
    response_str = response['agent_response'][0]
    response_data = json.loads(response_str)
    # Extract the message_id
    message_id = response_data['message_id']
    # Extract the text and options
    text = response_data['agent_json']['text']
    options = response_data['agent_json']['options']
    # Create the formatted output
    output = text + "\n"
    for option in options:
        output += f"{option['key']} : {option['value']}\n"
    return message_id, output.strip()
def stop_session(session_id, token):
    data = {"payload": {"type": "stop"}}
    response = post_request(f"https://agentverse.ai/v1beta1/engine/chat/sessions/{session_id}/submit", data, {"Authorization": token})
    print("Session stopped:", response.json())
# Functions to interact with the AI-Engine
def send_user_choice_as_uuid(session_id, message_id, referral_id,user_choice, token):
    data = {
        "payload": {
            "message_id": message_id,
            "referral_id": referral_id,
            "type": "user_json",
            "user_json": {
                "type": "options",
                "selection": [user_choice]
                },
            "session_id": session_id
        }
    }
    return post_request(f"https://agentverse.ai/v1beta1/engine/chat/sessions/{session_id}/submit", data, {"Authorization": token})
def send_user_choice_as_task(session_id, message_id, referral_id,user_choice, token):
    data = {
        "payload": {
            "message_id": message_id,
            "referral_id": referral_id,
            "type": "user_json",
            "user_json": {
                "type": "task_list",
                "selection": [user_choice]
                },
            "session_id": session_id
        }
    }
    return post_request(f"https://agentverse.ai/v1beta1/engine/chat/sessions/{session_id}/submit", data, {"Authorization": token})
def send_user_message(session_id, message_id, referral_id, user_message, token):
    data = {
        "payload": {
            "message_id": message_id,
            "referral_id": referral_id,
            "type": "user_message",
            "user_message": str(user_message)
        },
        "session_id": session_id
    }
    return post_request(f"https://agentverse.ai/v1beta1/engine/chat/sessions/{session_id}/submit", data, {"Authorization": token})