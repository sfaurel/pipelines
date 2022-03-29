from jinja2 import Template
import re
from git import Repo
import os
import json
from pygments import highlight, lexers, formatters
import glob


def get_git_url():
    repo = Repo()
    return repo.remotes.origin.url, False


def get_image_tag():
    repo = Repo()
    tag_name = repo.remotes.origin.url.split(
        "@gitlab.grupoalto.com:altochecks/")[-1].strip('.git')
    return tag_name, False


def get_pipeline_name():
    repo = Repo()
    pipeline_name = repo.remotes.origin.url.split('/')[-1].strip('.git')
    return pipeline_name, True


default_values = {
    'PIPELINE_GROUP': lambda: (None, False),
    'PIPELINE_NAME': get_pipeline_name,
    'GIT_URL': get_git_url,
    'NEXUS': lambda: ('nexus.altoalliance.com:8086', False),
    'IMAGEN_TAG': get_image_tag
}

if __name__ == "__main__":
    script_dir = os.path.dirname(__file__)
    template_path = os.path.join(script_dir, 'docker_image.json.j2')
    with open(template_path) as template_file:
        file_content = template_file.read()
        template = Template(file_content)
        variables = re.findall(r'{{(.*)}}', file_content)
        values = {}
        for variable in variables:
            default, is_name = default_values.get(variable, lambda: None)()
            while(True):
                value = input(
                    f"insert value for {variable} [{default}]:\n") or default
                if is_name:
                    output_filename = f"{value}.json"
                    output_path = os.path.join(script_dir, output_filename)
                    exist_path = os.path.join(script_dir, "*", output_filename)
                    print(exist_path)
                    if glob.glob(exist_path):
                        print("pipeline name already exist, please insert anotherone")
                        continue

                if value:
                    values[variable] = value
                    break
                else:
                    if default:
                        values[variable] = default
                        break
                    else:
                        print("please insert a value")
                        continue
        output = template.render(**values)

        formatted_json = json.dumps(json.loads(output), indent=4)
        colorful_json = highlight(
            formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
        print("new pipeline was generated, check before save it")
        print(colorful_json)
        while(True):
            default_save = 'y'
            save = input(
                "Do you want to save pipeline?[Y/n]:\n",).lower() or default_save
            if save in ['yes', 'y', 'si', 's']:
                with open(output_path, 'w') as output_file:
                    output_file.write(output)
                    break
            elif save in ['no', 'n']:
                break
            else:
                print(
                    "Bad option, valid options are ('yes', 'y', 'si', 's', 'no', 'n'")
