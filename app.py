import json
import boto3
import os

MODEL_ID = 'amazon.titan-text-lite-v1'
BUCKET_NAME = 'pruebas-miguel-aws'
FILE_NAME = 'correosNFQ.pdf'

# Initialize AWS clients
s3 = boto3.client('s3')
textract = boto3.client('textract')
bedrock_runtime = boto3.client('bedrock-runtime', region_name='eu-central-1')

def analyze_pdf_from_s3_with_textract(bucket_name, file_name):
    '''
    Analiza todo el contenido de un PDF almacenado en un bucket de S3, ya sea imágenes o texto.
    @param bucket_name: Nombre del bucket de S3 donde se encuentra el PDF.
    @param file_name: Clave del objeto (PDF) en el bucket de S3.
    :return Contenido del PDF en utf-8.
    '''
    # Inicializar el cliente de S3
    s3 = boto3.client('s3')

    # Inicializar el cliente de Textract
    textract = boto3.client('textract')

    # Obtener el documento de S3
    response = s3.get_object(Bucket=bucket_name, Key=file_name)
    image_bytes = response['Body'].read()

    # Analizar el documento con Textract
    response = textract.analyze_document(
        Document={'Bytes': image_bytes},
        FeatureTypes=['TABLES', 'FORMS']
    )

    # Extraer la respuesta en texto
    extracted_text = ""
    for block in response['Blocks']:
        if block['BlockType'] == 'LINE':
            extracted_text += block['Text'] + '\n'

    return extracted_text

def lambda_handler(event, context):

    document = analyze_pdf_from_s3_with_textract(BUCKET_NAME, FILE_NAME)

    # Step 3: Summarize the text using AWS Bedrock
    prompt = (f"Summarize the following text in 3-5 sentences:\n\n{document}"
                "Write the summarize of the extracted text in the next line. Just the basic information:")
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
                "modelId": MODEL_ID,
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
            summary = bedrock_output['results'][0]['outputText']
            
            # Step 4: Return the summary
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'summary': f"Resumen generado: {summary}"
                })
            }
        
        except Exception as e:
            # Handle errors
            return {
                'statusCode': 500,
                'body': json.dumps({
                    'error': str(e)
                })
            }
# Prueba en local
if __name__ == "__main__":
    response = lambda_handler(None, None)
    body = json.loads(response['body'])  # Convertir el JSON en un diccionario
    print(body['summary'])  # Acceder correctamente al resumen
