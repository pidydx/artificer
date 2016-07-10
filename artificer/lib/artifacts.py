import json

from sqlalchemy.orm.exc import NoResultFound
from artificer.models import User, Artifact, Label, SupportedOS, Source

from artificer.lib.errors import ArtifactAlreadyExists, MissingAuthor

import artifacts.definitions as fa_definitions
import artifacts.source_type as fa_sources

def get_artifact(db_session, forensic_artifact, author, replace=False):
    artifact_definition = json.dumps(forensic_artifact.AsDict())

    try:
        author = db_session.query(User).filter_by(name=author).one()
    except NoResultFound:
        raise MissingAuthor

    try:
        artifact = db_session.query(Artifact).filter_by(name=forensic_artifact.name).one()
        if not replace:
            raise ArtifactAlreadyExists
        else:
            artifact.author = author
            # TODO Fix data
            artifact.data = artifact_definition

    except NoResultFound:
        # TODO Fix data
        artifact = Artifact(name=forensic_artifact.name, author=author, data=artifact_definition)

    set_artifact_labels(db_session, artifact, forensic_artifact.labels)

    set_artifact_sources(db_session, artifact, forensic_artifact.sources)

    set_artifact_supported_os(db_session, artifact, forensic_artifact.supported_os)

    return artifact


def update_artifact(db_session, artifact, forensic_artifact, author='admin'):
    artifact_definition = json.dumps(forensic_artifact.AsDict())

    try:
        author = db_session.query(User).filter_by(name=author).one()
    except NoResultFound:
        raise MissingAuthor

    if artifact.name != forensic_artifact.name:
        if db_session.query(Artifact).filter_by(name=forensic_artifact.name).count():
            raise ArtifactAlreadyExists

    artifact.author = author
    artifact.name = forensic_artifact.name
    artifact.data = artifact_definition

    set_artifact_labels(db_session, artifact, forensic_artifact.labels)

    set_artifact_sources(db_session, artifact, forensic_artifact.sources)

    set_artifact_supported_os(db_session, artifact, forensic_artifact.supported_os)

    return artifact


def set_artifact_labels(db_session, artifact, labels):
    artifact.labels = []
    for label_name in labels:
        label = get_label(db_session, label_name, "")
        if label not in artifact.labels:
            artifact.labels.append(label)


def set_artifact_sources(db_session, artifact, sources):
    artifact.sources = []

    for source_data in sources:
        source_type = source_data.TYPE_INDICATOR
        source = get_source(db_session, source_type)
        if source not in artifact.sources:
            artifact.sources.append(source)


def set_artifact_supported_os(db_session, artifact, supported_os):
    artifact.supported_os = []

    # Add unique supported os to artifact
    for os_name in supported_os:
        supported_os = get_supported_os(db_session, os_name)
        artifact.supported_os.append(supported_os)


def init_sources(db_session):
    for source_type in fa_sources.SourceTypeFactory.GetSourceTypeIndicators():
        get_source(db_session, source_type)


def init_supported_os(db_session):
    for os_name in fa_definitions.SUPPORTED_OS:
        get_supported_os(db_session, os_name)


def init_labels(db_session):
    for label_name, label_desc in fa_definitions.LABELS.items():
        get_label(db_session, label_name, label_desc)


def get_label(db_session, label_name, label_desc):
    try:
        label = db_session.query(Label).filter_by(name=label_name).one()
    except NoResultFound:
        label = Label(name=label_name, desc=label_desc)
        db_session.add(label)

    return label


def get_source(db_session, source_type):
    try:
        source = db_session.query(Source).filter_by(type=source_type).one()
    except NoResultFound:
        source = Source(type=source_type)
        db_session.add(source)

    return source


def get_supported_os(db_session, os_name):
    try:
        supported_os = db_session.query(SupportedOS).filter_by(name=os_name).one()
    except NoResultFound:
        supported_os = SupportedOS(name=os_name)
        db_session.add(supported_os)

    return supported_os
