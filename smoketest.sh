#!/bin/bash

# Define the base URL for the Flask API
BASE_URL="http://localhost:5002/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Health Checks
#
###############################################

check_health() {
  echo "Checking health status..."
  response=$(curl -s -X GET "$BASE_URL/health")
  if echo "$response" | grep -q '"status": "healthy"'; then
    echo "Service is healthy."
  else
    echo "Health check failed. Response: $response"
    exit 1
  fi
}

check_api() {
  echo "Checking API status"
  TEST_URL="$BASE_URL/health"
  response=$(curl -s -X GET "$TEST_URL")
  if echo "$response" | grep -q '"status": "healthy"'; then
    echo "api connection is healthy"
  else
    echo "api check failed. Response: $response"
    exit 1
  fi
}

check_db() {
  echo "Checking database connection..."
  response=$(curl -s -X GET "$BASE_URL/db-check")
  if echo "$response" | grep -q '"database_status": "healthy"'; then
    echo "Database connection is healthy."
  else
    echo "Database check failed. Response: $response"
    exit 1
  fi
}

###############################################
#
# User Management
#
###############################################

create_user() {
  username=$1
  password=$2

  echo "Creating user ($username)..."
  response=$(curl -s -X POST "$BASE_URL/create-user" -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"password\":\"$password\"}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "User created successfully."
  else
    echo "Failed to create user. Response: $response"
    exit 1
  fi
}

delete_user() {
  username=$1

  echo "Deleting user ($username)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-user/$username")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "User deleted successfully."
  else
    echo "Failed to delete user. Response: $response"
    exit 1
  fi
}

###############################################
#
# Location Management
#
###############################################

create_location() {
  city=$1
  latitude=$2
  longitude=$3

  echo "Creating location ($city)..."
  response=$(curl -s -X POST "$BASE_URL/create-location" -H "Content-Type: application/json" \
    -d "{\"city\":\"$city\", \"latitude\":$latitude, \"longitude\":$longitude}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Location created successfully."
  else
    echo "Failed to create location. Response: $response"
    exit 1
  fi
}

get_location() {
  location_id=$1

  echo "Getting location by ID ($location_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-location/$location_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Location retrieved successfully."
  else
    echo "Failed to get location. Response: $response"
    exit 1
  fi
}

###############################################
#
# Weather and Air Quality
#
###############################################

get_weather() {
  location_id=$1

  echo "Getting weather for location ID ($location_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-weather/$location_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Weather data retrieved successfully."
  else
    echo "Failed to get weather. Response: $response"
    exit 1
  fi
}

get_air_quality() {
  location_id=$1

  echo "Getting air quality for location ID ($location_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-air-quality/$location_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Air quality data retrieved successfully."
  else
    echo "Failed to get air quality. Response: $response"
    exit 1
  fi
}

###############################################
#
# Favorites Management
#
###############################################

add_favorite() {
  user_id=$1
  location_id=$2

  echo "Adding location ID ($location_id) to user ID ($user_id)'s favorites..."
  response=$(curl -s -X POST "$BASE_URL/add-favorite" -H "Content-Type: application/json" \
    -d "{\"user_id\":$user_id, \"location_id\":$location_id}")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Location added to favorites successfully."
  else
    echo "Failed to add location to favorites. Response: $response"
    exit 1
  fi
}

get_favorites() {
  user_id=$1

  echo "Getting favorites for user ID ($user_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-favorites/$user_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Favorites retrieved successfully."
  else
    echo "Failed to get favorites. Response: $response"
    exit 1
  fi
}

remove_favorite() {
  user_id=$1
  location_id=$2

  echo "Removing location ID ($location_id) from user ID ($user_id)'s favorites..."
  response=$(curl -s -X DELETE "$BASE_URL/remove-favorite/$user_id/$location_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Location removed from favorites successfully."
  else
    echo "Failed to remove location from favorites. Response: $response"
    exit 1
  fi
}

###############################################
#
# Test Execution
#
###############################################

# Health Checks
check_api
check_health
check_db

# User Management
create_user "testuser" "password123"
delete_user "testuser"

# Location Management
create_location "Boston" 42.3601 -71.0589
get_location 1

# Weather Retrieval

# Favorites Management
add_favorite 1 1
get_favorites 1
remove_favorite 1 1

echo "All tests passed successfully!"
