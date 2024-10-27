from flask import Flask, request, jsonify
import os
import json
import uuid
from functions_chat import post_request, get_request, extract_message_id_and_format_response, send_user_choice_as_uuid, send_user_message, send_user_choice_as_task
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
api_key = os.getenv("AIENGINE_KEY")
token = f'Bearer {api_key}'
email=os.getenv("EMAIL")
functionGroup=os.getenv("FUNCTIONGROUP")


@app.route('/api/start_session', methods=['POST'])
def start_session():
    #data = request.json
    session_creation_payload = {
        "email": email,
        "requestedModel": "next-gen",
        "functionGroup": functionGroup
    }
    print(session_creation_payload)
    response = post_request("https://agentverse.ai/v1beta1/engine/chat/sessions", session_creation_payload, {"Authorization": token})
    return jsonify(response.json())

@app.route('/api/submit_objective', methods=['POST'])
def submit_objective():
    data = request.json
    objective_payload = {
        "payload": {
            "type": "start",
            "objective": data['objective'],
            "context": data['context'],
            "session_id": data['session_id']
        }
    }
    response = post_request(f"https://agentverse.ai/v1beta1/engine/chat/sessions/{data['session_id']}/submit", objective_payload, {"Authorization": token})
    return jsonify(response.json())


@app.route('/api/get_messages', methods=['GET'])
def get_messages():
    session_id = request.args.get('session_id')  # Correctly extract query parameter
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    url_template = f"https://agentverse.ai/v1beta1/engine/chat/sessions/{session_id}/new-messages"
    response = get_request(url_template, {"Authorization": token})
    
    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch messages"}), response.status_code
    
    return jsonify(response.json())


@app.route('/api/get_messages2', methods=['GET'])
def get_messages2():
    session_id = request.args.get('session_id')  # Correctly extract query parameter
    last_message_id = request.args.get('last_message_id', '')  # Optional parameter

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    # Construct the URL with the optional last_message_id parameter
    url_template = f"https://agentverse.ai/v1beta1/engine/chat/sessions/{session_id}/new-messages"
    if last_message_id:
        url_template += f"?last_message_id={last_message_id}"

    headers = {"Authorization": token}
    response = get_request(url_template, headers)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch messages"}), response.status_code

    return jsonify(response.json())

@app.route('/api/send_user_choice', methods=['POST'])
def send_user_choice():
    data = request.json
    payload = data['payload']
    print(data)
    response = send_user_choice_as_task(str(payload['session_id']), payload['message_id'], payload['referral_id'], payload['user_json']['selection'], token)
    return jsonify(response.json())

@app.route('/api/send_user_choice2', methods=['POST'])
def send_user_choice2():
    data = request.json
    payload = data['payload']
    print(data)
    response = send_user_choice_as_uuid(str(payload['session_id']), payload['message_id'], payload['referral_id'], payload['user_json']['selection'], token)
    return jsonify(response.json())

@app.route('/api/send_user_message', methods=['POST'])
def send_user_messageb():
    data = request.json
    payload = data['payload']
    print(data)
    response = send_user_message(payload['session_id'], payload['message_id'], payload['referral_id'], str(payload['user_message']), token)
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(debug=True)
