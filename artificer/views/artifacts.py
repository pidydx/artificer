import json

from pyramid.response import Response
from pyramid.view import view_config
import pyramid.exceptions

from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm.exc import NoResultFound

from artificer.models import Artifact, Label, SupportedOS, Source, User

from artificer.lib.artifacts import update_artifact, get_artifact
from artificer.lib.errors import ArtifactAlreadyExists, MissingAuthor

import artifacts.writer as fa_writers
import artifacts.reader as fa_readers
import artifacts.errors as fa_errors

db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_artificer_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""

missing_author_err_msg = "Missing author"
artifact_exists_err_msg = "Artifact exists"
num_artifact_err_msg = "Must provide only one artifact_data parameter"
invalid_artifact_err_msg = "Invalid artifact sent"
invalid_file_err_msg = "Missing or invalid artifact yaml file"


@view_config(route_name='artifacts', renderer='json')
def artifacts_view(request):
    results = {'artifacts': []}
    label_filter = request.params.getall('labels')
    supported_os_filter = request.params.getall('supported_os')
    author_filter = request.params.getall('author')
    source_filter = request.params.getall('sources')

    try:
        artifacts = request.db_session.query(Artifact)
        if label_filter:
            artifacts = artifacts.filter(Artifact.labels.any(Label.name.in_(label_filter)))

        if supported_os_filter:
            artifacts = artifacts.filter(Artifact.supported_os.any(SupportedOS.name.in_(supported_os_filter)))

        if author_filter:
            artifacts = artifacts.filter(Artifact.author.has(User.name.in_(author_filter)))

        if source_filter:
            artifacts = artifacts.filter(Artifact.sources.any(Source.type.in_(source_filter)))

        for artifact in artifacts:
            results['artifacts'].append({
                'name': artifact.name,
                'id': artifact.id,
                'author': artifact.author.name,
                'supported_os': [supported_os.name for supported_os in artifact.supported_os],
                'labels': [label.name for label in artifact.labels],
                'sources': [source.type for source in artifact.sources]
            })
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)

    return results


@view_config(route_name='labels', renderer='json')
def labels_view(request):
    results = {'labels': []}
    try:
        labels = request.db_session.query(Label).all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)

    for label in labels:
        results['labels'].append({
            'name': label.name,
            'artifacts': [{'id': artifact.id, 'name': artifact.name} for artifact in label.artifacts]
        })
    return results


@view_config(route_name='supported_os', renderer='json')
def supported_os_view(request):
    results = {'supported_os': []}
    try:
        supported_oss = request.db_session.query(SupportedOS).all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)

    for supported_os in supported_oss:
        results['supported_os'].append({
            'name': supported_os.name,
            'artifacts': [{'id': artifact.id, 'name': artifact.name} for artifact in supported_os.artifacts]
        })
    return results


@view_config(route_name='sources', renderer='json')
def sources_view(request):
    results = {'sources': []}
    try:
        sources = request.db_session.query(Source).all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)

    for source in sources:
        results['sources'].append({
            'type': source.type,
            'artifacts': [{'id': artifact.id, 'name': artifact.name} for artifact in source.artifacts]
        })
    return results


@view_config(route_name='authors', renderer='json')
def authors_view(request):
    results = {'authors': []}
    try:
        users = request.db_session.query(User).all()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)

    for user in users:
        results['authors'].append({
            'name': user.name,
            'artifacts': [{'id': artifact.id, 'name': artifact.name} for artifact in user.artifacts]
        })
    return results


@view_config(request_method='GET', route_name='artifact', renderer='json')
def artifact_view(request):
    artifact_id = request.matchdict.get('id')
    try:
        artifact = request.db_session.query(Artifact).filter_by(id=artifact_id).one()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    except NoResultFound:
        raise pyramid.exceptions.HTTPNotFound()

    return json.loads(artifact.data)


@view_config(request_method='DELETE', route_name='artifact', renderer='json')
def artifact_delete(request):
    artifact_id = request.matchdict.get('id')
    try:
        try:
            artifact = request.db_session.query(Artifact).filter_by(id=artifact_id).one()
        except NoResultFound:
            raise pyramid.exceptions.HTTPNotFound()
        request.db_session.delete(artifact)
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)

    return Response(content_type='text/plain', status=204)


@view_config(request_method='PUT', route_name='artifact', renderer='json')
def artifact_update(request):
    # TODO Fix author
    artifact_id = request.matchdict.get('id')
    artifact_reader = fa_readers.ArtifactsReader()

    try:
        artifact_definition = request.params.getone('artifact_data')
    except KeyError:
        return Response(num_artifact_err_msg, content_type='text/plain', status=500)

    try:
        forensic_artifact = artifact_reader.ReadArtifactDefinitionValues(artifact_definition)
    except fa_errors.FormatError:
        return Response(invalid_artifact_err_msg, content_type='text/plain', status=500)

    try:
        try:
            artifact = request.db_session.query(Artifact).filter_by(id=artifact_id).one()
        except NoResultFound:
            raise pyramid.exceptions.HTTPNotFound()

        try:
            update_artifact(request.db_session, artifact=artifact, forensic_artifact=forensic_artifact, author='admin')
            request.db_session.add(artifact)
        except ArtifactAlreadyExists:
            return Response(artifact_exists_err_msg, content_type='text/plain', status=500)
        except MissingAuthor:
            return Response(missing_author_err_msg, content_type='text/plain', status=500)

    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)

    return Response(content_type='text/plain', status=204)


@view_config(request_method='POST', route_name='artifacts', renderer='json')
def artifact_create(request):
    # TODO Fix author
    artifact_reader = fa_readers.ArtifactsReader()

    try:
        artifact_definition = request.params.getone('artifact_data')
    except KeyError:
        return Response(num_artifact_err_msg, content_type='text/plain', status=500)

    try:
        forensic_artifact = artifact_reader.ReadArtifactDefinitionValues(artifact_definition)
    except fa_errors.FormatError:
        return Response(invalid_artifact_err_msg, content_type='text/plain', status=500)

    try:
        artifact = get_artifact(request.db_session, forensic_artifact, author='admin')
        request.db_session.add(artifact)
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    except ArtifactAlreadyExists:
        return Response(artifact_exists_err_msg, content_type='text/plain', status=500)
    except MissingAuthor:
        return Response(missing_author_err_msg, content_type='text/plain', status=500)
    return Response(content_type='application/json; charset=UTF-8',
                    body={'id': artifact.id},
                    status=200)


@view_config(route_name='export_artifacts', renderer='string')
def artifact_export_view(request):
    forensic_artifacts = []
    artifact_reader = fa_readers.ArtifactsReader()
    artifact_writer = fa_writers.YamlArtifactsWriter()
    artifact_ids = request.params.getall('id')

    if not artifact_ids:
        return ""

    try:
        artifacts = request.db_session.query(Artifact).filter(Artifact.id.in_(artifact_ids))
        for artifact in artifacts:
            artifact_definition = json.loads(artifact.data)
            forensic_artifacts.append(artifact_reader.ReadArtifactDefinitionValues(artifact_definition))
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)

    return artifact_writer.FormatArtifacts(forensic_artifacts)


@view_config(route_name='import_artifacts', renderer='json')
def artifact_import(request):
    # TODO Fix Author
    replace = request.params.get('replace', False)
    artifact_file = request.params.get('artifact_file')
    if not artifact_file.file:
        return Response(invalid_file_err_msg, content_type='text/plain', status=500)
    artifact_ids = []
    failed_artifacts = []
    artifact_reader = fa_readers.YamlArtifactsReader()

    # TODO Catch bad file reads

    for forensic_artifact in artifact_reader.ReadFileObject(artifact_file.file):
        try:
            artifact = get_artifact(request.db_session, forensic_artifact, author='admin', replace=replace)
            request.db_session.add(artifact)
            artifact_ids.append(artifact.id)
        except DBAPIError:
            return Response(db_err_msg, content_type='text/plain', status=500)
        except ArtifactAlreadyExists:
            failed_artifacts.append(forensic_artifact.name)
        except MissingAuthor:
            return Response(missing_author_err_msg, content_type='text/plain', status=500)

    if artifact_ids:
        return Response(content_type='application/json; charset=UTF-8',
                        body={'ids': artifact_ids, 'failed': failed_artifacts},
                        status=200)
    elif failed_artifacts:
        return Response(artifact_exists_err_msg, content_type='text/plain', status=500)
