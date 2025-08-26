#!/usr/bin/env python3
import datetime
import logging
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

# Configure logging
LOG_FILE = "/tmp/order_reminders_log.txt"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
)

# GraphQL endpoint
transport = RequestsHTTPTransport(
    url="http://localhost:8000/graphql",
    verify=True,
    retries=3,
)

client = Client(transport=transport, fetch_schema_from_transport=True)

# Calculate date range (last 7 days)
today = datetime.date.today()
seven_days_ago = today - datetime.timedelta(days=7)

# GraphQL query
query = gql(
    """
    query GetRecentOrders($from: Date!, $to: Date!) {
      orders(filter: { orderDate_Gte: $from, orderDate_Lte: $to }) {
        id
        customer {
          email
        }
      }
    }
    """
)

params = {
    "from": seven_days_ago.isoformat(),
    "to": today.isoformat(),
}

try:
    result = client.execute(query, variable_values=params)
    orders = result.get("orders", [])

    for order in orders:
        order_id = order["id"]
        email = order["customer"]["email"]
        logging.info(f"Reminder: Order {order_id} for {email}")

    print("Order reminders processed!")

except Exception as e:
    logging.error(f"Error while fetching orders: {e}")
    print("Error occurred while processing reminders!")
