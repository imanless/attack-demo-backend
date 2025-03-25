if ! dpkg -l | grep -q apache2; then
    echo "Apache2 is not installed. Installing now..."
    sudo apt-get update
    sudo apt-get install apache2 -y
else
    echo "Apache2 is installed."
fi


cd ReadMine-Mirai-Demo-Files/release
sudo mkdir -p /var/www/html/bins
sudo cp mirai.* /var/www/html/bins
sudo cp bins.sh /var/www/html/bins

#very important, for 'others' the files must be executable in order to download them
sudo chmod 755 /var/www/html/bins/*

if [ -f /var/www/html/index.html ]; then
    sudo rm /var/www/html/index.html
fi
sudo service apache2 start

echo "Done"

