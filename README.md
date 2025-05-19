# 😴 Wake Me Up

Small client/server that lets you remotely wake up a computer using [Wake-on-LAN](https://en.wikipedia.org/wiki/Wake-on-LAN)

## Usage

1. Create TLS/SSL certificates for your domain if you have not already done so. You can use the `create_cert.sh` script to help you if you do not already have a certificate. To use this script, first make a copy of `openssl.cnf.template` and rename it to `openssl.cnf`. You can configure this file to adjust your certificate. Afterwards, run `create_cert.sh` to generate the certificate using the `openssl` cli. If you're on Windows, you can get access to the `openssl` cli by running the `create_cert.sh` script in Git bash. 

2. Duplicate the `.env.template` and `.config.json.template` files, and remove the `.template` from the ends of the duplicated files. Inside the `.env` file, you can configure the password used to authenticate users of the server. The `.env` file should be shared with both the servers and the client computers. You can use `config.json` to configure the computers that the server is allowed to wake up.

3. Move the `.cert` and `.key` files to the server, and run `server.py` on the server to host the server.

4. Move the `.cert` file to the client, and run `client.py` on the client to connect to the server.

## Developing

Requirements
- Python 3.11.5

It's recommended to use a [Python virtual environment](https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/) to avoid package conflicts with your global Python packages.
First, create a virtual environment.

```bash
python -m venv .venv
```

Then, activate the virtual environment, which causes any packages you install to be installed locally, as well as letting Python know to look for packages locally.

```bash
.venv\Scripts\activate
```

Finally, make sure to install the packages from the `requirements.txt`

```bash
python -m pip install -r requirements.txt
```

To exit the virtual environment, run

```bash
deactivate
```
