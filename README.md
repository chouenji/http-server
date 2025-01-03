# Mini HTTPS Server in Python

This project sets up a simple HTTPS server using Python and SSL.

## SSL

To generate a self-signed SSL certificate, run the following command:

```bash
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

## Running the program
Run python3 main.py  Http-server and Https-server
