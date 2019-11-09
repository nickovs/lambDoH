# lambDoH

"""
A DNS over HTTPS server that runs as an AWS Lambda function
"""

from base64 import b64decode
import logging
import os
import sys

from chalice import Chalice, Response, BadRequestError

from chalicelib import DNSClient

APP_NAME = "lambDoH"
LAMBDOH_VERSION_STRING = "0.2.0"

DNS_MESSAGE_TYPE = 'application/dns-message'

# Set up logging based on the LOG_LEVEL environment variable
LOG_LEVEL = getattr(logging,
                    os.environ.get('LOG_LEVEL', '').upper(),
                    logging.ERROR)
LOGGER = logging.getLogger("__app__")
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(LOG_LEVEL)

try:
    DNS_TIMEOUT = float(os.environ.get('DNS_TIMEOUT', '5.0'))
except ValueError:
    DNS_TIMEOUT = 5.0
    LOGGER.error("Illegal value for DNS timeout (%s), defaulting to %s seconds",
                 os.environ.get('DNS_TIMEOUT'), DNS_TIMEOUT)

DNS_SHUFFLE = (os.environ.get('DNS_SHUFFLE', 'no').strip().lower() in
               {"1", "yes", "on", "true"})

# Create a single DNS client
DNS_CLIENT = DNSClient(os.environ.get('DNS_SERVERS'),
                       shuffle=DNS_SHUFFLE, timeout=DNS_TIMEOUT)

# Chalice likes the top-level `app` variable to be lower case, PyLint does not
# pylint: disable=invalid-name
app = Chalice(app_name=APP_NAME)
# For some reason simply adding DNS_MESSAGE_TYPE to the list does not work
app.api.binary_types = ['*/*']

@app.route('/version')
def index():
    """Return app and version information"""
    return {'app': APP_NAME,
            'version': LAMBDOH_VERSION_STRING}

@app.route('/', methods=['GET'])
def dns_query_get():
    """Handle DoH request over GET"""
    request = app.current_request
    LOGGER.debug("API gateway request (GET): %s", request.to_dict())
    b64_payload = request.query_params.get("dns")
    pad = "=" * ((-len(b64_payload)) % 4)
    return _dns_query_handle(b64decode(b64_payload + pad))

@app.route('/', methods=['POST'],
           content_types=[DNS_MESSAGE_TYPE])
def dns_query_post():
    """Handle DoH request over POST"""
    request = app.current_request
    LOGGER.debug("API gateway request (POST): %s", request.to_dict())
    return _dns_query_handle(request.raw_body)

# Chalice-specific code for processing queries
def _dns_query_handle(query_raw):
    if not query_raw:
        raise BadRequestError("No dns query given")
    LOGGER.debug("Query is %s bytes: %s", len(query_raw), query_raw)

    reply_raw = DNS_CLIENT.resolve_dns_query(query_raw)

    LOGGER.debug("Reply is %s bytes: %s", len(reply_raw), reply_raw)

    return Response(body=reply_raw, status_code=200,
                    headers={'Content-Type': DNS_MESSAGE_TYPE})
