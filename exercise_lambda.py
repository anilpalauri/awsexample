import os, traceback, json, configparser, boto3

# Initialize boto3 client at global scope for connection reuse
client = boto3.client('ssm')
env = os.environ['ENV']
path_config = os.environ['APP_CONFIG_PATH']
full_config_path = '/' + env + '/' + path_config
item = None

class RetrieveSSM:
    def __init__(self, config):
        self.config = config

    def get_config(self):
        return self.config

def upload_config(ssm_path):
    
    configuration = configparser.ConfigParser()
    try:
        # Get all parameters for this item
        param_values = client.get_parameters_by_path(
            Path=ssm_path,
            Recursive=False,
            WithDecryption=True
        )

        # Loop through the returned parameters and populate the ConfigParser
        if 'Parameters' in param_values and len(param_values.get('Parameters')) > 0:
            for param in param_values.get('Parameters'):
                param_name = param.get('Name')
                config_values = json.loads(param.get('Value'))
                config_dict = {param_name: config_values}
                print("Found configuration: " + str(config_dict))                
        
                
    except:
        print("Error loading config from SSM.")
        traceback.print_exc()
    finally:
        return configuration

def lambda_handler(event, context):
    global item
    s3client=boto3.client('s3')
    
    if item is None:
        print("Loading config and retrieve SSM values...")
        config = upload_config(full_config_path)
        item = RetrieveSSM(config)

     # Write the data to file and store in S3***********************
    ssmValues=item.get_config() 
    with open("/tmp/user.txt","w") as fn:
        json.dump(ssmValues,fn)
    s3client.upload_file("/tmp/user.txt","parameter-example","users.txt")

    return "RetrieveSSM config is " + str(item.get_config()._sections)