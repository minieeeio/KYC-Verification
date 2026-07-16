from robot.libraries.BuiltIn import BuiltIn
import os


class QREnv:

    BOT_NAME = 'QRBot'             # Name of the bot. Will be used in email notifications
    
    PLATFORM_VERSION = 2            # v1 currently in NCell, Prime, Civil, NMB. Rest are on v2     
    NO_PLATFORM = True
    
    IDENTIFIER = os.environ.get("identifier")                             # For platform v2
    
    VERIFY_SSL = False
    DEBUG = True
    
    BASE_DIR = os.environ.get("ROBOT_ROOT")                                     
    ARTIFACT_DIR = os.environ.get("ROBOT_ARTIFACTS")                           # Default to output directory
    DEFAULT_STORAGE_LOCATION = os.path.join(BASE_DIR, 'storage_downloads')     # Downloaded files from storage bucket will be stored here

    
    # ENVIRONMENTS - Should be retrieved dynamically from django env
    ENV_LOCAL = "LOCAL"             # Use for locahost
    ENV_QR_DEV = "QR_DEV"           # Use for internal dev server
    ENV_QR_UAT = "QR_UAT"           # Use for internal uat server
    ENV_UAT = "UAT"                 # Use for client uat server
    ENV_PRODUCTION = "PRODUCTION"   # Use for client production

    # Platform URLS
    URL_LOCAL = "http://127.0.0.1:8000/api/v1"                  # Use for locahost
    URL_QR_DEV_URL = "http://13.58.117.7:8000/api/v1"           # Use for internal dev server                            
    URL_QR_UAT_URL = "http://18.217.209.236/api/v1"             # Use for internal uat server                                 
    URL_UAT_URL = ""                                            # Use for client uat server
    URL_PROD = ""                                               # Use for client production

    # Dictiory to pick Platform URL based on current Environment
    ENV_URL = {
        ENV_LOCAL: URL_LOCAL,
        ENV_QR_DEV: URL_QR_DEV_URL,
        ENV_QR_UAT: URL_QR_UAT_URL,
        ENV_UAT: URL_UAT_URL,
        ENV_PRODUCTION: URL_PROD
    }

    # ENVIRONMENT = os.environ.get("ENVIRONMENT")
    ENVIRONMENT = ENV_UAT
    
    try:
        BASE_URL = ENV_URL[ENVIRONMENT]
    except Exception as e:
        BASE_URL = URL_LOCAL


    # Set required vaults, queues and storage buckets
    # Vault items are fetched. However, queues and storage buckets are only checked if they are accessible
    QUEUE_NAMES = []
    STORAGE_NAMES = []
    VAULT_NAMES = ["qrbot_vault"]

    # Retrieved vault items are set in this dictionary
    VAULTS = {}


