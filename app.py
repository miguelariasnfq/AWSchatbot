import json
import boto3

# Inicialización del cliente
bedrock_runtime = boto3.client('bedrock-runtime', region_name='eu-central-1')
model_id = 'amazon.titan-text-lite-v1'

#Conexión s3
s3 = boto3.client('s3')

BUCKET_NAME = 'pruebas-miguel-aws'
FILE_NAME = 'ragPruebaCorreos.json'

def load_contacts_from_s3():
    '''
    Lee el archivo JSON desde S3 y lo convierte en una lista de contactos.
    ''' 
    try:
        response = s3.get_object(Bucket = BUCKET_NAME, Key = FILE_NAME)
        data = response['Body'].read().decode('utf-8')
        return json.loads(data)
    except Exception as e:
        print(f"Error al obtener JSON desde S3: {str(e)}")
        return []
    
# Nombre del archivo local

def load_contacts_from_local():
    '''
    Lee el archivo JSON desde el sistema de archivos local.
    '''
    try:
        with open(FILE_NAME, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error al leer el JSON local: {str(e)}")
        return []

def lambda_handler(event, context):
    # Validación de la entrada
    if 'body' not in event or not event['body']:
        return {
            'statusCode': 400,
            'body': "Error: No input provided."
        }
    
    #Entrada del usuario
    user_input = event['body']

    #Obtener los datos de s3
    contacts = load_contacts_from_local()

    # Llamada a Bedrock
    prompt = (
        f'El usuario tiene la siguiente pregunta: {user_input}.\n'
        'Para poder contestarla necesito que leas y analices el siguiente documento.'
        'En el documento obtendrás todos los correos y sus respectivos servicios de la empresa.'
        f"{json.dumps(contacts, indent=2)}\n"
        'Devuelve solamente el correo más relevante y adecuado para solucionar la pregunta del usuario.'
    )
    try:
        kwargs = {
            "modelId": model_id,
            "contentType": "application/json",
            "accept": "*/*",
            "body": json.dumps(
                {
                    "inputText": prompt
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
            'body': f"Respuesta generada: {generated_text}"
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': f"Error: {str(e)}"
        }