import json
import os
import requests
import time



def get_config_dict():
    filename = "config.json"
    if os.path.exists(filename):
        try:
            with open(filename,"r") as file:
                return json.load(file)
        except Exception as e:
            raise Exception("{} could be corrupted\nError Message: {e}".format(filename,))
    else:
        raise Exception("{} is missing".format(filename))

TELEGRAM_BOT_TOKEN = get_config_dict().get("TELEGRAM_BOT_TOKEN","")
TELEGRAM_BOT_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
CONGFIG_FILENAME = "config.json"

EXCHANGE_RATE_API_KEY = get_config_dict().get("EXCHANGE_RATE_API_KEY","")
 

last_update_id = 0

def get_updates():
    """Get recent and unprocessed updates  no longer than 24hours old from bot server"""  
    if TELEGRAM_BOT_TOKEN:
        try:
            response = requests.get(f"{TELEGRAM_BOT_API_URL}/getUpdates?offset={last_update_id + 1}")
            if response.status_code == 200:
                return response.json()
            elif 400>=response.status_code<500:
                raise Exception("Client Error: Make to save a valid key in config.json file and the file must be in same directory as the script ")
            elif response.status_code >=500:
                raise Exception("Server Error: Unable to connect to bot Server")
            else:
                raise Exception(f"Something went Wrong. Error Message: {response.status_code}")
        except Exception as e:
            print(f"Something went wrong. Check your Internet Connection. Error Message: {e}")


def handle_updates(updates):
    """Main Point Where the updates obtained from the bot server undergoes processing-handled effectively"""
    global last_update_id
    if updates:     
        for update in updates.get("result", []):
            if update:
                last_update_id = update.get("update_id", last_update_id)
                chat_id = update.get("message", "").get("chat","").get("id","")
                username = update.get("message", {}).get("from", {}).get("username", "")
                received_text = update.get("message","").get("text","")
                print(f"\n{received_text.lower()}\n")
                if "/start" in received_text.lower() or "start" in received_text.lower():
                    start_command_handler(chat_id,username)
                elif "/help" in received_text.lower() or "help" in received_text.lower():
                    help_command_handler(chat_id)
                elif "/currencysupported" in received_text.lower() or "currencysupported" in received_text.lower():
                    currencysupported_command_handler(chat_id)
                elif "/showrate" in received_text.lower() or "showrate" in received_text.lower():
                    showrate_command_handler(chat_id,received_text)
                elif "/convert" in received_text.lower() or "convert" in received_text.lower():
                    convert_command_handler(chat_id,received_text)
                else:
                    message = f"Option not implemented or Invalid command"
                    send_error_message(chat_id,message)
  


def start_command_handler(chat_id,username):
    """Executes when the /start command is sent by the user and handles any associated data"""
    welcome_message = "Hello Welcome to CurrencyXBot"
    payload = {
        "chat_id":chat_id,
        "text":welcome_message
    }
    
    put_post_request_sendMessage(chat_id,payload)
    time.sleep(1), print(f"woke from 1 second sleep")
    help_command_handler(chat_id)

def help_command_handler(chat_id):
    """Executes When the user sends /help command and displays necessary info"""
    help_message = (
    "💱 *CurrencyXchange Bot Help*\n\n"
    "🌟 *Features:*\n"
    "• Convert between over 150 international currencies in real-time.\n\n"
    "📌 *How to Use:*\n"
    "• Just send a message in this format:\n"
    "`convert <amount> <base_currency_code> to <target_currency_code>`\n\n"
    "🧾 *Example:*\n"
    "`convert 100 USD to GHS`\n\n"
    "_Note: The command works with or without the `/` prefix, but spacing is important._"
    )
    payload = {
        "chat_id":chat_id,
        "text":help_message,
        "parse_mode": "Markdown"  # Allow bold header
    }
    put_post_request_sendMessage(chat_id, payload)

def currencysupported_command_handler(chat_id):
    """Displays a list of all the 150 currencies whose conversions are supported"""
    filename = "currency_codes.json"
    if os.path.exists(filename):
        try:
            with open(filename, "r") as file:
                currency_data = json.load(file)

                # Sort the currency codes alphabetically
                sorted_currency_items = sorted(currency_data.items())

                # Format in groups of 3 per line for better readability
                formatted_lines = []
                line = "code - name\n"
                for i, (code, name) in enumerate(sorted_currency_items, start=1):
                    line += f"{code} - {name}\n"
                    # if i % 3 == 0:
                    #     formatted_lines.append(line.strip())
                    #     line = ""
                if line:  # Add remaining line if any
                    formatted_lines.append(line)

                # Join all lines into the final message
                formatted_text = "*💱 Supported Currencies:*\n\n" + "\n".join(formatted_lines)

                payload = {
                    "chat_id": chat_id,
                    "text": formatted_text,
                    "parse_mode": "Markdown"  # Allow bold header
                }
                put_post_request_sendMessage(chat_id,payload)
        except:
            raise Exception(f"{filename} could be corrupted")
    else:
        raise Exception(f"{filename} is missing or does not exist")
    
def showrate_command_handler(chat_id,received_text):
    """handles  the showrate command from the bot interface from the user
    """
    # showrate <base_currency_code> to <target_currency_code>
    try:
        _,base_currency_code,_,target_currency_code = received_text.split(" ")
        conversion_rate = request_conversion_rate(base_currency_code,target_currency_code)
        if conversion_rate:
            conversion_rate_message = f"1 {base_currency_code.upper()} is equivalent to {conversion_rate} {target_currency_code.upper()}"
        
            payload = {
                "chat_id":chat_id,
                "text":conversion_rate_message
            }
            put_post_request_sendMessage(chat_id, payload)
            print(f"showrate handled successfully for chat id:{chat_id}")
        else:
            error_message = f"unknown-code"
            send_error_message(chat_id,error_message)
    except ValueError:
        message = f"Invalid request format.\nCorrect format: `showrate <base_currency_code> to <target_currency_code>`"
        send_error_message(chat_id,message)
    except Exception as e:
        message = f"Unknown Error. Please check to see if everything is in order-Internet Connectivity Maybe."
        send_error_message(chat_id,message)

def request_conversion_rate(base_currency_code,target_currency_code):
        """Puts a GET request to ExchangeRate-API  and returns the minimum conversion rate of one currency to the other"""
        headers = {
                  "content-type":"application/json",
                  "accept":"application/json",
                  "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
            }
        
        EXCHANGE_RATE_API_URL =f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/pair/{base_currency_code.upper()}/{target_currency_code.upper()}"
        if EXCHANGE_RATE_API_KEY:
            try:
                response = requests.get(EXCHANGE_RATE_API_URL, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("conversion_rate", "") if data.get("result","")=="success" else ""
                elif 400>=response.status_code<500:
                    raise Exception("Client Error: Make to save a valid key for ExchangeRate-API in config.json file and the file must be in same directory as the script ")
                elif response.status_code >=500:
                    raise Exception("Server Error: Unable to connect to bot Server")
                else:
                    raise Exception(f"Something went Wrong. Error Message: {response.status_code}")
            except Exception as e:
                raise(f"Something went wrong. Check your Server Connection to Internet. Error Message: {e}")

def convert_command_handler(chat_id,received_text):
    """Handles the convert command entered by the user in the bot interface"""
    # convert <amount> <base_currency_code> to <target_currency_code>
    try:
        _,amount,base_currency_code,_,target_currency_code = received_text.split(" ")
        conversion = request_conversion(base_currency_code,target_currency_code,amount)
        if conversion:
            conversion_message = f"{amount} {base_currency_code.upper()} is equivalent to {conversion} {target_currency_code.upper()}"
        
            payload = {
                "chat_id":chat_id,
                "text":conversion_message
            }
            put_post_request_sendMessage(chat_id, payload)
            print(f"convert handled successfully for chat id:{chat_id}")
        else:
            error_message = f"unknown-code or Invalid amount"
            send_error_message(chat_id,error_message)
    except ValueError:
        message = f"Invalid request format.\nCorrect format: `convert <amount> <base_currency_code> to <target_currency_code>`"
        send_error_message(chat_id,message)
    except Exception as e:
        message = f"Unknown Error. Please check to see if everything is inorder"
        send_error_message(chat_id,message)

def request_conversion(base_currency_code,target_currency_code,amount):
    """Puts a GET request for the conversion of sepcified amount from one currency to the other"""
    headers = {
                  "content-type":"application/json",
                  "accept":"application/json",
                  "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36 Edg/136.0.0.0"
            }
        
    EXCHANGE_RATE_API_URL =f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API_KEY}/pair/{base_currency_code.upper()}/{target_currency_code.upper()}/{amount}"
    if EXCHANGE_RATE_API_KEY:
        try:
            response = requests.get(EXCHANGE_RATE_API_URL, headers=headers)
            if response.status_code == 200:
                data = response.json()
                return data.get("conversion_result", "") if data.get("result","")=="success" else ""
            elif 400>=response.status_code<500:
                raise Exception("Client Error: Make to save a valid key for ExchangeRate-API in config.json file and the file must be in same directory as the script ")
            elif response.status_code >=500:
                raise Exception("Server Error: Unable to connect to bot Server")
            else:
                raise Exception(f"Something went Wrong. Error Message: {response.status_code}")
        except Exception as e:
            raise Exception(f"Something went wrong. Check your Internet Connection. Error Message: {e}")
    show_politeness()

def put_post_request_sendMessage(chat_id, payload):
    """Made generic to handle POST request to the bot server to the user"""
    try:
        response = requests.post(f"{TELEGRAM_BOT_API_URL}/sendMessage", json=payload)
        if response.status_code == 200:
            print(f"\nMessage sent to chat id: {chat_id}")
    except Exception as e:
        print(f"\nError Sending message to chat id {chat_id}. Error Message : {e}")
    show_politeness("woke from 1 second sleep after post request")


def send_error_message(chat_id, message):
    """Handles the sending of error message to the bot server to the user end"""
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"  # Allow bold header
    }
    put_post_request_sendMessage(chat_id,payload)
    show_politeness("woke from 1 second sleep after sending error message")

def show_politeness(message="Woke from 1 second sleep"):
    """Prevents spamming on the bot server"""
    time.sleep(1), print(f"{message}")



def main():
    """CurrencyXBot Script Entry Point"""
    print(f"(=:----------Starting CurrecnyXBot---------- :=)")
    while True:
        updates = get_updates()
        handle_updates(updates)
        show_politeness()

if __name__ == "__main__":
    main()