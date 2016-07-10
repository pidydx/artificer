Artificer README
==================

Getting Started
---------------

1. $VENV/bin/pip install -e .
2. $VENV/bin/initialize_artificer_db development.ini
3. $VENV/bin/pserve development.ini

API Documentation
----------------

GET /api/artifacts - Returns index of all or filtered artifacts

    params: labels - list of labels to include
            supported_os - list of supported_os to include
            sources - list of source types to include
            authors - list of authors to include
POST /api/artifacts - Returns id of artifact created from artifact_data

    params: artifact_data (ForensicArtifact in JSON format)

GET /api/artifacts/{id} - Returns JSON of artifact with database {id}

DELETE /api/artifacts/{id} - Deletes artifact with database {id}

PUT /api/artifacts/{id} - Update artifact with database {id} with artifact_data

    params: artifact_data (ForensicArtifact in JSON format)

GET /api/labels - Returns index of all artifacys by label

GET /api/sources - Returns index of all artifacts by source types

GET /api/supported_os - Returns index of all artifacts by supported_os

PUT /api/import - Import artifacts from file. Returns JSON of ids of successful imports and names of failed imports

    params: replace(bool) - replace existing artifacts found in database
            artifact_file - file upload

GET /api/export - Export artifacts in YAML format by ids

    params: id - list of database ids to export

TODO
---
* User Authentication
* Authoring Control
* Export Script
* Import Script
* UI for View/Edit
