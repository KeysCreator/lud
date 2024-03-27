import os
import requests

# Install requests if not already installed
try:
    import requests
except ImportError:
    print("Requests library not found. Installing...")
    os.system('pip install requests')

# Now that requests is installed, import it again
import requests

def send_request():
    url = "https://discord.com/"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Request sent successfully to", url)
        else:
            print("Failed to send request. Status code:", response.status_code)
    except Exception as e:
        print("An error occurred:", str(e))

if __name__ == "__main__":
    send_request()
