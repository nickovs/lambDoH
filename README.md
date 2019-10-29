# lambDoH

*lambDoH* is a simple DNS over HTTPS server that runs as an AWS Lambda service. It is designed to provide an easy way to deploy your own DNS over HTTPS solution that allows users to have more control of the privacy of their DNS lookups. Regular DNS lookups are transmitted in the clear, allowing ISPs and others with network access to see which domains you look look up. DNS over HTTPS (DoH) is designed to proivide a confidential channel for transmitting DNS requests and receiving their responses, but it requires users to send all of their DNS requests through a single server, which means that the provider of this service can monitor all of the users' requests. Running your own DoH server allows you to control that choke point.

### Deployment

In most cases, assuming that you have your AWS credentials set up correctly, deployment should be as easy as:

```
chalice deploy
```

Once this command completes it will print the URL of the API endpoint for the service. You can paste this URL into your DoH configuration
