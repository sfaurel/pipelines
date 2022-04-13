from jinja2 import Template
import re
from git import Repo
import os
import json
from pygments import highlight, lexers, formatters
import glob
NAME = "NAME"
GROUP = "GROUP"
WARN = "\033[1;33"
DEFAULT = "\033[0m"


def get_git_url():
    repo = Repo()
    return repo.remotes.origin.url, None


def get_image_tag():
    repo = Repo()
    tag_name = repo.remotes.origin.url.split(
        "@gitlab.grupoalto.com:altochecks/")[-1].strip('.git')
    return tag_name, None


def get_pipeline_name():
    repo = Repo()
    pipeline_name = repo.remotes.origin.url.split('/')[-1].strip('.git')
    return pipeline_name, NAME


default_values = {
    'PIPELINE_GROUP': lambda: (None, GROUP),
    'PIPELINE_NAME': get_pipeline_name,
    'GIT_URL': get_git_url,
    'NEXUS': lambda: ('nexus.altoalliance.com:8086', None),
    'IMAGEN_TAG': get_image_tag
}

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    template_path = os.path.join(script_dir, 'docker_image.json.j2')

    values = {}
    while(True):
        default, value_type = default_values.get('PIPELINE_GROUP', lambda: (None, None))()
        value = input(f"insert value for PIPELINE_GROUP:\n") or default
        if value:
            group_path = os.path.join(script_dir, value)
            values['PIPELINE_GROUP'] = value
            break
        else:
            if default:
                group_path = os.path.join(script_dir, value)
                values['PIPELINE_GROUP'] = default
                break
            else:
                print(f"{WARN}mplease insert a value{DEFAULT}")
                continue

    while(True):
        default, value_type = default_values.get('PIPELINE_NAME', lambda: None)()
        value = input(
            f"insert value for PIPELINE_NAME:\n") or default
        output_filename = f"{value}.gopipeline.json"
        output_path = os.path.join(group_path, output_filename)
        exist_path = os.path.join(script_dir, "*", output_filename)
        if glob.glob(exist_path):
            print(f"{WARN}mpipeline name already exist, please insert anotherone{DEFAULT}")
            continue
        if value:
            values['PIPELINE_NAME'] = value
            break
        else:
            if default:
                values['PIPELINE_NAME'] = default
                break
            else:
                print(f"{WARN}mplease insert a value{DEFAULT}")
                continue

    with open(template_path) as template_file:
        file_content = template_file.read()
        template = Template(file_content)
        variables = re.findall(r'{{(.*)}}', file_content)
        values = {}


        while(True):
            default_save = 'y'
            save = input(
                "Do you want to save generated pipeline?[Y/n]:\n",).lower() or default_save
            if save in ['yes', 'y', 'si', 's']:
                if not os.path.exists(group_path):
                    os.mkdir(group_path)
                with open(output_path, 'w') as output_file:
                    output_file.write(output)
                    break
            elif save in ['no', 'n']:
                break
            else:
                print(f"{WARN}mBad option, valid options are ('yes', 'y', 'si', 's', 'no', 'n'{DEFAULT}")
