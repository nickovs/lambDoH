# lambDoH
#
# A DNS over HTTPS server that runs as an AWS Lambda function

from chalice import Chalice, Response, NotFoundError, BadRequestError
from base64 import b64decode

import dns.message
import dns.query

LAMBDOH_VERSION_STRING = "0.1.0"

DNS_MESSAGE_TYPE = 'application/dns-message'

app = Chalice(app_name='lambDoH')
# For some reason simply adding DNS_MESSAGE_TYPE to the list does not work
app.api.binary_types = ['*/*']

# We helpfully provide some version information
@app.route('/version')
def index():
    return {'app': 'lambDoh',
            'version': LAMBDOH_VERSION_STRING}

# Support queries by GET
@app.route('/', methods=['GET'])
def dns_query_get():
    request = app.current_request
    # print(request.to_dict())
    b64_payload = request.query_params.get("dns")
    pad = "=" * ((-len(b64_payload)) % 4)
    return _dns_query_handle(b64decode(b64_payload + pad))

# Support queries by POST
@app.route('/',  methods=['POST'],
           content_types=[DNS_MESSAGE_TYPE])
def dns_query_post():
    request = app.current_request
    # print(request.to_dict())
    return _dns_query_handle(request.raw_body)

# Chalice-specific code for processing queries
def _dns_query_handle(query_raw):
    if not query_raw:
        raise BadRequestError("No dns query given")
    print("Query is {} bytes: {}".format(len(query_raw), query_raw))

    reply_raw = resolve_dns_query(query_raw)

    print("Reply is {} bytes: {}".format(len(reply_raw), reply_raw))
        
    return Response(body=reply_raw, status_code=200,
                    headers={'Content-Type': DNS_MESSAGE_TYPE} )


# Core DNS resolver code

# Process a DNS request packet and return the response packet
def resolve_dns_query(request_packet):
    query = dns.message.from_wire(request_packet)

    reply = dns.query.udp(query, "8.8.8.8")

    return reply.to_wire() if reply else b''
