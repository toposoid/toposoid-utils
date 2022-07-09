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

#Update files required for version upgrade and execute git command

import re
import os
import datetime
from glob import glob
import git
import subprocess

t_delta = datetime.timedelta(hours=9)
JST = datetime.timezone(t_delta, 'JST')
now = datetime.datetime.now(JST)

regexActionYml = re.compile('.*(PJ_VERSION\: )(.*)')
regexBuildSbt1 = re.compile('.*(version.*= )\"(\d+\.\d+.*)\"')
regexBuildSbt2 = re.compile('.*(com\.ideal\.linked\" %% \")(.*% )\"(\d+\.\d+.*)\"')
regexDockerComposeYml = re.compile('.*(image\: toposoid\/)(toposoid-|scala-).*\:(\d+\.\d+.*)')
regexDockerComposeYmlWF1 = re.compile('.*(image\: )(toposoid-|scala-).*\:(\d+\.\d+.*)')
regexDockerComposeYmlWF2 = re.compile('.*(image\: toposoid\/)(toposoid-|scala-).*\:(\d+\.\d+.*)-workflow')
regexEntryPointSh = re.compile('.*(\d+\.\d+.*)\/bin\/.*')
regexDockerfile1 = re.compile('FROM.*\:(\d+\.\d+.*)')
regexDockerfile2 = re.compile('.* unzip -o.*(\d+\.\d+.*).zip')
backupDate = now.strftime('%Y%m%d%H%M%S')

def replaceVersion(projectRootPath, targetRepogitory, targetFile, regexs, versionStr):    
    newVersionContent = ""
    with open(projectRootPath + "/" + targetRepogitory + "/" + targetFile) as f:          
        for line in f:
            isHit = False
            for groupNo, regex in regexs:
                #In the case of Dockerfile, if it contains a specific character string, it is excluded from VersionUp.
                if targetFile.startswith("Dockerfile") and ("scala-base:" in line or "scala-nlp:" in line or "scala-knp:" in line or "core-nlp:" in line or "python-nlp-japanese:" in line or "python:" in line):
                    continue
                result = regex.match(line)
                if not result is None:
                    isHit = True
                    newVersionContent += line.replace(result.group(groupNo), versionStr)                    
                    break #It is assumed that one line is replaced by one regular expression
            if not isHit:
                newVersionContent += line
                
    os.rename(projectRootPath + "/" + targetRepogitory + "/" + targetFile, projectRootPath + "/" + targetRepogitory + "/" + targetFile + backupDate)

    with open(projectRootPath  + "/" + targetRepogitory + "/" + targetFile, 'w', encoding='utf-8') as f:
        f.write(newVersionContent)

def convert(projectRootPath, targetRepogitory, versionStr):
    

    repo = git.Repo(projectRootPath + "/" + targetRepogitory)    
    
    repo.git.pull()
    #Branch checkout
    repo.git.checkout('origin/upgrade-to-v' + versionStr, b='upgrade-to-v' + versionStr)
    
    #action.xml
    if os.path.exists(projectRootPath + "/" + targetRepogitory + "/.github/workflows/action.yml"):
        replaceVersion(projectRootPath, targetRepogitory, ".github/workflows/action.yml", [(2,regexActionYml)], versionStr)
        repo.git.add(".github/workflows/action.yml")
    #build.sbt
    if os.path.exists(projectRootPath + "/" + targetRepogitory + "/build.sbt"):
        replaceVersion(projectRootPath, targetRepogitory, "build.sbt", [(2,regexBuildSbt1), (3,regexBuildSbt2)], versionStr)
        repo.git.add("build.sbt")

    #docker-compose
    if os.path.exists(projectRootPath + "/" + targetRepogitory + "/docker-compose.yml"):
        replaceVersion(projectRootPath, targetRepogitory, "docker-compose.yml", [(3,regexDockerComposeYml)], versionStr)
        repo.git.add("docker-compose.yml")

    #docker-compose-workflow　
    #Regular expression order is important
    if os.path.exists(projectRootPath + "/" + targetRepogitory + "/docker-compose-workflow.yml"):
        replaceVersion(projectRootPath, targetRepogitory, "docker-compose-workflow.yml", [(3,regexDockerComposeYmlWF1), (3,regexDockerComposeYmlWF2), (3,regexDockerComposeYml)], versionStr)
        repo.git.add("docker-compose-workflow.yml")

    #docker-entrypoint.sh
    if os.path.exists(projectRootPath + "/" + targetRepogitory + "/docker-entrypoint.sh"):
        replaceVersion(projectRootPath, targetRepogitory, "docker-entrypoint.sh", [(1,regexEntryPointSh)], versionStr)
        #This file requires execute permission
        result = subprocess.run("chmod +x docker-entrypoint.sh", 
            cwd=projectRootPath + "/" + targetRepogitory,
            shell=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if not result.returncode == 0:
            raise Exception(result.stdout)

        
        repo.git.add("docker-entrypoint.sh")

    #Dockerfile
    if os.path.exists(projectRootPath + "/" + targetRepogitory + "/Dockerfile"):
        replaceVersion(projectRootPath, targetRepogitory, "Dockerfile", [(1,regexDockerfile1), (1,regexDockerfile2)], versionStr)
        repo.git.add("Dockerfile")
    if os.path.exists(projectRootPath + "/" + targetRepogitory + "/Dockerfile-smallspec"):
        replaceVersion(projectRootPath, targetRepogitory, "Dockerfile-smallspec", [(1,regexDockerfile1), (1,regexDockerfile2)], versionStr)
        repo.git.add("Dockerfile-smallspec")
    if os.path.exists(projectRootPath + "/" + targetRepogitory + "/Dockerfile-workflow"):
        replaceVersion(projectRootPath, targetRepogitory, "Dockerfile-workflow", [(1,regexDockerfile1), (1,regexDockerfile2)], versionStr)
        repo.git.add("Dockerfile-workflow")
    
    #git commit
    repo.git.commit(message="Upgrade to version " + versionStr)
    #git push
    repo.git.push('origin', 'upgrade-to-v' + versionStr)


