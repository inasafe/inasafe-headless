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
7. If you are not in production, you need to copy/paste the file `src/headless/celeryconfig_sample.py` to `src/headless/celeryconfig.py`
8. You should have `Celery workers` in Run Configurations. Check if it's running.
9. Run unit test, to make sure all is good: `make coverage-tests`


### Running Test
1. In `src/headless/celeryconfig.py`, there is `task_always_eager` variable. If it's set to True, it will run the unit test synchronously. If it's set to False, it will run the unit test asynchronously.
2. If you want to run asynchronously, you need to run `Celery Worker` in the Run configurations.
3. Travis has been set to run the unit test for both synchronously and asynchronously.
4. You can run the unit test in `src/headless/tasks/test/test_celery_task.py` like in the common unit test (i.e. right click and press run unittest in the test method/class).
5. If the unit test generate a result, you can access it in the `src/headless/tasks/test/data/result` directory. This directory is already mounted to the container to `INASAFE_OUTPUT_DIR=/home/headless/output`
6. You can delete all the result from the unit test by running `make clean-test-output` from the `deployment` directory.


### Available Tasks
1. Read metadata
    - **Input**: _layer_uri_ (uri to the layer)
    - **Output**: Dictionary of metadata
2. Run analysis
    - **Input**
        - hazard_layer_uri
        - exposure_layer_uri
        - aggregation_layer_uri
        - crs
    - **Output**
        ```python
        output = {
            'status': 0,
            'message': '',
            'outputs': {
                'output_layer_key_1': 'output_layer_path_1',
                'output_layer_key_2': 'output_layer_path_2',
            }
        }
        ```
3. Run multi exposure analysis
    - **Input**
        - hazard_layer_uri
        - exposure_layer_uri
        - aggregation_layer_uri
        - crs
    - **Output**
        ```python
        output = {
            'status': 0,
            'message': '',
            'outputs': {
                'exposure_1': {
                    'output_layer_key_11': 'output_layer_path_11',
                    'output_layer_key_12': 'output_layer_path_12',
                },
                'exposure_2': {
                    'output_layer_key_21': 'output_layer_path_21',
                    'output_layer_key_22': 'output_layer_path_22',
                },
                'multi_exposure_output_layer_key_1':
                    'multi_exposure_output_layer_path_1',
                'multi_exposure_output_layer_key_2':
                    'multi_exposure_output_layer_path_2',
            }
        }
        ```
4. Generate reports (with custom template)
    - **Input**
        - impact_layer_uri
        - custom_report_template_uri (optional)
    - **Output**
        ```python
        output = {
            'status': 0,
            'message': '',
            'output': {
                'html_product_tag': {
                    'action-checklist-report': u'path',
                    'analysis-provenance-details-report': u'path',
                    'impact-report': u'path',
                },
                'pdf_product_tag': {
                    'action-checklist-pdf': u'path',
                    'analysis-provenance-details-report-pdf': u'path',
                    'impact-report-pdf': u'path',
                    'inasafe-map-report-landscape': u'path',
                    'inasafe-map-report-portrait': u'path',
                },
                'qpt_product_tag': {
                    'inasafe-map-report-landscape': u'path',
                    'inasafe-map-report-portrait': u'path',
                }
            },
        }
        ```
5. Get generated reports
    - **Input**
        - impact_layer_uri
        - custom_report_template_uri (optional)
    - **Output**
        ```python
        output = {
            'status': 0,
            'message': '',
            'output': {
                'html_product_tag': {
                    'action-checklist-report': u'path',
                    'analysis-provenance-details-report': u'path',
                    'impact-report': u'path',
                },
                'pdf_product_tag': {
                    'action-checklist-pdf': u'path',
                    'analysis-provenance-details-report-pdf': u'path',
                    'impact-report-pdf': u'path',
                    'inasafe-map-report-landscape': u'path',
                    'inasafe-map-report-portrait': u'path',
                },
                'qpt_product_tag': {
                    'inasafe-map-report-landscape': u'path',
                    'inasafe-map-report-portrait': u'path',
                }
            },
        }
        ```
6. Generate contour
    1. **Input**: _layer_uri_
    2. **Output**: _contour_uri_

For more detail, please go to `src/headless/tasks/inasafe_wrapper.py`