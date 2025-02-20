import json
import boto3
from funciones import analyze_pdf_with_textract, analyze_pdf_from_s3_with_textract, load_contacts_from_local, load_contacts_from_s3

# Inicialización del cliente
bedrock_runtime = boto3.client('bedrock-runtime', region_name='eu-central-1')
model_id = 'amazon.titan-text-lite-v1'

BUCKET_NAME = 'pruebas-miguel-aws'
FILE_NAME = 'correosNFQ.pdf'
    
def lambda_handler(event, context):
    # Validación de la entrada
    if 'body' not in event or not event['body']:
        return {
            'statusCode': 400,
            'body': "Error: No input provided."
        }
    
    #Entrada del usuario
    user_input = event['body']

    #Obtener los datos de los contactos
    contacts = analyze_pdf_with_textract(FILE_NAME)
    '''
    contacts = read_pdf_from_s3(BUCKET_NAME, FILE_NAME)
    contacts = load_contacts_from_local(FILE_NAME)
    contacts = load_contacts_from_s3(FILE_NAME)
    '''

    # Llamada a Bedrock
    prompt = (
        f'El usuario tiene la siguiente pregunta: {user_input}.\n'
        'Para poder contestarla necesito que leas y analices el siguiente documento. '
        'En el documento obtendrás todos los correos y sus respectivos servicios de la empresa.'
        f"\n{(contacts)}\n"
        'A continuación encontrarás entre "****************" varios ejemplos que debes tomar de referencia para tu proceso de lógica y la forma en la que debes responder.\n'
        '******************************************************************************************\n'
        'Pregunta: "¿Cuántos días de vacaciones me quedan este año?"\n'
        'Respuesta: "se@nfq.es"\n'
        'Pregunta: "¿A qué correo debo escribir si quiero irme de viaje por trabajo?"\n'
        'Respuesta: "viajes@nfq.es"\n'
        'Pregunta: "¿Dónde puedo pedir información sobre un curso de marketing?"\n'
        'Respuesta: "formacion@nfq.es"\n'
        'Pregunta: "No puedo acceder a mi correo corporativo, ¿me pueden ayudar?"\n'
        'Respuesta: "it@nfq.es"\n'
        'Pregunta: "¿Cuántos días de vacaciones me quedan este año?"\n'
        'Respuesta: "se@nfq.es"\n'
        'Pregunta: "Voy a empezar un nuevo proyecto y necesito un portátil, ¿cómo solicito uno?"\n'
        'Respuesta: "soportelogistico@nfq.es"\n'
        'Pregunta: "¿Cuándo es la próxima convocatoria para la certificación en AWS?"\n'
        'Respuesta: "formacion@nfq.es"\n'
        '******************************************************************************************\n'
        'Ahora devuelve el correo más relevante y adecuado para solucionar la pregunta del usuario como en los ejemplos. Sin más texto ni ningún carácter de por medio, únicamente el correo que solucione el problema del usuario, nada más.'
    )

    #Comprobamos si el prompt se manda de forma correcta antes de invocar al modelo
    print(prompt)
    avance = input('¿Seguir? (y/n):\n')
    while avance.lower() not in ['y', 'n']:
        avance = input('¿Seguir? (y/n):\n')
    if avance.lower() == 'n':
        return
    else:
        try:
            kwargs = {
                "modelId": model_id,
                "contentType": "application/json",
                "accept": "*/*",
                "body": json.dumps(
                    {
                        "inputText": prompt,
                        "textGenerationConfig":{
                            "temperature":0.1,
                            "topP":0.9
                        }
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
                'body': f"Correo al que debe escribir: {generated_text}"
            }

        except Exception as e:
            return {
                'statusCode': 500,
                'body': f"Error: {str(e)}"
            }
    
# Prueba en local
if __name__ == "__main__":
    event = {
        "body": "Quiero cambiar mi cuenta de banco a la que quiero que me den mi nómina, ¿a quién debería solicitarle el cambio?"
    }
    response = lambda_handler(event, None)
    print(response)