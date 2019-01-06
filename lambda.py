import datetime
import dateutil
import json

import boto3
from botocore.vendored import requests


def chainso_api_handler(response_data):
    """
    An API handler for Chain.so (a public block explorer) API responses. Returns
    the block height for the given coin + network.

    Used to parse: BTC, LTC, DASH, ZEC
    """
    return response_data['data']['blocks']


def btcdotcom_api_handler(response_data):
    """
    An API handler for btc.com (a public block explorer) API responses. Returns
    the block height for the given coin + network.

    Used to parse: BCH
    """
    return response_data['data']['height']


def blocktrail_api_handler(response_data):
    """
    An API handler for blocktrail.com (a public block explorer) API responses. Returns
    the block height for the given coin + network.

    Used to parse: TBCH
    """
    return int(response_data['last_blocks'][0]['height'])

def blockcypher_api_handler(response_data):
    """
    An API handler for blockcypher.com (a public block explorer) API responses. Returns
    the block height for the given coin + network.

    Used to parse: ETH
    """
    return response_data['height']


def blockscout_api_handler(response_data):
    """
    An API handler for blockscout.com (a public block explorer) API responses. Returns
    the block height for the given coin + network.

    Used to parse: TETH (Kovan)
    """
    return int(response_data['next_page_path'].split('/')[-1].split('=')[-1])


def ripple_api_handler(response_data):
    """
    An API handler for data.ripple.com (a public block explorer) API responses. Returns
    the block height for the given coin + network.

    Used to parse: XRP
    """
    return response_data['ledger']['ledger_index']


def stellar_api_handler(response_data):
    """
    An API handler for data.ripple.com (a public block explorer) API responses. Returns
    the block height for the given coin + network.

    Used to parse: XRP
    """
    return response_data['_embedded']['records'][0]['sequence']


def lambda_handler(event, context):
    """
    Runs through every indexer in BitGo's stack, compares it state to a public
    block explorer, and writes that state to a JSON file on s3 (actually, two
    JSON files, one time-stamped file and another that represents the "latest"
    file that a front-end app will pull from).

    The data structure pushed to s3 will look like:
    """
    pst = dateutil.tz.gettz('US/Pacific')
    current_time = datetime.datetime.now(tz=pst)

    # The number of blocks we allow BitGo to fall behind for a given chain
    # before alerting the dashboard
    BLOCKS_BEHIND_THRESHOLD = 4

    # This dict acts as both a mapping of coin + env to public block explorer as
    # as the final data dict that will be jsonified and persisted to s3 once
    # values like `status`, `latestBlock`, and `blocksBehind` have been populated
    output_data = {
        "metadata": {
            "dateFetched": current_time.strftime('%Y-%m-%d at %I:%M%p PST')
        },
        "indexers": {
            "BTC": {
                "name": "Bitcoin",
                "icon": "assets/images/btc.png",
                "environments": [{
                    "network": "MainNet",
                    "bgURL": "https://www.bitgo.com/api/v2/btc/public/block/latest",
                    "publicURL": "https://chain.so/api/v2/get_info/BTC",
                    "apiHandler": chainso_api_handler
                },
                {
                    "network": "TestNet",
                    "bgURL": "https://test.bitgo.com/api/v2/tbtc/public/block/latest",
                    "publicURL": "https://chain.so/api/v2/get_info/BTCTEST",
                    "apiHandler": chainso_api_handler
                }]
            },
            "LTC": {
                "name": "Litecoin",
                "icon": "assets/images/ltc.png",
                "environments": [{
                    "network": "MainNet",
                    "bgURL": "https://www.bitgo.com/api/v2/ltc/public/block/latest",
                    "publicURL": "https://chain.so/api/v2/get_info/LTC",
                    "apiHandler": chainso_api_handler
                },
                {
                    "network": "TestNet",
                    "bgURL": "https://test.bitgo.com/api/v2/tltc/public/block/latest",
                    "publicURL": "https://chain.so/api/v2/get_info/LTCTEST",
                    "apiHandler": chainso_api_handler
                }]
            },
            "BCH": {
                "name": "Bitcoin Cash",
                "icon": "assets/images/bch.png",
                "environments": [{
                    "network": "MainNet",
                    "bgURL": "https://www.bitgo.com/api/v2/bch/public/block/latest",
                    "publicURL": "https://bch-chain.api.btc.com/v3/block/latest/",
                    "apiHandler": btcdotcom_api_handler,
                },
                {
                    "network": "TestNet",
                    "bgURL": "https://test.bitgo.com/api/v2/tbch/public/block/latest",
                    "publicURL": "https://www.blocktrail.com/tBCC/json/blockchain/block_all/main/1",
                    "apiHandler": blocktrail_api_handler,
                }]
            },
            "ETH": {
                "name": "Ethereum",
                "icon": "assets/images/eth.png",
                "environments": [{
                    "network": "MainNet",
                    "bgURL": "https://www.bitgo.com/api/v2/eth/public/block/latest",
                    "publicURL": "https://api.blockcypher.com/v1/eth/main",
                    "apiHandler": blockcypher_api_handler,
                },
                {
                    "network": "TestNet",
                    "bgURL": "https://test.bitgo.com/api/v2/teth/public/block/latest",
                    "publicURL": "https://blockscout.com/eth/kovan/blocks?type=JSON",
                    "apiHandler": blockscout_api_handler,
                }]
            },
            "DASH": {
                "name": "Dash",
                "icon": "assets/images/dash.png",
                "environments": [{
                    "network": "MainNet",
                    "bgURL": "https://www.bitgo.com/api/v2/dash/public/block/latest",
                    "publicURL": "https://chain.so/api/v2/get_info/DASH",
                    "apiHandler": chainso_api_handler
                },
                {
                    "network": "TestNet",
                    "bgURL": "https://test.bitgo.com/api/v2/tdash/public/block/latest",
                    "publicURL": "https://chain.so/api/v2/get_info/DASHTEST",
                    "apiHandler": chainso_api_handler
                }]
            },
            "ZEC": {
                "name": "ZCash",
                "icon": "assets/images/zec.png",
                "environments": [{
                    "network": "MainNet",
                    "bgURL": "https://www.bitgo.com/api/v2/zec/public/block/latest",
                    "publicURL": "https://chain.so/api/v2/get_info/ZEC",
                    "apiHandler": chainso_api_handler
                },
                {
                    "network": "TestNet",
                    "bgURL": "https://test.bitgo.com/api/v2/tzec/public/block/latest",
                    "publicURL": "https://chain.so/api/v2/get_info/ZECTEST",
                    "apiHandler": chainso_api_handler
                }]
            },
            "XRP": {
                "name": "Ripple",
                "icon": "assets/images/xrp.png",
                "environments": [{
                    "network": "MainNet",
                    "bgURL": "https://www.bitgo.com/api/v2/xrp/public/block/latest",
                    "publicURL": "https://data.ripple.com/v2/ledgers/",
                    "apiHandler": ripple_api_handler,
                },
                {
                    "network": "TestNet",
                    "bgURL": "https://test.bitgo.com/api/v2/txrp/public/block/latest",
                    "publicURL": "https://testnet.data.api.ripple.com/v2/ledgers",
                    "apiHandler": ripple_api_handler,
                }]
            },
            "XLM": {
                "name": "Stellar",
                "icon": "assets/images/xlm.png",
                "environments": [{
                    "network": "MainNet",
                    "bgURL": "https://www.bitgo.com/api/v2/xlm/public/block/latest",
                    "publicURL": "https://horizon.stellar.org/ledgers?order=desc",
                    "apiHandler": stellar_api_handler,
                },
                {
                    "network": "TestNet",
                    "bgURL": "https://test.bitgo.com/api/v2/txlm/public/block/latest",
                    "publicURL": "https://horizon-testnet.stellar.org/ledgers?order=desc",
                    "apiHandler": stellar_api_handler,
                }]
            },
        }
    }

    # Iterate over the dict above and fill in the blanks:
    # 1. Hit BitGo to get the state of the indexer
    # 2. Hit a public block explorer to compare chainheads
    # 3. Add the state to the dict
    for coin_symbol, coin_data in output_data['indexers'].items():
        for env_data in coin_data['environments']:

            # Hit BitGo's IMS to fetch data about the most recently processed block
            response = requests.get(env_data['bgURL'])
            bg_response = json.loads(response.content)

            # Set default values (assume a healthy status)
            env_data['status'] = True
            env_data['blocksBehind'] = 0
            env_data['latestBlock'] = bg_response['height']

            # Fetch the api handler defined in the indexer config and pop it
            # from the dict at the same time; we don't want to provide it in the
            # serialized JSON output)
            api_handler = env_data.pop('apiHandler')

            # Sometimes, BitGo will inform us directly that it's at chainhead.
            # In these cases, assume that that is truthy, and move on with
            # checking against a public block explorer.
            if bg_response.get('chainHead', False):
                # No need to continue processing - keep the default data and move on
                continue

            # Compare the current chain height of BitGo to that of a public
            # block explorer
            response = requests.get(env_data['publicURL'])
            public_response = json.loads(response.content)

            # Use the handler defined on the coin + network to parse the response
            # and return the public height of the blockchain
            public_block_explorer_height = api_handler(public_response)

            # If the difference is greater than our threshold, pitch a fit
            if (public_block_explorer_height - bg_response['height']) > BLOCKS_BEHIND_THRESHOLD:
                env_data['status'] = False
                env_data['blocksBehind'] = '{} blocks'.format(public_block_explorer_height - bg_response['height'])
                env_data['latestBlock'] = bg_response['height']

    # Jsonify the output dict
    string = json.dumps(output_data)
    encoded_string = string.encode("utf-8")

    # Create the file names; we create two:
    # 1. A timestamped version of the json for historical purposes
    # 2. A file called 'latest' which overwrites the previously marked 'latest'
    # file. This is the file that the front-end app consumes. Overwriting it every
    # five minutes keeps the app up to date.
    dated_file_name = "{}.json".format(current_time)
    latest_file_name = "latest.json"

    # Write the files to the bucket
    bucket_name = "bitgo-indexer-health"
    s3 = boto3.resource("s3")
    aws_kwargs = {
        'Body': encoded_string,
        'ACL': 'public-read',
        'ContentType': 'application/json',
    }
    s3.Bucket(bucket_name).put_object(Key=dated_file_name, **aws_kwargs)
    s3.Bucket(bucket_name).put_object(Key=latest_file_name, **aws_kwargs)
