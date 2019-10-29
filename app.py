# lambDoH

"""
A DNS over HTTPS server that runs as an AWS Lambda function
"""

from base64 import b64decode
import logging
import os
import sys

from chalice import Chalice, Response, BadRequestError
import dns.message
import dns.query

APP_NAME = "lambDoH"
LAMBDOH_VERSION_STRING = "0.1.1"

DNS_MESSAGE_TYPE = 'application/dns-message'

# Set up logging based on the LOG_LEVEL environment variable
LOG_LEVEL = getattr(logging,
                    os.environ.get('LOG_LEVEL', '').upper(),
                    logging.ERROR)
LOGGER = logging.getLogger(APP_NAME)
LOGGER.setLevel(LOG_LEVEL)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))

DNS_SERVER_LIST = os.environ.get('DNS_SERVERS', '8.8.8.8, 8.8.4.4')
DNS_SERVERS = [ip.strip() for ip in DNS_SERVER_LIST.split(',')]

# Chalice likes this the app name to be lower case, PyLint does not
# pylint: disable=invalid-name
app = Chalice(app_name='lambDoH')
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

    reply_raw = _resolve_dns_query(query_raw)

    LOGGER.debug("Reply is %s bytes: %s", len(reply_raw), reply_raw)

    return Response(body=reply_raw, status_code=200,
                    headers={'Content-Type': DNS_MESSAGE_TYPE})


# Core DNS resolver code

# Process a DNS request packet and return the response packet
# THIS IS WORK IN PROGRESS!!!
def _resolve_dns_query(request_packet):
    query = dns.message.from_wire(request_packet)
    LOGGER.info("Query details: %s", query.to_text())

    reply = dns.query.udp(query, DNS_SERVERS[0])
    if not reply:
        LOGGER.warning("No reply to query for %s", query)
    else:
        LOGGER.info("Reply details: %s", reply.to_text())

    return reply.to_wire() if reply else b''
