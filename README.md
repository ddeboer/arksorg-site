# ARKSORG

Provides the arks.org website and ARK resolver service.

## Installation for Producton on AWS EC2

Prerequisites:
- pyenv
- python >= 3.9
- python poetry
- ruby, bundle, jekyll

Setup python pyenv
```
# install direnv, optional but helpful for automating python env invocation
curl -sfL https://direnv.net/install.sh | bash
# Install dependencies for python build
sudo yum install gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel
# Install pyenv
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> .bashrc_local
## restart shell
# install python 3.11
pyenv install 3.11
# set default python for shell
pyenv global 3.11
```

Install `jekyll` and `bundler`

```
sudo yum install ruby-devel
gem install jekyll bundler
```

Install `nginx unit`

unit.repo:
```
[unit]
name=unit repo
baseurl=https://packages.nginx.org/unit/amzn/2023/$basearch/
gpgcheck=0
enabled=1
```

Add the repo and install `unit`.
```
sudo yum-config-manager --add-repo unit.repo
sudo yum update
sudo yum install unit
sudo yum install unit-devel unit-python311
sudo systemctl restart unit
```


1. Checkout this repository:
```
git clone --recursive xxx
```

2. Build the site documents
```
cd arksorg/arks.github.io
bundle exec jekyll build --config _config.yml,../_config.local.yml
```

The generated documents are in the `site` folder of the root.


3. Setup a virtual environment and activate
```
python -m venv ${HOME}/venv
source ${HOME}/venv/bin/activate
```

4. Install dependencies
```
cd resolver
pip install -e .
```

5. Deploy `unit` application

```
export APP_ROOT="$(pwd)"
export APP_PORT="8880"
export DLR='$'
mkdir -p "${APP_ROOT}/resolver/rslv/data"
envsubst < unit.json.template | curl -X PUT --data-binary @- \
  --unix-socket /usr/local/var/run/unit/control.sock \
  http://localhost/config/
```
