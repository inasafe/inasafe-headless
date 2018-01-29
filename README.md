# InaSAFE Headless

Run InaSAFE headlessly as docker container.

## Setup Development Environment

### Prerequisites:
- Running MacOS or Ubuntu 16.04/16.10
- Docker installed
- Ansible is installed (`pip install ansible` or `brew install ansible`)
- PyCharm professional is installed (versions: 2016.3, 2017.1, 2017.2, or 2017.3)


### Step by step
1. Clone this repository, and open it in PyCharm.
2. Configure specific options for your local system
   1. `cd inasafe-headless/deployment/ansible/development/group_vars`
   2. `cp all.sample.yml all.yml`
   3. Edit `all.yml` for this items:
      1. `remote_user` (your username)
      2. `remote_group` (your user's group) (usually your username on linux, "staff" on macos)
      3. `project_path` (the location of this project)
      4. `interpreters->inasafe-headless->ipaddress` (your IP address)
3. Go to deployment directory `cd inasafe-headless/deployment`
3. Run `make setup-ansible` to setup the environment, make sure to get no failed. Restart PyCharm if needed.
4. Run `make build`
5. Run `make up`
6. Open PyCharm preferences / options, and go to project interpreter. Make sure you have `InaSAFE Headless Container` as the remote python interpreter. You should make sure all python package is loaded also.
7. If you are not in production, you need to copy/paste the file `src/headless/tasks/celeryconfig_sample.py` to `src/headless/tasks/celeryconfig.py`
8. You should have `Celery workers` in Run Configurations. Check if it's running.
9. Run unit test, to make sure all is good: `make coverage-tests`