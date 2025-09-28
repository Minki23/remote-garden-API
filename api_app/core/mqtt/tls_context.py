import ssl


def create_tls_context():
    """
    Create and configure an SSL/TLS context for MQTT connections.

    Loads the CA certificate, backend certificate, and private key
    from predefined file paths in `/app/ca/`.

    Returns
    -------
    ssl.SSLContext
        Configured SSL context for secure MQTT communication.
    """
    ctx = ssl.create_default_context(cafile="/app/ca/ca.crt")
    ctx.load_cert_chain(
        certfile="/app/ca/backend.crt",
        keyfile="/app/ca/backend.key"
    )
    return ctx
