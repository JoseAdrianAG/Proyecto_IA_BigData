# aws sts get-caller-identity --profile adrian
# aws sso login --profile adrian
# rm ~/.aws/config para borrar fichero de configuración
import boto3

session = boto3.Session(profile_name='adrian')
bedrock = session.client('bedrock')
response = bedrock.list_foundation_models()
models = response['modelSummaries']
print(f'{len(models)} available models.')
for model in models:
    print(f'- {model["modelId"]}')
