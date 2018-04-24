ssh-keygen -t rsa -b 4096 -C "thetomcraig@icloud.com"
sudo cat ~/.ssh/id_rsa.pub
git clone git@github.com:thetomcraig/HERON.git
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
source ~/.bash_profile
apt install python-minimal
apt-get install build-essential
apt-get install -y zlib1g-dev
apt-get install -y libssl-dev
sudo apt-get install software-properties-common
sudo apt-add-repository universe
sudo apt-get update
sudo apt-get install python-pip
