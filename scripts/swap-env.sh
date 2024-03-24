#!/bin/bash

# Check if .env and .env.other files exist
if [ ! -f .env ] || [ ! -f .env.other ]; then
  echo "Error: .env and .env.other files must exist."
  exit 1
fi

# Create .env.temp file
touch .env.temp

# Copy contents of .env to .env.temp
cp .env .env.temp

# Copy contents of .env.other to .env
cp .env.other .env

# Copy contents of .env.temp to .env.other
cp .env.temp .env.other

# Delete .env.temp file
rm .env.temp

# Print the DEV field of .env
echo "CURRENT ENVIRONMENT: $(grep ENV .env | cut -d '=' -f2)"

echo "Successfully swapped .env and .env.other."