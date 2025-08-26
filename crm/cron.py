import datetime


def log_crm_heartbeat():
    """Logs a heartbeat message to confirm CRM app health."""
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive\n"
    with open("/tmp/crm_heartbeat_log.txt", "a") as f:
        f.write(message)

    # (Optional) GraphQL health check
    try:
        from gql import gql, Client
        from gql.transport.requests import RequestsHTTPTransport

        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql", verify=True, retries=1
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)
        query = gql(""" query { hello } """)
        result = client.execute(query)
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(f"{timestamp} GraphQL hello: {result.get('hello')}\n")
    except Exception as e:
        with open("/tmp/crm_heartbeat_log.txt", "a") as f:
            f.write(f"{timestamp} GraphQL check failed: {e}\n")
