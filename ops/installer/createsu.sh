#!/bin/sh

# This script runs the Django createsuperuser command
# inside the running 'awecount-backend-1' Docker container.

echo "Attempting to run createsuperuser in container 'awecount-backend-1'..."
echo "You will be prompted for user details (username, email, password)."

# Execute the command
docker exec -it awecount-backend-1 uv run manage.py createsuperuser

# Check the exit status of the last command (docker exec)
exit_status=$?

if [ $exit_status -eq 0 ]; then
  echo "Command completed successfully."
else
  echo "Command failed with exit status $exit_status."
  echo "Make sure the container 'awecount-backend-1' is running and 'uv run manage.py createsuperuser' is a valid command inside it."
fi

# Exit the script with the same status code as the docker exec command
exit $exit_status