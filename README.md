# pocket-bridge

A bridge application that exposes Pocket through other APIs.

## Features

* Publishes RSS and Atom feeds from your Pocket lists
  * Filterable by tag
  * Can integrate page's full content, filtered through Readability. Your server will requests the page by itself and store it in cache.
* Show Readability-filtered content for pages

## Usage

Use the Docker image with port 80, or install dependencies using `pip install .` and run `with python app/main.py`.

## Configuration

Configuration is done using variable environement or a `.env` file. All variables are prefixed with `BRIDGE_`.

* `BRIDGE_POCKET_CONSUMER_KEY`: Your Pocket application's consumer key
* `BRIDGE_USER_TOKENS`: Associations between request tokens (how you authenticate with pocket-bridge) and Pocket access
  token (how the bridge authenticates your account against Pocket). Sample: `{"password": "access-token"}`
* `BRIDGE_CACHE__BACKEND`: Cache backend to use, either `inmemory` or `redis`
* `BRIDGE_CACHE__REDIS_URL`: Redis URl to use when cache backend is redis.
* `BRIDGE_CACHE__PREFIX`: Prefix of bridge's data in cache backend
* `BRIDGE_CACHE__POCKET_LIST_EXPIRATION`: How many seconds Pocket lists will be kept in cache
* `BRIDGE_CACHE__READABILITY_EXPIRATION`: How many seconds Readability-filtered articles will be kept in cache
