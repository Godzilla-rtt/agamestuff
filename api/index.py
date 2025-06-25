

app = Flask(__name__)
Expand
Metro's Backend.py
6 KB
import requests
import random
from flask import Flask, jsonify, request

class GameInfo:
    def __init__(self):
        self.TitleId : str = "1A52F7"
        self.SecretKey : str = "R7CG6TBBSJQ4MO4PPUPQTFGGTXEB44R6YCS5N5YENSRQIASR5K"
        self.ApiKey : str = "OC|29238831412382524|03eed8dfc563290fd8656adc7448c3e7"

    def get_auth_headers(self):
        return {
            "content-type": "application/json",
            "X-SecretKey": self.SecretKey
        }

settings = GameInfo()
app = Flask(__name__)
playfab_cache = {}
mute_cache = {}

def return_function_json(data, funcname, funcparam={}):
    user_id = data["FunctionParameter"]["CallerEntityProfile"]["Lineage"]["TitlePlayerAccountId"]

    response = requests.post(
        url=f"https://{settings.TitleId}.playfabapi.com/Server/ExecuteCloudScript",
        json={
            "PlayFabId": user_id,
            "FunctionName": funcname,
            "FunctionParameter": funcparam
        },
        headers=settings.get_auth_headers()
    )

    if response.status_code == 200:
        return jsonify(response.json().get("data").get("FunctionResult")), response.status_code
    else:
        return jsonify({}), response.status_code

def get_is_nonce_valid(nonce, oculus_id):
    response = requests.post(
        url=f'https://graph.oculus.com/user_nonce_validate?nonce={nonce}&user_id={oculus_id}&access_token={settings.ApiKey}',
        url1=f'https://graph.oculus.com/user_nonce_validate?nonce={nonce}&user_id={oculus_id}&access_token={settings.ApiKey1}',
        headers={"content-type": "application/json"}
    )
    return response.json().get("is_valid")

@app.route("/", methods=["POST", "GET"])
def main():
    return "Service is running"

@app.route("/api/PlayFabAuthentication", methods=["POST"])
def playfab_authentication():
    rjson = request.get_json()
    required_fields = ["CustomId", "Nonce", "AppId", "Platform", "OculusId"]
    missing_fields = [field for field in required_fields if not rjson.get(field)]

    if missing_fields:
        return jsonify({
            "Message": f"Missing parameter(s): {', '.join(missing_fields)}",
            "Error": f"BadRequest-No{missing_fields[0]}"
        }), 400

    if rjson.get("AppId") != settings.TitleId:
        return jsonify({
            "Message": "Request sent for the wrong App ID",
            "Error": "BadRequest-AppIdMismatch"
        }), 400

    if not rjson.get("CustomId").startswith(("OC", "PI")):
        return jsonify({
            "Message": "Bad request",
            "Error": "BadRequest-NoOCorPIPrefix"
        }), 400

    url = f"https://{settings.TitleId}.playfabapi.com/Server/LoginWithServerCustomId"
    login_request = requests.post(
        url=url,
        json={
            "ServerCustomId": rjson.get("CustomId"),
            "CreateAccount": True
        },
        headers=settings.get_auth_headers()
    )

    if login_request.status_code == 200:
        data = login_request.json().get("data")
        session_ticket = data.get("SessionTicket")
        entity_token = data.get("EntityToken").get("EntityToken")
        playfab_id = data.get("PlayFabId")
        entity_type = data.get("EntityToken").get("Entity").get("Type")
        entity_id = data.get("EntityToken").get("Entity").get("Id")

        link_response = requests.post(
            url=f"https://{settings.TitleId}.playfabapi.com/Server/LinkServerCustomId",
            json={
                "ForceLink": True,
                "PlayFabId": playfab_id,
                "ServerCustomId": rjson.get("CustomId"),
            },
... (145 lines left)
