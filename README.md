# lambDoH

*lambDoH* is a simple DNS over HTTPS server that runs as an AWS Lambda service. It is designed to provide an easy way to deploy your own DNS over HTTPS solution that allows users to have more control of the privacy of their DNS lookups.

### Why *lambDoH*?

Regular DNS lookups are transmitted in the clear, allowing ISPs and others with network access to see which domains you look look up. DNS over HTTPS (DoH) is designed to proivide a confidential channel for transmitting DNS requests and receiving their responses, but it requires users to send all of their DNS requests through a single server, which means that the provider of this service can monitor all of the users' requests. Running your own DoH server allows you to control that choke point.

### Deployment

In most cases, assuming that you have your AWS credentials set up correctly, deployment should be as easy as:

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

The `Rest API URL` value can now be used directly as the DoH service address.

### Development status

This code is still sort of experimental. Notably it lacks the ability to configure which recursive DNS resolver will be used by the server (right now it's hardwired to Google's 8.8.8.8 server).
