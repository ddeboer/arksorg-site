Ansible Playbook `deploy_arksorg_site`
=====================================

works in consort with puppet module `uc3_ezid_arks`(url)

designed to run on the local host, so puppet can run it


### Usage

   export ANSIBLE_STDOUT_CALLBACK=debug
   ansible-playbook -i hosts deploy_arksorg_site.yaml -CD
   ansible-playbook -i hosts deploy_arksorg_site.yaml



### Prereqs (deployed by puppet)

- installed nginx unit rpms:
  - unit
  - unit-devel
  - unit-python311

- python3.11 rpms from Amzn repo:
  - python3.11
  - python3.11-libs
  - python3.11-setuptools
  - python3.11-pip
  - python3.11-tkinter

- systemd dropin file for `unit.service`.  This provides:
  - service runs as group `ezid`
  - pid file group ownership as `ezid`
  - log file group ownership as `ezid`
  - unit service unix socket writable by `ezid`

- ansible binaries installed local to ezid user using `pip3.11`.

- ruby and bundler installed local to ezid user.  These are for building `arks.github.io` content.



