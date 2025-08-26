import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport


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


def update_low_stock():
    """Runs GraphQL mutation to restock low-stock products and logs updates."""
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        verify=True,
        retries=2,
    )
    client = Client(transport=transport, fetch_schema_from_transport=True)

    mutation = gql(
        """
        mutation {
          updateLowStockProducts {
            updatedProducts {
              id
              name
              stock
            }
            message
          }
        }
        """
    )

    try:
        result = client.execute(mutation)
        data = result.get("updateLowStockProducts", {})
        updated = data.get("updatedProducts", [])
        message = data.get("message", "")

        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"{timestamp} - {message}\n")
            for product in updated:
                f.write(
                    f"   Product {product['name']} restocked to {product['stock']}\n"
                )

    except Exception as e:
        with open("/tmp/low_stock_updates_log.txt", "a") as f:
            f.write(f"{timestamp} - ERROR: {e}\n")
