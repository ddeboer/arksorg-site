# ARKSORG

Provides the arks.org website and ARK resolver service.

## Installation on AWS EC2

Deployment and configuration is performed by a combination of puppet and ansible.
These provide a deployment of arks.org on AWS EC2 instance listening on HTTP port 18880.

See UC3 Puppet module [`uc3_ezid_arks`](https://github.com/CDLUC3/uc3-ops-puppet-modules/tree/main/modules/uc3_ezid_arks) and ansible playbook [`deploy_arksorg_site`](./ansible/README.md).

For manual installation notes see [Manual Installation on AWS EC2](./ansible/notes/original_manual_deployment_notes.md).

