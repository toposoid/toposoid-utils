'''
  Copyright 2021 Linked Ideal LLC.[https://linked-ideal.com/]
 
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at
 
      http://www.apache.org/licenses/LICENSE-2.0
 
  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
 '''

import requests
import os
import time
import subprocess
from logging import config
config.fileConfig('logging-tag.conf')
import logging
LOG = logging.getLogger(__name__)
import traceback
import argparse
from common import rex_check

GITHUB_USERNAME = os.environ.get('TOPOSOID_GITHUB_USERNAME')
GITHUB_REPO_OWNERNANE = os.environ.get('TOPOSOID_GITHUB_REPO_OWNERNANE')
GITHUB_PERSONAL_ACCESS_TOKENS = os.environ.get('TOPOSOID_GITHUB_PERSONAL_ACCESS_TOKENS')
TOPOSOID_PROJECT_DIR = os.environ.get('TOPOSOID_PROJECT_DIR')

session = requests.Session()
session.auth = (GITHUB_USERNAME, GITHUB_PERSONAL_ACCESS_TOKENS)

repogitoryNames = [
    #"scala-common",    
    "toposoid-common",
    "toposoid-knowledgebase-model",
    "toposoid-deduction-protocol-model",    
    "toposoid-common-nlp-japanese-web",
    "toposoid-common-nlp-english-web",
    "toposoid-sentence-parser-japanese",
    "toposoid-sentence-parser-japanese-web",
    "toposoid-sentence-parser-english-web",    
    "scala-data-accessor-neo4j",
    "toposoid-sentence-transformer-neo4j",   
    "toposoid-contents-admin-web",
    "toposoid-common-image-recognition-web",   
    "data-accessor-weaviate-web",   
    "toposoid-feature-vectorizer",    
    "toposoid-scala-lib",    
    "toposoid-knowledge-register-web",
    "scala-data-accessor-neo4j-web",
    "toposoid-deduction-common",
    "toposoid-deduction-unit-exact-match-web",
    "toposoid-deduction-unit-synonym-match-web",
    "toposoid-deduction-unit-sentence-vector-match-web",
    "toposoid-deduction-unit-image-vector-match-web",
    "toposoid-deduction-unit-whole-sentence-image-match-web",
    "toposoid-deduction-admin-web",
    "toposoid-sat-solver-web",
    "toposoid-component-dispatcher-web",
    "toposoid-easy-search-web",
    #"toposoid",
]



def main(args):
    try:
        for targetRepogitory in repogitoryNames:  

            os.chdir('../' + targetRepogitory )
            print(os.getcwd())
            cmd = ["git", "pull"]
            c = subprocess.check_output(cmd).decode()
            LOG.info(c)
            cmd = ["git", "checkout", "main"]
            c = subprocess.check_output(cmd).decode()
            LOG.info(c)
            cmd = ["git", "pull"]            
            c = subprocess.check_output(cmd).decode()
            LOG.info(c)
            cmd = ["git", "tag", "-a", "v%s" % (args.version), "-m", "version %s" % (args.version)]
            c = subprocess.check_output(cmd).decode()
            LOG.info(c)
            cmd = ["git", "push", "origin", "v%s" % (args.version)]
            c = subprocess.check_output(cmd).decode()
            LOG.info(c)
            time.sleep(3)

    except Exception as e:
        LOG.error(e)
        LOG.error(traceback.format_exc())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="This utility for 'git tag' in Toposoid Project.")  
    parser.add_argument('--version',  type=str, choices=rex_check(r"^\d+(?:\.\d+)$"), required=True) 
    args = parser.parse_args()    
    main(args)