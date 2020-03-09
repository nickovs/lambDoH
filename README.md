# lambDoH

*lambDoH* is a simple DNS over HTTPS server that runs as an AWS Lambda service. It is designed to provide an easy way to deploy your own DNS over HTTPS solution that allows users to have more control of the privacy of their DNS lookups.

### Why *lambDoH*?

Regular DNS lookups are transmitted in the clear, allowing ISPs and others with network access to see which domains you look look up. DNS over HTTPS (DoH) is designed to proivide a confidential channel for transmitting DNS requests and receiving their responses, but it requires users to send all of their DNS requests through a single server, which means that the provider of this service can monitor all of the users' requests. Running your own DoH server allows you to control that choke point.

### Deployment

#### TL;DR

In most cases, assuming that you have your AWS credentials set up correctly and already have [`chalice`](https://chalice.readthedocs.io/en/latest/) installed, deployment should be as easy as:

```
chalice deploy
```

#### The details

Deploying `lambDoH` requires an [Amazon Web Services](https://aws.amazon.com) account. If you don't have an account you need to create one before continuing.

Before installing you also need to make sure that you have all of the necessary dependencies installed, including Python3.  (MacOS before Catalina defaulted to Python 2). You can do this by executing:

```
pip install chalice
pip install -r requirements.txt
```

In order to deploy with `chalice` you will need to have your AWS credentials configured. If you don't already have this set up it is [documented](https://chalice.readthedocs.io/en/latest/quickstart.html#credentials) in the in the `chalice` documentation.

By default `lambDoH` will be deployed on a development stage of your AWS API Gateway endpoint, with minimal logging and using the default AWS Domain Name Service servers. The configuration can be altered by editting the [`.chalice/config.json`](https://chalice.readthedocs.io/en/latest/topics/configfile.html) file. See the [configuration](#Configuration) section below for the `lambDoH`-specific environment variables.

Once you are happy with the configuration, `lambDoH` can be deployed bymoving to the source directory and using the command:
```
chalice deploy
```

This should result in output that looks similar to:
```
Creating deployment package.
Updating policy for IAM role: lambDoH-dev
Updating lambda function: lambDoH-dev
Updating rest API
Resources deployed:
  - Lambda ARN: arn:aws:lambda:us-east-1:012345678900:function:lambDoH-dev
  - Rest API URL: https://xyz123abcd.execute-api.us-east-1.amazonaws.com/api/
```

The `Rest API URL` value that you get can now be used directly as the DoH service address.

### Configuration

The server can be configured using environment variables that can be set in the AWS Lambda stage configuration (typically by editing the `.chalice/config.json` file). Currently the supported environment variables are:

* `LOG_LEVEL` can be set to one of `CRITICAL`, `ERROR`, `WARNING`, `INFO` or `DEBUG`. The default level is `ERROR`.
* `DNS_SERVERS` can be set to a comma-separated list of dotted IP addresses for DNS servers to use for the underlying lookup. If no configuration is given the server attempts to read the local `resolv.conf` file. If for some reason this can not be read it defaults to using Google's servers at `8.8.8.8` and `8.8.4.4`.
* `DNS_SHUFFLE` can be set to `1`, `yes` or `true` to indicate that the list of DNS servers should be shuffled before being used, otherwise they will be tried in the order in which they are listed in `DNS_SERVERS`. The default is not to shuffle the list.
* `DNS_TIMEOUT` can be set to a floating point number of seconds for the timeout of DNS requests sent to the recursive resolves. Note that setting a large value here can potentially lead to larger charges if a domain's DNS server is being unresponsive. The defaust is 5 seconds.

### Cost of operation

If you have access to Amazon's _Free Tier_ for AWS Lambda and AWS API Gateway then you can handle one million DNS queries a month without charge. Without the _Free Tier_, at the prices in effect as of 2019-11-01 in AWS's US-East region the cost will start at a little less than US$4.00 per million requests in low volume and go down to rather less than US$2.00 per million in large volume.

### Limitations and issues

At the moment the code can only use UDP DNS servers for the lookup. While this is what the vast majority of the world uses the vast majority of the time, it does mean that it's limited to 512 bytes for requests and replies. This can occasionally cause problems with lookups that might yield large replies (mostly a problem with DNS-SEC).

If the logging level is turned up to `DEBUG` level then the AWS Lambda log files will include details of the queries that are performed. This might be a privacy issue, depending on who has access to the log files.
