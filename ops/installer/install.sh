#!/bin/bash

# Clone the repository
# git clone https://github.com/awecode/awecount.git

# Copy the .env.example.docker-compose file to .env
cp .env.example.docker-compose .env

prompt_for_env() {
  local key="$1" message="$2" default_value_arg="$3" type="${4:-text}" doc_link="$5" secret_length="${6:-32}" yesno_default_pref="${7:-n}" custom_yes_value="$8" custom_no_value="$9" warning_if_empty="${10}"
  [[ -z "$key" || -z "$message" ]] && { echo "Usage: prompt_for_env KEY \"Prompt Message\" [DEFAULT] [TYPE] [DOC_LINK] [SECRET_LENGTH] [YESNO_DEFAULT] [YES_VALUE] [NO_VALUE] [\"Warning if empty\"]" >&2; return 1; }

  local C_RESET="" C_BOLD="" C_DIM="" C_GREEN="" C_YELLOW="" C_BLUE="" C_CYAN=""
  [[ -t 1 && -t 2 ]] && {
    C_RESET='\033[0m' C_BOLD='\033[1m' C_DIM='\033[2m' C_GREEN='\033[32m' C_YELLOW='\033[33m' C_BLUE='\033[34m' C_CYAN='\033[36m'
  }

  local prompt_string="" effective_default="" user_input="" final_value="" env_file=".env" temp_env_file=".env.tmp.$$" actual_yes_value="yes" actual_no_value="no"
  [[ -n "$custom_yes_value" ]] && { actual_yes_value="$custom_yes_value"; actual_no_value="${custom_no_value:-no}"; }

  prompt_string+="${C_BOLD}${C_CYAN}❯ ${message}${C_RESET}"

  case "$type" in
    secret)
      if [[ -z "$default_value_arg" || "$default_value_arg" == "GENERATE" ]]; then
        effective_default=$(LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c "$secret_length" 2>/dev/null)
        [[ -z "$effective_default" ]] && { echo -e "  ${C_YELLOW}⚠️ Warning: Failed to generate secret${C_RESET}" >&2; effective_default="GENERATION_FAILED"; }
        prompt_string+=" ${C_DIM}[default: <generated secret>]${C_RESET}"
      else
        effective_default="$default_value_arg"
        prompt_string+=" ${C_DIM}[default: <provided>]${C_RESET}"
      fi
      ;;
    yesno)
      local yn_prompt_suffix="" default_display=""
      if [[ "$yesno_default_pref" == "y" ]]; then
        yn_prompt_suffix="[Y/n]" default_display="y" effective_default="$actual_yes_value"
      else
        yn_prompt_suffix="[y/N]" default_display="n" effective_default="$actual_no_value"
      fi
      [[ -n "$default_value_arg" ]] && {
        effective_default="$default_value_arg"
        local lower_default_arg=$(echo "$default_value_arg" | tr '[:upper:]' '[:lower:]')
        local lower_actual_yes=$(echo "$actual_yes_value" | tr '[:upper:]' '[:lower:]')
        if [[ "$lower_default_arg" == "$lower_actual_yes" ]]; then
          default_display="y" yn_prompt_suffix="[Y/n]"
        else
          default_display="n" yn_prompt_suffix="[y/N]"
        fi
      }
      prompt_string+=" ${C_DIM}${yn_prompt_suffix} [default: ${default_display}]${C_RESET}"
      ;;
    *)
      [[ -n "$default_value_arg" ]] && { effective_default="$default_value_arg"; prompt_string+=" ${C_DIM}[default: ${effective_default}]${C_RESET}"; }
      ;;
  esac

  [[ -n "$doc_link" ]] && prompt_string+="\n  ${C_DIM}ℹ Docs: ${doc_link}${C_RESET}"
  prompt_string+="\n  ${C_GREEN}➜ ${C_RESET}"
  read -p "$(echo -e "${prompt_string}")" user_input

  if [[ -z "$user_input" ]]; then
    final_value="$effective_default"
    if [[ "$type" == "secret" && ("$default_value_arg" == "GENERATE" || -z "$default_value_arg") && "$final_value" != "GENERATION_FAILED" ]]; then
      echo -e "  ${C_DIM}Using generated secret.${C_RESET}" >&2
    elif [[ "$type" == "yesno" ]]; then
      echo -e "  ${C_DIM}Using default: '${final_value}'${C_RESET}" >&2
    elif [[ -n "$final_value" ]]; then
      echo -e "  ${C_DIM}Using default: '${final_value}'${C_RESET}" >&2
    elif [[ -n "$warning_if_empty" ]]; then
      echo -e "  ${C_YELLOW}⚠️ ${warning_if_empty}${C_RESET}" >&2
    fi
  else
    final_value="$user_input"
  fi

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
        echo -e "  ${C_YELLOW}⚠️ Invalid input ('$final_value'). Using default: '${effective_default}'${C_RESET}" >&2
        final_value="$effective_default"
      fi
    fi
  fi

  touch "$env_file" || { echo -e "  ${C_YELLOW}⚠️ Error: Cannot create $env_file${C_RESET}" >&2; echo "$final_value"; return 1; }
  export _PROMPT_KEY="$key" _PROMPT_VALUE="$final_value"
  awk 'BEGIN {key = ENVIRON["_PROMPT_KEY"]; value = ENVIRON["_PROMPT_VALUE"]; key_regex = "^[[:space:]]*" key "[[:space:]]*=.*$"; gsub(/\\/, "\\\\", value); gsub(/&/, "\\&", value); updated = 0} !/^([[:space:]]*#|$)/ && $0 ~ key_regex {print key "=" value; updated = 1; next} {print} END {if (!updated) print key "=" value}' "$env_file" > "$temp_env_file"
  local awk_status=$?
  unset _PROMPT_KEY _PROMPT_VALUE

  if [[ $awk_status -eq 0 ]]; then
    if mv "$temp_env_file" "$env_file"; then
      echo -e "  ${C_DIM}${C_GREEN}✓ Updated '$key' in $env_file${C_RESET}\n" >&2
    else
      echo -e "  ${C_YELLOW}⚠️ Error: Failed to move $temp_env_file to $env_file${C_RESET}\n" >&2
      rm -f "$temp_env_file"
    fi
  else
    echo -e "  ${C_YELLOW}⚠️ Error: awk failed to process $env_file (status: $awk_status)${C_RESET}\n" >&2
    rm -f "$temp_env_file"
  fi

  echo "$final_value"
}

APP_URL=$(prompt_for_env "APP_URL" "Enter the application URL" "http://localhost:8000")
prompt_for_env "SECRET_KEY" "App secret key?" "" "secret" "" 50
prompt_for_env "DEBUG" "Debug mode?" "True" "yesno" "" "" "y" "True" "False"
prompt_for_env "ALLOW_SIGNUP" "Allow signup?" "True" "yesno" "" "" "y" "True" "False"
prompt_for_env "POSTGRES_PASSWORD" "Postgres password?" "" "secret" "" 20

# Strip protocol and trailing slash from APP_URL
DOMAIN=$(echo "$APP_URL" | sed -e 's|^https\?://||' -e 's|/$||')
SERVER_EMAIL=$(prompt_for_env "SERVER_EMAIL" "Server email?" "support@$DOMAIN" "text")

prompt_for_env "DEFAULT_FROM_EMAIL" "Default from email?" "$SERVER_EMAIL" "text"

prompt_for_env "EMAIL_HOST" "Email host?" "email-smtp.us-east-1.amazonaws.com" "text"

prompt_for_env "EMAIL_PORT" "Email port?" "587" "text"

prompt_for_env "EMAIL_USE_TLS" "Email use TLS?" "True" "yesno" "" "" "y" "True" "False"

prompt_for_env "EMAIL_USE_SSL" "Email use SSL?" "False" "yesno" "" "" "n" "True" "False"

prompt_for_env "EMAIL_HOST_USER" "Email host user?" "" "text"

prompt_for_env "EMAIL_HOST_PASSWORD" "Email host password?" "" "text"

prompt_for_env "SENTRY_DSN" "Sentry DSN?" "" "text"
