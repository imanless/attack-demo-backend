if ! command -v apache2 &> /dev/null
then
    echo "Insatlling Apache2"
    sudo apt-get update
    sudo apt-get install apache2 -y
else
    echo "Apache2 is installed"
fi



cd ReadMine-Mirai-Demo-Files/release
mkdir /var/www/html/bins
cp mirai.* /var/www/html/bins
cp bins.sh /var/www/html/bins
rm /var/www/html/index.html

sudo service apache2 start

echo "Done"

