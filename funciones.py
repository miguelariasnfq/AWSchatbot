import fitz  # PyMuPDF
import json
import boto3
from io import BytesIO

def read_pdf_from_s3(bucket_name, file_name):
    """
    Lee un archivo PDF desde S3 y devuelve su contenido como una cadena UTF-8.
    
    @param bucket_name: Nombre del bucket de S3.
    @param file_name: Nombre del archivo PDF en el bucket de S3.
    :return: Contenido del PDF en formato UTF-8.
    """
    s3 = boto3.client('s3')
    try:
        # Descargar el archivo PDF desde S3
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        pdf_data = response['Body'].read()

        # Abrir el PDF usando fitz (PyMuPDF)
        doc = fitz.open(stream=BytesIO(pdf_data))
        text = "\n".join([page.get_text("text") for page in doc])
        return text

    except Exception as e:
        return f"Error al leer el PDF desde S3: {e}"
    
def read_pdf(pdf_path):
    """
    Lee un archivo PDF y devuelve su contenido como una cadena UTF-8.
    
    :param pdf_path: Ruta al archivo PDF.S
    :return: Contenido del PDF en formato UTF-8.
    """
    try:
        doc = fitz.open(pdf_path)
        text = "\n".join([page.get_text("text") for page in doc])
        return text
    except Exception as e:
        return f"Error al leer el PDF: {e}"

def load_contacts_from_local(LOCAL_FILE):
    '''
    Lee el archivo JSON desde el sistema de archivos local.
    '''
    try:
        with open(LOCAL_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error al leer el JSON local: {str(e)}")
        return []
    
def load_contacts_from_s3(BUCKET_NAME, S3_FILE):
    '''
    Lee el archivo JSON desde S3 y lo convierte en una lista de contactos.
    ''' 
    #Conexión s3
    s3 = boto3.client('s3') 

    try:
        response = s3.get_object(Bucket = BUCKET_NAME, Key = S3_FILE)
        data = response['Body'].read().decode('utf-8')
        return json.loads(data)
    except Exception as e:
        print(f"Error al obtener JSON desde S3: {str(e)}")
        return []