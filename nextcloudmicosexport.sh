#!/bin/bash

# activate virtual environment
source {{ nextcloud_micos_export_dir }}/venv/bin/activate

cd {{ nextcloud_micos_export_dir }}
python3 -m nextcloudmicosexport