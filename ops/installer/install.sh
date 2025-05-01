#!/bin/bash
# Or #!/bin/zsh

# Function to prompt user for input and update/append to a .env file.
# Provides features like default values, yes/no handling (with custom output),
# secret generation, documentation links, warnings for empty input,
# and a colorful CLI experience.
#
# Usage:
#   variable_value=$(prompt_for_env KEY "Prompt Message" [DEFAULT] [TYPE] [DOC_LINK] [SECRET_LENGTH] [YESNO_DEFAULT] [YES_VALUE] [NO_VALUE] ["Warning if empty"])
#
# Parameters:
#   $1: KEY           (Required) The environment variable key (e.g., DATABASE_URL).
#   $2: "Prompt Message" (Required) The message displayed to the user.
#   $3: DEFAULT       (Optional) The default value *to be saved* if the user provides no input.
#                                For type='secret', set to "GENERATE" or leave empty to auto-generate.
#                                For type='yesno', should correspond to one of the effective yes/no values (e.g., "True", "1").
#                                If omitted for yesno, it's derived from YESNO_DEFAULT ($7).
#   $4: TYPE          (Optional) Input type: 'text' (default), 'yesno', 'secret'.
#   $5: DOC_LINK      (Optional) A URL to documentation related to the prompt.
#   $6: SECRET_LENGTH (Optional) Length for generated secrets (default: 32). Used only if type='secret'.
#   $7: YESNO_DEFAULT (Optional) Default choice for 'yesno' type: 'y' or 'n'. Determines prompt style [Y/n] or [y/N]
#                                and the default value if $3 is not provided. Defaults to 'n'.
#   $8: YES_VALUE     (Optional) Custom output value for 'yes' answer (e.g., "True", "1"). Used only if type='yesno'.
#                                Defaults to "yes".
#   $9: NO_VALUE      (Optional) Custom output value for 'no' answer (e.g., "False", "0"). Used only if type='yesno'.
#                                Defaults to "no".
#  $10: "Warning if empty" (Optional) A warning message displayed (in yellow) if the user provides no input AND there's no default value.
#
# Returns (via echo):
#   The final value (user input, default, or generated value) for ALL types, including secrets.
#   This value is printed to standard output and can be captured using command substitution $(...).
#   Informational messages (updates, warnings) are printed to stderr.
#
# Example:
#   DB_HOST=$(prompt_for_env "DATABASE_HOST" "Enter the database host" "localhost")
#   # Standard yes/no, default 'yes'
#   ENABLE_SSL=$(prompt_for_env "ENABLE_SSL" "Enable SSL?" "" "yesno" "" "" "y")
#   # Custom True/False for Python, default to True (explicitly set)
#   PYTHON_DEBUG=$(prompt_for_env "PYTHON_DEBUG" "Enable Python Debug Mode?" "True" "yesno" "" "" "y" "True" "False")
#   # Secret generation - ADMIN_PASSWORD variable will contain the secret
#   ADMIN_PASSWORD=$(prompt_for_env "APP_SECRET_KEY" "Generate an app secret key?" "GENERATE" "secret" "" 64)
#   # Text input with warning if left empty
#   ADMIN_EMAIL=$(prompt_for_env "ADMIN_EMAIL" "Enter admin email address" "" "text" "" "" "" "" "" "Warning: Admin notifications will not be sent if empty.")
#   # Use captured DB_HOST in a subsequent prompt default
#   DB_URL=$(prompt_for_env "DATABASE_URL" "Enter full database URL" "postgres://${DB_HOST}:5432/mydb")
#
prompt_for_env() {
  # --- Parameters ---
  local key="$1"
  local message="$2"
  local default_value_arg="$3" # Optional - The explicit default value passed by the caller
  local type="${4:-text}"      # Optional, default 'text'
  local doc_link="$5"         # Optional
  local secret_length="${6:-32}" # Optional, default 32 for type=secret
  local yesno_default_pref="${7:-n}" # Optional, 'y' or 'n' for type=yesno, default 'n'
  local custom_yes_value="$8" # Optional
  local custom_no_value="$9"  # Optional
  local warning_if_empty="${10}" # Optional - Warning message

  # --- Input Validation ---
  if [[ -z "$key" || -z "$message" ]]; then
    echo "Usage: prompt_for_env KEY \"Prompt Message\" [DEFAULT] [TYPE] [DOC_LINK] [SECRET_LENGTH] [YESNO_DEFAULT] [YES_VALUE] [NO_VALUE] [\"Warning if empty\"]" >&2
    return 1 # Exit function with error status
  fi

  # --- Colors and Styles ---
  local C_RESET="" C_BOLD="" C_DIM="" C_GREEN="" C_YELLOW="" C_BLUE="" C_CYAN=""
  # Check only if stderr (2) is a terminal for coloring prompts and status messages
  if [[ -t 2 ]]; then
    C_RESET='\033[0m'
    C_BOLD='\033[1m'
    C_DIM='\033[2m'      # Muted/Dim color
    C_GREEN='\033[32m'   # Green for success/input arrow
    C_YELLOW='\033[33m'  # Yellow for warnings
    C_BLUE='\033[34m'
    C_CYAN='\033[36m'    # Cyan for the main prompt message
  fi

  # --- Variables ---
  local prompt_string=""
  local effective_default="" # The actual value to use if user presses Enter
  local user_input=""
  local final_value="" # This variable will hold the value to be saved and echoed
  local env_file=".env"
  local temp_env_file=".env.tmp.$$" # Unique temp file using PID
  local actual_yes_value="yes" # Default output for yes
  local actual_no_value="no"   # Default output for no

  # --- Determine Actual Yes/No Values ---
  if [[ -n "$custom_yes_value" ]]; then
    actual_yes_value="$custom_yes_value"
    actual_no_value="${custom_no_value:-no}"
  fi

  # --- Build Prompt String ---
  prompt_string+="${C_BOLD}${C_CYAN}❯ ${message}${C_RESET}" # Bold Cyan for main question

  # Handle default value display and logic based on type
  case "$type" in
    secret)
      if [[ -z "$default_value_arg" || "$default_value_arg" == "GENERATE" ]]; then
         effective_default=$(LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c "$secret_length" 2>/dev/null)
         if [[ -z "$effective_default" ]]; then
             # Warning printed to stderr
             echo -e "  ${C_YELLOW}⚠️ Warning: Failed to generate secret (check /dev/urandom access).${C_RESET}" >&2
             effective_default="GENERATION_FAILED"
         fi
         prompt_string+=" ${C_DIM}[default: <generated secret>]${C_RESET}" # Dim hint
      else
         effective_default="$default_value_arg"
         prompt_string+=" ${C_DIM}[default: <provided>]${C_RESET}" # Dim hint
      fi
      ;;
    yesno)
      local yn_prompt_suffix=""
      local default_display=""

      if [[ "$yesno_default_pref" == "y" ]]; then
        yn_prompt_suffix="[Y/n]"
        default_display="y"
        effective_default="$actual_yes_value"
      else
        yn_prompt_suffix="[y/N]"
        default_display="n"
        effective_default="$actual_no_value"
      fi

      if [[ -n "$default_value_arg" ]]; then
         effective_default="$default_value_arg"
         local lower_default_arg=$(echo "$default_value_arg" | tr '[:upper:]' '[:lower:]')
         local lower_actual_yes=$(echo "$actual_yes_value" | tr '[:upper:]' '[:lower:]')
         if [[ "$lower_default_arg" == "$lower_actual_yes" ]]; then
             default_display="y"
             yn_prompt_suffix="[Y/n]"
         else
             default_display="n"
             yn_prompt_suffix="[y/N]"
         fi
      fi
      # Dim hint for yes/no default
      prompt_string+=" ${C_DIM}${yn_prompt_suffix} [default: ${default_display}]${C_RESET}"
      ;;
    *) # text type (default)
      if [[ -n "$default_value_arg" ]]; then
        effective_default="$default_value_arg"
        prompt_string+=" ${C_DIM}[default: ${effective_default}]${C_RESET}" # Dim hint
      else
        effective_default=""
      fi
      ;;
  esac

  # Add documentation link if provided (Dim)
  if [[ -n "$doc_link" ]]; then
    prompt_string+="\n  ${C_DIM}ℹ Docs: ${doc_link}${C_RESET}"
  fi

  # Add the input indicator line (Green arrow)
  prompt_string+="\n  ${C_GREEN}➜ ${C_RESET}"

  # --- Get User Input ---
  # Use read -p which prints the prompt string to stdout and reads input
  # Note: echo -e is needed if the prompt itself contains newlines (\n) before the read command.
  read -p "$(echo -e "${prompt_string}")" user_input

  # --- Determine Final Value ---
  if [[ -z "$user_input" ]]; then
    # User pressed Enter
    final_value="$effective_default"
    # Display confirmations or warnings to stderr
    if [[ "$type" == "secret" && ("$default_value_arg" == "GENERATE" || -z "$default_value_arg") && "$final_value" != "GENERATION_FAILED" ]]; then
       echo -e "  ${C_DIM}Using generated secret.${C_RESET}" >&2
    elif [[ "$type" == "yesno" ]]; then
        # Show the actual value being used
        echo -e "  ${C_DIM}Using default: '${final_value}'${C_RESET}" >&2
    elif [[ -n "$final_value" ]]; then # Default was used for text type
         echo -e "  ${C_DIM}Using default: '${final_value}'${C_RESET}" >&2
    elif [[ -n "$warning_if_empty" ]]; then # No input, no default, but warning provided
        echo -e "  ${C_YELLOW}⚠️ ${warning_if_empty}${C_RESET}" >&2
    fi
  else
    # User provided input
    final_value="$user_input"
  fi

  # --- Handle Yes/No Validation and Normalization ---
  if [[ "$type" == "yesno" ]]; then
    local lower_input=$(echo "$final_value" | tr '[:upper:]' '[:lower:]')
    if [[ "$lower_input" == "y" || "$lower_input" == "yes" ]]; then
      final_value="$actual_yes_value"
    elif [[ "$lower_input" == "n" || "$lower_input" == "no" ]]; then
      final_value="$actual_no_value"
    else
      local lower_actual_yes=$(echo "$actual_yes_value" | tr '[:upper:]' '[:lower:]')
      local lower_actual_no=$(echo "$actual_no_value" | tr '[:upper:]' '[:lower:]')

      if [[ "$lower_input" == "$lower_actual_yes" ]]; then
          final_value="$actual_yes_value"
      elif [[ "$lower_input" == "$lower_actual_no" ]]; then
          final_value="$actual_no_value"
      else
          # Invalid input, revert to effective default, print warning to stderr
          echo -e "  ${C_YELLOW}⚠️ Invalid input ('$final_value'). Using default: '${effective_default}'${C_RESET}" >&2
          final_value="$effective_default"
      fi
    fi
  fi

  # --- Update .env file ---
  touch "$env_file" || { echo -e "  ${C_YELLOW}⚠️ Error: Cannot create $env_file${C_RESET}" >&2; return 1; } # Return 1 on error

  export _PROMPT_KEY="$key"
  export _PROMPT_VALUE="$final_value" # Pass the actual value to awk
  awk '
    BEGIN {
        key = ENVIRON["_PROMPT_KEY"]
        value = ENVIRON["_PROMPT_VALUE"]
        key_regex = "^[[:space:]]*" key "[[:space:]]*=.*$"
        gsub(/\\/, "\\\\", value)
        gsub(/&/, "\\&", value)
        updated = 0
    }
    !/^([[:space:]]*#|$)/ && $0 ~ key_regex {
        print key "=" value
        updated = 1
        next
    }
    { print }
    END {
        if (!updated) {
            print key "=" value
        }
    }
  ' "$env_file" > "$temp_env_file"

  local awk_status=$?
  unset _PROMPT_KEY _PROMPT_VALUE # Clean up env vars

  # Check awk status and move temp file
  if [[ $awk_status -eq 0 ]]; then
      if mv "$temp_env_file" "$env_file"; then
          # Success message in Dim Green, followed by a newline for spacing
          echo -e "  ${C_DIM}${C_GREEN}✓ Updated '$key' in $env_file${C_RESET}\n" >&2
      else
          # Error message in Yellow
          echo -e "  ${C_YELLOW}⚠️ Error: Failed to move $temp_env_file to $env_file${C_RESET}\n" >&2
          rm -f "$temp_env_file"
          return 1 # Indicate failure
      fi
  else
      # Error message in Yellow
      echo -e "  ${C_YELLOW}⚠️ Error: awk failed to process $env_file (status: $awk_status)${C_RESET}\n" >&2
      rm -f "$temp_env_file"
      return 1 # Indicate failure
  fi

  # --- Return Value ---
  # Echo the final value to stdout. This will be captured by command substitution $(...).
  # Note: This WILL print secrets to stdout if captured.
  echo "$final_value"

  # Return success status code
  return 0
}

# --- Example Usage ---
# Note: Variables captured using $(...) will contain the actual value, including secrets.

# echo "Configuring App..."
# # Standard text input
# APP_URL=$(prompt_for_env "APP_URL" "Enter the application URL" "http://localhost:8000")

# # Standard yes/no, default 'yes' (derived from 'y' preference)
# ENABLE_LOGGING=$(prompt_for_env "ENABLE_LOGGING" "Enable basic logging?" "" "yesno" "" "" "y")

# # Custom True/False for Python, default 'False' (explicitly set)
# PYTHON_VERBOSE=$(prompt_for_env "PYTHON_VERBOSE" "Enable Python verbose mode?" "False" "yesno" "" "" "n" "True" "False")

# # Custom 1/0, default '1' (explicitly set, implies 'y' preference for display)
# USE_NEW_API=$(prompt_for_env "USE_NEW_API" "Use the new API endpoint?" "1" "yesno" "https://docs.example.com/api#new" "" "" "1" "0")

# # Text input with warning if left empty
# SMTP_PASS=$(prompt_for_env "SMTP_PASSWORD" "Enter SMTP password (leave blank if not using SMTP)" "" "text" "" "" "" "" "" "Warning: SMTP email sending will be disabled.")

# # Secret generation - ADMIN_PASSWORD variable will contain the secret
# ADMIN_PASSWORD=$(prompt_for_env "ADMIN_PASSWORD" "Set initial admin password (leave blank to generate)" "GENERATE" "secret" "" 20)


# echo "--- Configuration Summary ---"
# echo "App URL: $APP_URL"
# echo "Logging Enabled: $ENABLE_LOGGING"
# echo "Python Verbose: $PYTHON_VERBOSE"
# echo "Use New API: $USE_NEW_API"
# echo "SMTP Password Set: $( [[ -n $SMTP_PASS ]] && echo 'Yes' || echo 'No' )"
# # Avoid echoing sensitive values like passwords in real scripts
# # echo "Admin Password: $ADMIN_PASSWORD" # Uncommenting this would print the secret
# echo "Admin Password Set in .env: Yes"
# echo "-----------------------------"
# echo "Check the .env file for saved values."



# Clone the repository
# git clone https://github.com/awecode/awecount.git

# Copy the .env.example.docker-compose file to .env
cp .env.example.docker-compose .env


APP_URL=$(prompt_for_env "APP_URL" "Enter the application URL" "http://localhost:8000")
SECRET_KEY=$(prompt_for_env "SECRET_KEY" "App secret key?" "" "secret" "" 50)
DEBUG=$(prompt_for_env "DEBUG" "Debug mode?" "True" "yesno" "" "" "y" "True" "False")
ALLOW_SIGNUP=$(prompt_for_env "ALLOW_SIGNUP" "Allow signup?" "True" "yesno" "" "" "y" "True" "False")
POSTGRES_PASSWORD=$(prompt_for_env "POSTGRES_PASSWORD" "Postgres password?" "" "secret" "" 20)

# Strip protocol, trailing slash, www. if present, and port if present
DOMAIN=$(echo "$APP_URL" | sed -e 's|^https\?://||' -e 's|/$||' -e 's|^www\.||' -e 's|:[0-9]*$||')
SERVER_EMAIL=$(prompt_for_env "SERVER_EMAIL" "Server email?" "support@$DOMAIN" "text")
DEFAULT_FROM_EMAIL=$(prompt_for_env "DEFAULT_FROM_EMAIL" "Default from email?" "$SERVER_EMAIL" "text")
EMAIL_HOST=$(prompt_for_env "EMAIL_HOST" "Email host?" "email-smtp.us-east-1.amazonaws.com" "text")
EMAIL_PORT=$(prompt_for_env "EMAIL_PORT" "Email port?" "587" "text")
EMAIL_USE_TLS=$(prompt_for_env "EMAIL_USE_TLS" "Email use TLS?" "True" "yesno" "" "" "y" "True" "False")
EMAIL_USE_SSL=$(prompt_for_env "EMAIL_USE_SSL" "Email use SSL?" "False" "yesno" "" "" "n" "True" "False")
EMAIL_HOST_USER=$(prompt_for_env "EMAIL_HOST_USER" "Email host user? (leave blank if not using email)" "" "text" "" "" "" "" "" "Warning: SMTP email sending will be disabled.")
EMAIL_HOST_PASSWORD=$(prompt_for_env "EMAIL_HOST_PASSWORD" "Email host password? (leave blank if not using email)" "" "text" "" "" "" "" "" "Warning: SMTP email sending will be disabled.")
SENTRY_DSN=$(prompt_for_env "SENTRY_DSN" "Sentry DSN? (leave blank if not using Sentry)" "" "text")
