# Under Construction

# Jiku

Estimate known vocabulary from Anki decks and apply this data to a texthooker and epub reader (more in the future).



Screenshots


## Installation

The recommended installation method is to use the docker-compose file. Running all components (including the postgresql and redis databases) directly on the host machine is possible by manually passing the necessary environmental variables.

1. Install [Docker](https://docs.docker.com/get-started/get-docker/)
2. Download the `docker-compose.yaml` file from the [releases page](https://github.com/TnTora/Jiku/releases)
3. Open terminal (or Command Prompt/Powershell) in the folder containing the downloaded file
4. Run the following command and wait for the installation to complete
```
docker-compose up -d
```

Once the command finishes you can stop and start the app from  Docker Desktop or Docker CLI.