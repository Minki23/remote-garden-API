import ssl


def create_tls_context():
    ctx = ssl.create_default_context(cafile="/app/ca/ca.crt")
    ctx.load_cert_chain(
        certfile="/app/ca/backend.crt",
        keyfile="/app/ca/backend.key"
    )
    return ctx
