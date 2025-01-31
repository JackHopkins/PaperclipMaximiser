# Factorio Learning Environment 

Factorio Learning Environment is an open-ended agent environment for evaluating LLMs in unbounded scenarios in Factorio, a sandbox game centred on automation and exponential resource production.


## Getting Started

Download install dependencies:

```
git clone https://github.com/ANONYMOUS
cd src
pip install -e .
```

Create a .env file

```
OPENAI_API_KEY=<KEY>
ANTHROPIC_API_KEY=<KEY>
NEPTUNE_API_TOKEN=<KEY>
TOGETHER_API_KEY = <KEY>

# To save the policies
SKILLS_DB_PORT=""
SKILLS_DB_NAME=""
SKILLS_DB_USER=""
SKILLS_DB_PASSWORD=""

# AWS credentials if wanting to use Cloudformation, NOT REQUIRED
AWS_SECRET_ACCESS_KEY=<KEY>
AWS_ACCESS_KEY_ID=""
AWS_DEFAULT_REGION=""
CLUSTER_NAME=""
```

### Client

- Buy Factorio from the [official website](https://www.factorio.com/).
- Downgrade to version 1.1.110 (the latest version supported by the environment) by following the following instructions:
    - Right-click Factorio in your Steam library and select Properties.
    - Go to the Betas tab.
    - Select 1.1.110 from the dropdown menu.

### Server

#### Install Docker

- Install Docker by following the instructions [here](https://docs.docker.com/get-docker/).
- Start the Docker daemon by running the following command:
    ```
    sudo systemctl start docker
    ```

##### Build the Docker image
- Navigate to the `factorio` directory and run the following command:
    ```
    docker build -t factorio .
    ```

##### Run the Factorio Server

- Navigate to `src/docker-compose-1.1.107.yml` and run the following command:
    ```
    docker-compose -f docker-compose-1.1.110.yml up -d
    ```
  
#### Activate Server

Once you have a server running, we need to activate it before we can start playing the game. 

To do this, open the Factorio client, navigate to 'Multiplayer' and enter the UDP address of the running server. By default this will be _localhost:34197_.

If you are running multiple servers (via docker compose), you will need to activate each one.

## Usage

### Running experiments
Open play experiments can be run with `src\search\beam\run_open_play.py` and lab-play experiments can be run with 
`src\search\beam\run_lab_play.py`.
To minimise local storage requirements, open-play experiments require the skills_db to be initialised as the last depth states are sampled from the database