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

#-----------------------------------------------------------------------------
#This module is a utility for version upgrade.
#-----------------------------------------------------------------------------

import os
import requests
import json
from fileConverter import convert
from logging import config
config.fileConfig('logging.conf')
import logging
LOG = logging.getLogger(__name__)
import traceback
import subprocess
import time
import argparse
import random
import re

GITHUB_USERNAME = os.environ.get('TOPOSOID_GITHUB_USERNAME')
GITHUB_REPO_OWNERNANE = os.environ.get('TOPOSOID_GITHUB_REPO_OWNERNANE')
GITHUB_PERSONAL_ACCESS_TOKENS = os.environ.get('TOPOSOID_GITHUB_PERSONAL_ACCESS_TOKENS')
TOPOSOID_PROJECT_DIR = os.environ.get('TOPOSOID_PROJECT_DIR')

session = requests.Session()
session.auth = (GITHUB_USERNAME, GITHUB_PERSONAL_ACCESS_TOKENS)

repogitoryNames = [
    "scala-common",
    "scala-data-accessor-neo4j",
    "toposoid-common"
    "toposoid-knowledgebase-model",
    "toposoid-deduction-protocol-model",
    "toposoid-common-nlp-japanese-web",
    "toposoid-common-nlp-english-web",
    "toposoid-sentence-parser-japanese",
    "toposoid-sentence-parser-japanese-web",
    "toposoid-sentence-parser-english-web",
    "toposoid-sentence-transformer-neo4j",
    "data-accessor-vald-web",
    "toposoid-feature-vectorizer",
    "toposoid-scala-lib",
    "scala-data-accessor-neo4j-web",
    "toposoid-deduction-common",
    "toposoid-deduction-unit-exact-match-web",
    "toposoid-deduction-unit-synonym-match-web",
    "toposoid-deduction-unit-sentence-vector-match-web",
    "toposoid-deduction-admin-web",
    "toposoid-sat-solver-web",
    "toposoid-knowledge-register-web",
    "toposoid-component-dispatcher-web",
    #"toposoid-ui",
    "toposoid"]

class rex_check(object):
  def __init__(self, pattern):
    self.pattern = pattern
  def __contains__(self, val):
    return re.match(self.pattern, val)
  def __iter__(self):
    return iter(("str", self.pattern))

def versionUp(targetRepogitory, version, labelColor, isSnapshot = False):

    try:
        versionTotalName = version  
        if isSnapshot:
            versionTotalName = version + "-SNAPSHOT"
            url = 'https://api.github.com/repos/%s/%s/labels' % (GITHUB_REPO_OWNERNANE, targetRepogitory)
            res = session.post(url,  json.dumps({
                "name": "assign to v" + version,
                "description": "This Issue is for release version " + versionTotalName,
                "color": labelColor            
            }))
            if not res.status_code == 201:
                raise Exception("Request Failed: {0} {1}".format(res.text, url))
            time.sleep(1)

        #TODO:If the snapshot is false, label the Issue with a release label
        url = 'https://api.github.com/repos/%s/%s/issues' % (GITHUB_REPO_OWNERNANE, targetRepogitory)
        res = session.post(url,  json.dumps({
            "title": "Upgrade to version " + versionTotalName,
            "body": "Feature branch upgrade.",            
            "labels": ["assign to v" + version],
        }))
        if not res.status_code == 201:
            raise Exception("Request Failed: {0} {1}".format(res.text, url))
        time.sleep(1)
        
        #make a branch
        url = "https://api.github.com/repos/%s/%s/git/refs/heads/feature" % (GITHUB_REPO_OWNERNANE, targetRepogitory)
        res = session.get(url)
        if not res.status_code == 200:
            raise Exception("Request Failed: {0} {1}".format(res.text, url))
        time.sleep(1)

        featureInfo = json.loads(res.content)
        sha = (featureInfo["object"]["sha"])

        url = "https://api.github.com/repos/%s/%s/git/refs" % (GITHUB_REPO_OWNERNANE, targetRepogitory)
        res = session.post(url,  json.dumps({
            "ref": "refs/heads/upgrade-to-v" + versionTotalName,
            "sha": sha
        }))    
        if not res.status_code == 201:
            raise Exception("Request Failed: {0} {1}".format(res.text, url))
        time.sleep(1)
       
        #update files
        convert(TOPOSOID_PROJECT_DIR, targetRepogitory, versionTotalName)
        
        #Some projects execute "sbt publishLocal"
        if targetRepogitory in ["scala-common","scala-data-accessor-neo4j","toposoid-common", "toposoid-knowledgebase-model","toposoid-deduction-protocol-model", "toposoid-sentence-parser-japanese", "toposoid-sentence-transformer-neo4j", "toposoid-feature-vectorizer"]:
            result = subprocess.run("sbt publishLocal", 
                cwd=TOPOSOID_PROJECT_DIR + "/" + targetRepogitory,
                shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            LOG.info(result.returncode)
            LOG.info(result.stdout)
            if not result.returncode == 0:
                raise Exception(result.stdout)


        #github pull request　from upgrade-v0.4-snapshot to feature
        url = 'https://api.github.com/repos/%s/%s/pulls' % (GITHUB_REPO_OWNERNANE, targetRepogitory)
        res = session.post(url,  json.dumps({
            "title": "Upgrade to version " + versionTotalName,
            "body": "This pull request is for release version " + versionTotalName,
            "head": "upgrade-to-v" + versionTotalName,
            "base": "feature"     
        }))

        if not res.status_code == 201:
            raise Exception("Request Failed: {0} {1}".format(res.text, url))
        time.sleep(3)

    except Exception as e:
        print(traceback.format_exc())
        LOG.error(traceback.format_exc())


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="This utility for version upgrade in Toposoid Project.")  
    parser.add_argument('--version',  type=str, choices=rex_check(r"^\d+(?:\.\d+)$"), required=True) 
    parser.add_argument('--isSnapshot', type=int, help="0:False,1:True", choices=[0, 1], required=True)
    parser.add_argument('--labelColor', type=str)
    args = parser.parse_args()
        
    color = [''.join([random.choice('0123456789ABCDEF') for j in range(6)])]
    if args.color:
      color = args.color
        
    for repo in repogitoryNames:    
        versionUp(repo, args.version, color, args.isSnapshot)
