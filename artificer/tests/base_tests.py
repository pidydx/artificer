import unittest
import transaction
import os

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from pyramid import testing
from artifacts import reader as fa_readers

class BaseTest(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp(settings={
            'sqlalchemy.url': 'sqlite:///:memory:'
        })
        self.config.include('artificer.models')
        settings = self.config.get_settings()

        from artificer.models import (
            get_engine,
            get_session_factory,
            get_tm_session,
            )

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)

        self.db_session = get_tm_session(session_factory, transaction.manager)

    def init_database(self):
        from artificer.models.meta import Base
        from artificer.models import User
        from artificer.lib.artifacts import get_artifact, init_labels, init_sources, init_supported_os

        Base.metadata.create_all(self.engine)

        init_labels(self.db_session)
        init_supported_os(self.db_session)
        init_sources(self.db_session)

        self.db_session.add(User(name='admin', fullname='admin', password='admin'))
        self.db_session.add(User(name='user', fullname='user', password='user'))
        artifact_reader = fa_readers.YamlArtifactsReader()
        for forensic_artifact in artifact_reader.ReadFile('test_data/test_artifacts_admin.yaml'):
            artifact = get_artifact(self.db_session, forensic_artifact, author='admin', replace=True)
            self.db_session.add(artifact)

        for forensic_artifact in artifact_reader.ReadFile( 'test_data/test_artifacts_user.yaml'):
            artifact = get_artifact(self.db_session, forensic_artifact, author='user', replace=True)
            self.db_session.add(artifact)


    def tearDown(self):
        from artificer.models.meta import Base

        testing.tearDown()
        transaction.abort()
        Base.metadata.drop_all(self.engine)


class ArtifactFileUpload(object):
    def __init__(self, filepath):
        with open(filepath, 'r') as fd:
            yaml_data = fd.read()
        self.filename = os.path.basename(filepath)
        self.file = StringIO(yaml_data)
