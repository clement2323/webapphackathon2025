curl -s https://deb.nodesource.com/setup_20.x | sudo bash
sudo apt install nodejs -y
npm install
pip install -r requirements.txt
npm run dev -- --port 5000 --host 0.0.0.0