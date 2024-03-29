**About**

The program for scraping info about GitHub repositories using datafile with the list of links. Datafile is a text file with the one link per line. The program checks is link correct or not. For each account link program get list of repo, for each repo we get info: full name, url, description, stars count, forks count, watching count, commits count, last commit info, releases count, last release, last release changelog. Can be run in test mode with hardcoded list of links. Scraped info will be saving to the MongoDB.

**Using data structure**

    full_name = str()
    description = str()
    site_url = str()
    stars = int()
    forks = int()
    watching = int()
    commits = int()
    last_commit_author = str() 
    last_commit_message = str()
    last_commit_datetime = str()
    releases = int()
    last_release_ver = str()
    last_release_change_log = str()
    last_release_datetime = str()

**System requirements**

- Linux based or Windows 10+ based with WSL2 with 1Gb RAM and 10Gb free disk space (if you will use local MongoDB)
- git preinstalled
- Docker preinstalled

**Build**

Firstly we need to copy the project sources from GitHub repository to local computer, run in terminal `git clone https://github.com/Sirojka/get_git.git`. After, go to project folder with: `cd get_git`, and all you need is a run `./build_image.sh` file or run `sudo docker build -t "get_git" .` command from the root folder of the project.

**Run**

Before running scraper you need MongoDB instance running locally/locally in docker container/on remote server. For locally running MongoDB please use the next mongo_uri command line option --mongo_uri mongodb://localhost:27017 or skip this option. If you need start new MongoDB instance in docker container locally please run next command from terminal: `sudo docker run --name local-mongo -d -p 27017:27017 mongo:latest`. It starts MondoDB container. After you should get container id with the next command: `sudo docker ps`. You will see output like this:

`CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS          PORTS                      NAMES`

`7f95be4a9815   mongo:latest   "docker-entrypoint.s…"   48 minutes ago   Up 48 minutes   0.0.0.0:27017->27017/tcp   local-mongo`

get CONTAINER ID (7f95be4a9815 - in this case) we'll need it than run scraper. Or you need uri connection string for remote server, like this: mongodb://HOST:PORT

After you get mongo_uri connection string you need start scraper with next command in terminal:

`sudo docker run -v LOCAL_LOG_DIR:/var/log -v LOCAL_LINKS_FILE_DIR:/opt --link CONTAINER_ID:CONTAINER_ID --rm get_git:latest python getgit_starter.py --datafile /opt/links.txt --mongo_uri mongodb://CONTAINER_ID:27017`

*Examples:*

`sudo docker run -v /var/log:/var/log --link 7f95be4a9815:7f95be4a9815 --rm get_git:latest python getgit_starter.py --test --mongo_uri mongodb://7f95be4a9815:27017`

`sudo docker run -v /var/log:/var/log -v /opt:/opt --link 7f95be4a9815:7f95be4a9815 --rm get_git:latest python getgit_starter.py --datafile /opt/links.txt --mongo_uri mongodb://7f95be4a9815:27017`

`sudo docker run -v /var/log:/var/log -v /opt:/opt --rm get_git:latest python getgit_starter.py --datafile /opt/links.txt --mongo_uri mongodb://remote_server.name:27017`

**Command line options**

- --apikey - api-key for Github API, allow 5000 requests per hour
- --test - run program in test-mode, will test only 2 hardcoded links (one account and one repository)
- --mongo_uri *MONGO_URI_STR* - uri for mongodb connection, default: mongodb://localhost:27017, format: mongodb://HOST:PORT
- --datafile *DATAFILE_STR* - full path to file with list of links, default: stored in settings as LINKS_FILE_NAME, you need to provide full path to file, like as /opt/files/links.txt and don't forget map /opt/files folder to docker container with -v option
- --proxy *PROXY_STR* - connection string for proxy server, default is blank (no using proxy), format: http://USER:PASS@HOST:PORT

*Example of datafile:*

    https://github.com/scrapy
    https://github.com/arm-software
    https://github.com/ronggang
    https://github.com/windoze
