# toposoid-utils
This repository contains utilities for Toposoid project development. For example, automatic version upgrade function, etc.
Toposoid is a knowledge base construction platform.(see [Toposoid　Root Project](https://github.com/toposoid/toposoid.git))

## Requirements
* python version 3.8.5, or later

## Setup
```bssh
pip install -r requirement.txt
```

## Usage
```bash
#automatic version upgrade
python versionUp.py --version 0.x --isSnapshot 0 
```
* --version: upgrade version
* --isSnapshot: 0:False,1:True
* --labelColor: For the SNAPSHOT version, you can specify the color when creating a new label(ex. 008672). If not specified, the color will be randomly determined.



## License
toposoid/toposoid-utils is Open Source software released under the [Apache 2.0 license](https://www.apache.org/licenses/LICENSE-2.0.html).

## Author
* Makoto Kubodera([Linked Ideal LLC.](https://linked-ideal.com/))

Thank you!
