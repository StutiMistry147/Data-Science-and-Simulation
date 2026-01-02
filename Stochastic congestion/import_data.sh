#!/bin/bash

DB_NAME="network_data.db"
CSV_FILE="network_traffic.csv"

rm -f $DB_NAME

sqlite3 $DB_NAME <<EOF
CREATE TABLE traffic (
    timestamp REAL,
    inter_arrival REAL,
    packet_size INTEGER
);
.mode csv
.import --skip 1 $CSV_FILE traffic
EOF

echo "Done! Data from $CSV_FILE has been loaded into $DB_NAME."
