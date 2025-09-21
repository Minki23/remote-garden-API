import ssl


def create_tls_context():
    ctx = ssl.create_default_context(cafile="/app/app/ca/ca.crt")
    ctx.load_cert_chain(
        certfile="/app/app/ca/backend.crt",
        keyfile="/app/app/ca/backend.key"
    )
    return ctx
