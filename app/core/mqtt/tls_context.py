import ssl


def create_tls_context():
    ctx = ssl.create_default_context(cafile="/app/certs/ca.crt")
    ctx.load_cert_chain(
        certfile="/app/app/ca/client.crt",
        keyfile="/app/app/ca/client.key"
    )
    return ctx
