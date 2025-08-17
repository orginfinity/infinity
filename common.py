from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

secrets = {}
secrets["google-search-uri"] = None
secrets["google-fav-icons-uri"] = None
secrets["agent-uri"] = None
secrets["sqlloginpwd"] = None
secrets["google-auth-secret"] = None
secrets["google-client-id"] = None
secrets["chainlit-secret"] = None
secrets["azure-openai-key"] = None

class StatusMsg:
    def __init__(self,command,result):
        self.command = command
        self.result = result

def getKeyValue(secret_name):
    if secret_name not in secrets.keys():
        return None

    if secrets[secret_name] != None:
        return secrets[secret_name]

    key_vault_url = "https://infinity.vault.azure.net/"
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_url, credential=credential)

    try:
        # Retrieve the secret
        retrieved_secret = client.get_secret(secret_name)
        secrets[secret_name] = retrieved_secret.value
        return retrieved_secret.value
    except Exception as e:
        print(e)
        return None
