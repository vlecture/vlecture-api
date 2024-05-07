# #!/bin/bash

# # Check if .env and .env.other files exist
# if [ ! -f .env ] || [ ! -f .env.other ]; then
#   echo "Error: .env and .env.other files must exist."
#   exit 1
# fi

# # Create .env.temp file
# touch .env.temp

# # Copy contents of .env to .env.temp
# cp .env .env.temp

# # Copy contents of .env.other to .env
# cp .env.other .env

# # Copy contents of .env.temp to .env.other
# cp .env.temp .env.other

# # Delete .env.temp file
# rm .env.temp

# # Print the DEV field of .env
# echo "CURRENT ENVIRONMENT: $(grep ENV .env | cut -d '=' -f2)"

# echo "Successfully swapped .env and .env.other."


#!/bin/bash

#!/bin/bash

# Function to check if a file exists
file_exists() {
  if [ ! -f "$1" ]; then
    echo "Error: File '$1' does not exist."
    exit 1
  fi
}

# Get the target environment from the first argument
target_env="$1"

# Define the base .env file
base_env=".env"

# Construct the target environment file name
target_env_file=".env.${target_env}"

# Check if both files exist
file_exists "$base_env"
file_exists "$target_env_file"

# Overwrite the content of .env with the target environment file
cp "$target_env_file" "$base_env"

# Print the current environment
current_env=$(grep ENV "$base_env" | cut -d '=' -f2)
echo "CURRENT ENVIRONMENT: $current_env"
echo "Successfully set .env with variables from $target_env_file."