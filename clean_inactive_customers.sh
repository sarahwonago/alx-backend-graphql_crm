#!/bin/bash

# Navigate to project root
cd "$(dirname "$0")/../.."

# Run Django shell command
deleted_count=$(python3 manage.py shell <<EOF
import datetime
from crm.models import Customer

cutoff = datetime.datetime.now() - datetime.timedelta(days=365)
inactive_customers = Customer.objects.filter(orders__isnull=True, created_at__lt=cutoff)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
EOF
)

# Log with timestamp
echo "$(date '+%Y-%m-%d %H:%M:%S') - Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt
