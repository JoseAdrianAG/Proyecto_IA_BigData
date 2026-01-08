import boto3
import json
from botocore.exceptions import ClientError

def bedrock_invoke(prompt: str):
    # Crear sesión usando tu perfil de AWS
    session = boto3.Session(profile_name='adrian')

    # Cliente del runtime de Bedrock
    client = session.client("bedrock-runtime")

    # Modelo a usar (ejemplo: Amazon Nova Premier)
    model_id = "amazon.nova-micro-v1:0"
    prompt = "Hello World!"
    
    # Cuerpo nativo para el modelo
    payload = {
        "inputText": prompt,
        "textGenerationConfig": {
            "maxTokenCount": 256,
            "temperature": 0.3,
            "topP": 0.9
        }
    }

    try:
        # Enviar la solicitud
        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(payload)
        )

        # Leer body del modelo
        model_output = json.loads(response["body"].read())

        # Extraer texto generado
        output_text = model_output["results"][0]["outputText"]

        return output_text

    except ClientError as e:
        print("Error del cliente AWS:", e)
    except Exception as e:
        print("Error general:", e)

# ------- EJEMPLO DE USO -------
if __name__ == "__main__":
    prompt = "Explica en una línea qué es un programa 'Hello World'."
    respuesta = bedrock_invoke(prompt)
    print("Respuesta del modelo:")
    print(respuesta)
