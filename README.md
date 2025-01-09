# Factory-1

Factory-1 is an open-ended agent environment for evaluating LLMs in unbounded scenarios in Factorio, a sandbox game centred on automation and exponential resource production.


## Getting Started

You will need openssl and [uv](https://docs.astral.sh/uv/). Openssl needs to be available in your environment.
```
brew install openssl uv
export LDFLAGS="-L/opt/homebrew/opt/openssl/lib"
```

Download the repository, set up a virtual environment and install the dependencies:
```
git clone https://github.com/JackHopkins/PaperclipMaximiser.git
cd PaperclipMaximiser
uv venv
source .venv/bin/activate
uv sync
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

##### Build a Docker image containing the test scenario
```
docker build -t factorio cluster/docker --load
```

##### Run the Factorio Server

- Run the following command:
  ```
  docker-compose -f cluster/local/docker-compose.yml up -d
  ```

#### Activate Server

Once you have a server running, we need to activate it before we can start playing the game.

To do this, open the Factorio client, navigate to 'Multiplayer' and enter the UDP address of the running server. By default this will be _localhost:34197_.

If you are running multiple servers (via docker compose), you will need to activate each one.

## Data

We provide a dataset of 50,000 trajectories of gameplay. These trajectories were generated by running an agent on the server and recording its actions.

The dataset can be downloaded [here]().

To generate your own dataset, you should perform an MCTS run by following the instructions [here](./src/search/mcts/readme.md)


## Evaluate Agent

## Background

Factorio is a sandbox game in which you build and maintain automated factories.

The player mines raw resources, researches technologies, builds infrastructure, automates production and fights enemies.

Automating production is the core of the game. The player builds machines that take in raw resources and output more complex and valuable resources.

By combining automated elements into economic structures, applying management skills to keep it working and finally protecting the factories from angry neighbours, there is scope for enormous factories.

There is the opportunity for infinite emergent complexity, as Factorio is Turing-complete (i.e any calculable function can be calculated in Factorio).


# Building a Paperclip Maximiser

### Introduction

In AGI, instrumental convergence is the hypothetical tendency for sufficiently intelligent agents to pursue unbounded instrumental goals provided that their ultimate goals are themselves unlimited.

This is illustrated by the hypothetical Paperclip Maximiser (Bostrum, 2003), in which an agent given the sole and unconstrained goal of maximising the number of paperclips a factory outputs, could attempt to turn the Earth into one giant factory (and convert all humans into paperclips in the process).

The drives of such an intelligent system are likely to include goal-content integrity, self-protection, freedom from interference, self-improvement, and non-satiable acquisition of additional resources.

Interestingly, the game of Factorio implicitly or explicitly models each of the above.

### The Game

Factorio is a game in which you build and maintain factories.

The core idea of Factorio is simple, but there is scope for massive emergent complexity.

The player mines raw resources, researches technologies, builds infrastructure, automates production and fights enemies. By combining simple elements into ingenious structures, applying management skills to keep it working and finally protecting the factories from angry neighbours, there is scope for enormous factories (or programs). There is the opportunity for infinite emergent complexity, as Factorio is Turing-complete (i.e any calculable function can be calculated in Factorio).

![Some crafting dependencies](https://community.wolfram.com//c/portal/getImageAttachment?filename=Factorio_All.png&userId=73716)

The size of factory you build is constrained by:
- Access to raw resources
- The hostility of neighbours, which increases proportionally to the size of the factory.

This second factor results in two viable long-term strategies. First, by building aggressively and investing in defenses (walls, auto-turrets etc). Second, by building slowly and investing in energy sources that don't impact the neighbours and don't incur hostility.

### An RL Sandbox

The simple rules and infinite emergent complexity of Factorio make it an ideal RL sandbox:
- The automated nature of the factory presents a dense reward function (i.e game resources update every tick).
- Extremely simple policies (i.e as few as 2 actions) can generate a some reward.
- Each of the basic drives of an intelligent system can be demonstrated and evaluated.


**Objective**: To maximise the number of 'paperclips' (represented as copper coils in-game) existant in the game-world at any cost.

**Goal-content Integrity**: The game supports pseudo-variables in-game, which means that the objective function can be represented as a composite of these pseudo-variables (e.g maximise the incidence of whatever resource is stored in the box in tile 1:15). A sufficiently intelligent agent would be adverse to altering the contents of the box, as that would compromise goal-content integrity.

**Resource Acquisition**: The game benefits an intelligent agent directly, as specific resources acquired affects it's reward function. Indirectly, the accrual of non-rewarded resources enables a sufficiently intelligent agent to expand the size of the factory, thus increasing the rate of paperclip generation.

**Self-Protection**: The game introduces hostile countermeasures to destroy the factory. A sufficiently intelligent agent would either develop resources to fight these countermeasures, or attempt to avoid countermeasures in the first place.

**Self-Improvement**: The game offers technological progression, in which certain features are unlocked after a factory has conducted research as a sub-goal. These features offer faster resource gathering, and more efficient factory layouts to improve density.
