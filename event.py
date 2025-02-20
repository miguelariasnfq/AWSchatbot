import requests
import json

# API Gateway endpoint URL
api_url = "https://n0wo1osmz7.execute-api.eu-central-1.amazonaws.com/dev/ask"

def ask_lambda(question):
    """
    Sends a question to the Lambda function via API Gateway and returns the response.
    """
    try:
        # Prepare the request payload
        payload = {
            "body": question
        }

        # Send the POST request to the API Gateway
        response = requests.post(api_url, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response JSON
            response_data = response.json()
            return response_data.get("body", "No response body found.")
        else:
            return f"Error: {response.status_code} - {response.text}"

    except Exception as e:
        return f"An error occurred: {str(e)}"

def main():
    # Get user input
    user_input = input("Introduce tu mensaje: ")

    # Call the Lambda function and get the response
    response = ask_lambda(user_input)

    # Display the response to the user
    print("\nRespuesta del modelo:")
    print(response)

if __name__ == "__main__":
    main()