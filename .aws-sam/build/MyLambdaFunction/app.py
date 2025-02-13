import json
import boto3
import os

# Inicialización del cliente
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ['AWS_REGION'])
model_id = os.environ['MODEL_ID']

def lambda_handler(event, context):
    # Validación de la entrada
    if 'body' not in event or not event['body']:
        return {
            'statusCode': 400,
            'body': "Error: No input provided."
        }
    
    #Entrada del usuario
    user_input = event['body']

    # Llamada a Bedrock
    try:
        kwargs = {
            "modelId": model_id,
            "contentType": "application/json",
            "accept": "*/*",
            "body": json.dumps(
                {
                    "inputText": user_input
                }
            )
        }

        response = bedrock_runtime.invoke_model(**kwargs)

        #Respuesta de Bedrock
        bedrock_output = json.loads(response['body'].read().decode('utf-8'))

        #Texto generado
        generated_text = bedrock_output['results'][0]['outputText']

        return {
            'statusCode': 200,
            'body': f"Received from Titan Lite: {generated_text}"
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }