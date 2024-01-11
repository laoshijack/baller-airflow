# Parse YAML, run local executor 

import os
import re
import yaml
import time
import subprocess

path = os.getenv('YAML_PATH')

def parse_config(path=path, data=None, tag='!ENV'):

    # pattern for global vars: look for ${word}
    pattern = re.compile('.*?\${(\w+)}.*?')
    loader = yaml.SafeLoader

    # the tag will be used to mark where to start searching for the pattern
    # e.g. somekey: !ENV somestring${MYENVVAR}blah blah blah
    loader.add_implicit_resolver(tag, pattern, None)

    def constructor_env_variables(loader, node):

        value = loader.construct_scalar(node)
        match = pattern.findall(value)  # to find all env variables in line
        if match:
            full_value = value
            for g in match:
                full_value = full_value.replace(
                    f'${{{g}}}', os.environ.get(g, g)
                )
            return full_value
        return value

    loader.add_constructor(tag, constructor_env_variables)

    if path:
        with open(path) as conf_data:
            return yaml.load(conf_data, Loader=loader)
    elif data:
        return yaml.load(data, Loader=loader)
    else:
        raise ValueError('Either a path or data should be defined as input')

fname = 'parse_executor.py'

if __name__ == "__main__":
    with open('docker-compose-LocalExecutor-keys.yml', 'w') as file:
        yaml.dump(parse_config(), file)
        dn = os.path.abspath(fname)
        f_path =dn.replace(fname,'')
        print(f_path)
        print('\nPaste this into Terminal:\n\n',f"docker-compose -f \"{f_path}docker-compose-LocalExecutor-keys.yml\" up -d")

        print('\n Once Docker is up and running configure mysql_conn connection in Admin --> Connections')
        print('\n Conn Id = mysqlconn\nConn Type = MySQL\nHost = mysql\nSchema = mysql\nLogin = root\n Password = {YOUR ROOT PASSWORD}')

