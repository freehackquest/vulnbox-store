#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import os
import zipfile
import os.path
import json
import StringIO
import re
from pprint import pprint
import shutil

expected_vulnbox_store_json_fields = [
    'id', 'game', 'name', 'version',
    'created', 'author', 'created', 'issues',
    'checker-install-linux-packages',
    'checker-install-run-commands',
    'keywords',
    'contacts',
    'service-using-ports',
    'skip'
]

if not os.path.isdir("./html"):
    os.mkdir("./html")

if not os.path.isdir("./html/css"):
    os.mkdir("./html/css")

if not os.path.isdir("./html/images"):
    os.mkdir("./html/images")

if not os.path.isdir("./html/teams"):
    os.mkdir("./html/teams")

# shutil.copyfile('./src/index.html', './html/index.html')
shutil.copyfile('./src/favicon.ico', './html/favicon.ico')
shutil.copyfile('./src/css/index.css', './html/css/index.css')
shutil.copyfile('./src/images/logo.png', './html/images/logo.png')
shutil.copyfile('./vbs.py', './html/vbs.py')

d = './services'
services_path = [os.path.join(d, o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]
services_path.sort()


d = './teams'
teams_path = [os.path.join(d, o) for o in os.listdir(d) if os.path.isdir(os.path.join(d,o))]
teams_path.sort()

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_success(msg):
    global bcolors
    print(bcolors.OKGREEN + "OK: " + msg + bcolors.ENDC)

def print_header(msg):
    global bcolors
    print(bcolors.BOLD + msg + bcolors.ENDC)

def log_warn(msg):
    global bcolors
    print(bcolors.WARNING + "Warning: " + msg + bcolors.ENDC)

def log_err(msg):
    global bcolors
    print(bcolors.FAIL + "ERROR: " + msg + bcolors.ENDC)

def sortById(inputStr):
    return inputStr[0]

def downloadFromGithub(path, github_link):
    current_version = ''
    if os.path.isfile(path + "/vulnbox-store.json"):
        with open(path + "/vulnbox-store.json") as f:
            _json = json.load(f)
        if 'version' in _json:
            current_version = _json['version']
    
    print("\tCompare versions from " + github_link + " and local version")

    github_link_content = github_link.replace("//github.com/", "//raw.githubusercontent.com/")
    if github_link_content[len(github_link_content)-1] != '/':
        github_link_content = github_link_content + '/'
    github_link_content = github_link_content + 'master/vulnbox-store.json'
    r = requests.get(github_link_content)
    if r.status_code != 200:
        return False
    if 'version' not in r.json():
        log_err("Field 'version' not found in " + github_link_content)
        return False
    if r.json()['version'] != current_version:
        print("\tVersions do not match, try downloading...")
        github_link_zip = github_link
        if github_link_zip[len(github_link_zip)-1] != '/':
            github_link_zip = github_link_zip + '/'

        github_link_zip = github_link_zip + 'archive/master.zip'
        r = requests.get(github_link_zip, stream=True)
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
        fileslist = z.namelist()
        z.extractall(path)
        parent_dir = ''
        for fn in fileslist:
            fn2 = fn.split("/")
            parent_dir = fn2.pop(0)
            fn2 = "/".join(fn2)
            print(fn2)
            if os.path.isdir(path + '/' + fn):
                if not os.path.isdir(path + '/' + fn2):
                    os.mkdir(path + '/' + fn2)
            elif os.path.isfile(path + '/' + fn):
                if fn2 == 'github-download.json':
                    log_warn('Skipped file from repository "github-download.json"')
                    continue
                shutil.copyfile(path + '/' + fn, path + '/' + fn2)
        shutil.rmtree(path + '/' + parent_dir)
    else:
        print_header("\tVersions match. Do nothing.")

    return True

def prepareArchive(id, path):
    vulnbox_store_json_path = path + '/vulnbox-store.json'
    if not os.path.isfile(vulnbox_store_json_path):
        log_err(vulnbox_store_json_path + ' - not found')
        return False
    zip_file_name = 'html/' + id + '.zip'
    if os.path.isfile('html/' + id + '.zip'):
        os.remove(zip_file_name)

    zipf = zipfile.ZipFile(zip_file_name, 'w', zipfile.ZIP_DEFLATED)
    # write checker directory
    path_checker = path + '/checker'
    for root, dirs, files in os.walk(path_checker):
        root2 = root[len(path):]
        for file in files:
            zipf.write(os.path.join(root, file), os.path.join(root2, file))

    # write service directory
    path_service = path + '/service'
    for root, dirs, files in os.walk(path_service):
        root2 = root[len(path):]
        for file in files:
            zipf.write(os.path.join(root, file), os.path.join(root2, file))

    zipf.write(path + '/vulnbox-store.json', 'vulnbox-store.json')
    zipf.close()
    return True

def checkServiceConf(id, path, vulnbox_store_json):
    service_conf_path = path + '/checker/service.conf'
    if not os.path.isfile(service_conf_path):
        log_err(service_conf_path + ' - not found')
        return False

    with open(service_conf_path) as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    prefix = 'services.' + id + '.'
    expected_fields = [
        prefix + 'enabled',
        prefix + 'name',
        prefix + 'script_path',
        prefix + 'script_wait_in_sec',
        prefix + 'time_sleep_between_run_scripts_in_sec',
    ]
    service_conf = {}
    bErr = False
    for lin in content:
        if lin.find('=') != -1:
            param_name = lin[0:lin.find('=')]
            param_value = lin[lin.find('=')+1:]
            param_name = param_name.strip()
            param_value = param_value.strip()
            if param_name not in expected_fields:
                log_err(service_conf_path + " - extra param_name '" + param_name + "'")
                bErr = True
            else:
                service_conf[param_name] = param_value
    for name in expected_fields:
        if name not in service_conf:
            log_err(service_conf_path + " - missing param '" + param_name + "'")
            bErr = True
    
    if bErr == True:
        return False

    if service_conf[prefix + "name"] != vulnbox_store_json["name"]:
        log_err(service_conf_path + " - don't match name with defined in vulnbox-store.json")

    checker_script_path = path + "/checker/" + service_conf[prefix + "script_path"]
    if not os.path.isfile(checker_script_path):
        log_err(checker_script_path + ' - not found file defined in ' + service_conf_path )
        return False

    return True


def checkPackageService(id, path):
    
    vulnbox_store_json_path = path + '/vulnbox-store.json'
    if not os.path.isfile(vulnbox_store_json_path):
        log_err(vulnbox_store_json_path + ' - not found')
        return False

    with open(vulnbox_store_json_path) as f:
        vulnbox_store_json = json.load(f)

    bErr = False
    for field in vulnbox_store_json:
        if field not in expected_vulnbox_store_json_fields:
            log_err(vulnbox_store_json_path + " - extra field '" + field + "'")
            bErr = True

    for field in expected_vulnbox_store_json_fields:
        if field not in vulnbox_store_json:
            log_err(vulnbox_store_json_path + " - not found field '" + field + "'")
            bErr = True

    if bErr:
        return False

    if not isinstance(vulnbox_store_json['service-using-ports'], list):
        log_err(vulnbox_store_json_path + " - field 'service-using-ports' expected list")
        return False
    
    if not isinstance(vulnbox_store_json['checker-install-linux-packages'], list):
        log_err(vulnbox_store_json_path + " - field 'checker-install-linux-packages' expected list")
        return False
    
    if not isinstance(vulnbox_store_json['checker-install-run-commands'], list):
        log_err(vulnbox_store_json_path + " - field 'checker-install-run-commands' expected list")
        return False

    if vulnbox_store_json['id'] != id:
        log_err(vulnbox_store_json_path + ' has id = ' + vulnbox_store_json['id'] + ' but expected ' + id)
        return False

    if not os.path.isdir(path + '/service'):
        log_err(path + '/service' + " - directory not found")
        return False

    if not os.path.isfile(path + '/service/Dockerfile'):
        log_err(path + '/service/Dockerfile' + " - file missing")
        return False
    
    if not os.path.isfile(path + '/service/README.md'):
        log_err(path + '/service/README.md' + " - file missing")
        return False

    if not os.path.isdir(path + '/checker'):
        log_err(path + '/checker' + " - directory not found")
        return False

    if not os.path.isfile(path + '/checker/service.conf'):
        log_err(path + '/checker/service.conf' + " - file missing")
        return False

    if not checkServiceConf(id, path, vulnbox_store_json):
        log_err(path + '/checker/service.conf - invalid params')
        return False

    return True

teams_names = []
teams_json = []
for s in teams_path:
    filename = s.split("/")
    filename = filename[len(filename)-1]
    filename = filename.lower()
    if filename in teams_names:
        log_err(filename + ' - duplicates')
        continue
    teams_names.append(filename)

    pattern = re.compile("^([a-z0-9_]+)$")
    if not pattern.match(filename):
        log_err('teams/' + filename + ' - allow contains a lower english characters, numbers and _')
        continue

    print_header("\n* teams/" + filename + " scanning...")

    info_json_path = s + '/info.json'
    if not os.path.isfile(info_json_path):
        log_err(info_json_path + ' - not found')
        continue

    with open(info_json_path) as f:
        info_json = json.load(f)

    if 'id' not in info_json:
        log_err(info_json_path + " - not found field 'id'")
        continue

    if info_json['id'] != filename:
        log_err(info_json_path + " - 'id' must contains " + filename)
        continue
    
    if 'name' not in info_json:
        log_err(info_json_path + " - not found field 'name'")
        continue

    if 'logo' not in info_json:
        log_err(info_json_path + " - not found field 'logo'")
        continue

    logo_img = info_json['logo']
    if logo_img.split(".")[0] != filename:
        log_err(info_json_path + " - base file name of logo must be " + filename)
        continue

    logo_img = s + '/' + info_json['logo']
    if not os.path.isfile(logo_img):
        log_err(info_json_path + ' - not found file ' + logo_img)
        continue
    
    shutil.copyfile(info_json_path, './html/teams/' + info_json['logo'])
    teams_json.append(info_json)
    print_success ("Done")

with open('html/teams.json', 'w') as outfile:
    json.dump(teams_json, outfile, ensure_ascii=False, indent=4)

services_names = []
services_json = []
for s in services_path:
    filename = s.split("/")
    filename = filename[len(filename)-1]
    filename = filename.lower()
    if filename in services_names:
        log_err(filename + ' - duplicates')
        continue
    services_names.append(filename)

    pattern = re.compile("^([a-z0-9_]+)$")
    if not pattern.match(filename):
        log_err('services/' + filename + ' - allow contains a lower english characters, numbers and _')
        continue

    zip_file_name = 'html/' + filename + '.zip'
    if os.path.isfile(zip_file_name):
        os.remove(zip_file_name)

    print_header("\n* services/" + filename + " scanning...")
    
    """
    Try downloads form github
    """

    github_download_json_path = s + '/github-download.json'
    if os.path.isfile(github_download_json_path):
        with open(github_download_json_path) as f:
            github_download_json = json.load(f)
        if "github" not in github_download_json:
            log_err(github_download_json_path + " - not found field 'github'")
            continue
        github_link = github_download_json['github']
        if downloadFromGithub(s, github_link) == False:
            log_err(github_download_json_path + " could not download from github")
            continue

    """
    check the struct of folder
    """

    if not checkPackageService(filename, s):
        log_err('./services/' + filename + ' - invalid')
        continue

    vulnbox_store_json_path = s + '/vulnbox-store.json'
    

    if not prepareArchive(filename, s):
        log_err('./services/' + filename + ' - could not prepare zip archive')
        continue
    
    with open(vulnbox_store_json_path) as f:
        vulnbox_store_json = json.load(f)
        services_json.append(vulnbox_store_json)

    print_success ("Done")

with open('html/services.json', 'w') as outfile:
    json.dump(services_json, outfile, ensure_ascii=False, indent=4)

with open('src/index.html') as f:
    index_html = f.readlines()

index_html = "".join(index_html)
start_i = index_html.find("<template-service>") + len("<template-service>")
end_i = index_html.find("</template-service>")

template_service = index_html[start_i:end_i]
_prev = index_html[:start_i]
_next = index_html[end_i:]

rows = []

for srvc in services_json:
    row = template_service
    for name in expected_vulnbox_store_json_fields:
        if isinstance(srvc[name], basestring):
            row = row.replace('{' + name + '}', srvc[name])

    checker_install = 'RUN apt install -y  "' + '" "'.join(srvc['checker-install-linux-packages']) + '"'
    checker_install = checker_install
    checker_install = checker_install + "\nRUN " + "\nRUN ".join(srvc['checker-install-run-commands'])
    
    row = row.replace('{checker-install}', checker_install)
    row = row.replace('{download}', srvc['id'] + '.zip')
    row = row.replace('{keywords}', ', '.join(srvc['keywords']))

    rows.append(row)

index_html = _prev + "".join(rows) + _next

with open('html/index.html', 'w') as f:
    f.write(index_html)