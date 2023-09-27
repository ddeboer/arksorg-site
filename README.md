# ARKSORG

Provides the arks.org website and ARK resolver service.

## Installation

Prerequisites:
- pyenv
- python >= 3.9
- python poetry
- ruby, bundle, jekyll

Setup python
```
curl -sfL https://direnv.net/install.sh | bash
sudo yum install gcc zlib-devel bzip2 bzip2-devel readline-devel sqlite sqlite-devel openssl-devel tk-devel libffi-devel
git clone https://github.com/pyenv/pyenv.git ~/.pyenv
echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> .bashrc_local
## restart shell
pyenv install 3.11
pyenv global 3.11
python -m pip install poetry
```

Setup Jekyll

```
sudo yum install ruby-devel
gem install jekyll bundler
```

Setup nginx

```
sudo yum install gunicorn3
```

1. Checkout this repository:
```
git clone --recursive xxx
```

2. Build the site documents
```
cd arksorg/arks.github.io
bundle exec jekyll build --config _config.yml,_config.local.yml
```

3. Setup a virtual environment and activate
```
python -m venv ${HOME}/venv
source ${HOME}/venv/bin/activate
```

4. Install dependencies