# Steps for getting this on EC2
- EC2
  - Make sure the instance has a security group that will allow connections for nginx
  - https://www.nginx.com/blog/nginx-plus-on-amazon-ec2-getting-started/

- SSH into the server

```
ssh -i ~/keys/aws-ec2-key.pem ubuntu@ec2-34-219-155-24.us-west-2.compute.amazonaws.com
```

- Ubuntu
```
sudo apt-get update
sudo apt-get upgrade
```
- Python
``` 
sudo apt-get install python-pip
sudo apt-get install python-dev
sudo apt-get install build-essential
sudo apt-get install -y zlib1g-dev
sudo apt-get install -y libssl-dev
sudo apt-get install software-properties-common
```

* bashrc file

```
pip install --upgrade pip
pip install virtualenvwrapper
```

- ssh

```
ssh-keygen -t rsa -b 4096 -C "thetomcraig@icloud.com"
cat ~/.ssh/id_rsa.pub >> (clipboard)
```

* Clone the repo
* Setup the repo

```
virtualenv env
pip install -r requirements.txt
cd heron
```

* Manually copy the `local_settings.py` file
* Django

```
python manage.py migrate
```

* nginx

```
sudo apt-get install nginx
sudo service nginx start

# (If it errors)
sudo service nginx stop
sudo mkdir /etc/systemd/system/nginx.service.d
sudo systemctl daemon-reload
sudo service nginx start
```

- nginx user

```
sudo service nginx stop
sudo vim /etc/nginx/nginx.conf
```

* Change the first line to read: `user ubuntu ubuntu;`

- Configure the app

```
sudo vim /etc/nginx/sites-enabled/default
```

- Can change settings here, for example:

```
access_log  /home/ubuntu/testapp/nginx-access.log;
error_log  /home/ubuntu/testapp/nginx-error.log info;
```

- Gunicorn install

```
# activate the env for the django app
pip install gunicorn
```

- Gunicorn configure

```
vim start_gnicorn.sh
```

- Should look something like:

```
APPNAME=testapp
APPDIR=/home/ubuntu/$APPNAME/

LOGFILE=$APPDIR'gunicorn.log'
ERRORFILE=$APPFIR'gunicorn-error.log'

NUM_WORKERS=3

ADDRESS=127.0.0.1:8000

cd $APPDIR

source ~/.bashrc
workon $APPNAME

exec gunicorn $APPNAME.wsgi:application \
-w $NUM_WORKERS --bind=$ADDRESS \
--log-level=debug \
--log-file=$LOGFILE 2>>$LOGFILE  1>>$ERRORFILE &
```

- Start app

```
sudo chmod +x start_gunicorn.sh
./start_gunicorn.sh
```

## Resources
- https://medium.com/@srijan.pydev_21998/complete-guide-to-deploy-django-applications-on-aws-ubuntu-16-04-instance-with-uwsgi-and-nginx-b9929da7b716
