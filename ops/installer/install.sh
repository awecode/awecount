#!/bin/bash


# Clone the repository
git clone https://github.com/awecode/awecount.git

# Copy the .env.example.docker-compose file to .env
cp .env.example.docker-compose .env

# Ask for the domain name
read -p "Enter the domain name: " domain

# Replace the domain name in the .env file
sed -i "s/APP_URL=.*/APP_URL=$domain/" .env

# Ask for the database password- suggest leave blank for new random password
read -p "Enter Postgres password for new awecount user (leave blank for new random password): " db_password
if [ -z "$db_password" ]; then
    db_password=$(openssl rand -base64 32)
    echo "Database password: $db_password"
fi

# Replace the database password in the .env file
sed -i "s/DB_PASSWORD=.*/DB_PASSWORD=$db_password/" .env

# Ask for the admin email - suggest [support@$domain]
read -p "Enter the admin email (leave blank for default: support@$domain): " admin_email

if [ -z "$admin_email" ]; then
    admin_email="support@$domain"
fi

# Replace the admin email in the .env file
sed -i "s/SERVER_EMAIL=.*/SERVER_EMAIL=$admin_email/" .env

# Ask for server email - from email address for outgoing emails - suggest the same as the admin email
read -p "Enter the server email (leave blank for $admin_email): " server_email

if [ -z "$server_email" ]; then
    server_email=$admin_email
fi

# Replace the server email in the .env file
sed -i "s/SERVER_EMAIL=.*/SERVER_EMAIL=$server_email/" .env

# Ask for email host
read -p "Enter the email host (leave blank for default: email-smtp.us-east-1.amazonaws.com): " email_host

if [ -z "$email_host" ]; then
    email_host="email-smtp.us-east-1.amazonaws.com"
fi

# Replace the email host in the .env file
sed -i "s/EMAIL_HOST=.*/EMAIL_HOST=$email_host/" .env

# Ask for email port
read -p "Enter the email port (leave blank for default: 587): " email_port

if [ -z "$email_port" ]; then
    email_port="587"
fi

# Replace the email port in the .env file
sed -i "s/EMAIL_PORT=.*/EMAIL_PORT=$email_port/" .env

# Ask for email use TLS
read -p "Use TLS for email? (y/n, default: y): " email_use_tls

if [ -z "$email_use_tls" ]; then
    email_use_tls="True"
elif [ "$email_use_tls" = "y" ]; then
    email_use_tls="True"
else
    email_use_tls="False"
fi

# Replace the email use TLS in the .env file
sed -i "s/EMAIL_USE_TLS=.*/EMAIL_USE_TLS=$email_use_tls/" .env

# Ask for email use SSL
read -p "Use SSL for email? (y/n, default: n): " email_use_ssl

if [ -z "$email_use_ssl" ]; then
    email_use_ssl="False"
elif [ "$email_use_ssl" = "y" ]; then
    email_use_ssl="True"
else
    email_use_ssl="False"
fi

# Replace the email use SSL in the .env file
sed -i "s/EMAIL_USE_SSL=.*/EMAIL_USE_SSL=$email_use_ssl/" .env

# Ask for email host user
read -p "Enter the email host user: " email_host_user