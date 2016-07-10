from artificer.tests.base_tests import BaseTest

class TestArtifacts(BaseTest):

    def setUp(self):
        super(TestArtifacts, self).setUp()
        self.init_database()

    def test_load_artifact(self):
        from artificer.models import Artifact
        count = self.db_session.query(Artifact).count()
        self.assertEqual(count, 3)

    def test_query_artifact(self):
        from artificer.models import Artifact
        artifact = self.db_session.query(Artifact).filter_by(name='TestArtifact1').one()
        self.assertEqual(artifact.name, 'TestArtifact1')
        self.assertEqual(artifact.author.name, 'admin')

    def test_delete_artifact(self):
        from artificer.models import Artifact
        artifact = self.db_session.query(Artifact).filter_by(name='TestArtifact1').one()
        self.db_session.delete(artifact)
        count = self.db_session.query(Artifact).filter_by(name='TestArtifact1').count()
        self.assertEqual(count, 0)

    def test_replace_all_artifacts(self):
        from artificer.lib.artifacts import get_artifact
        from artificer.models import Artifact
        from artifacts import reader
        artifact_reader = reader.YamlArtifactsReader()
        count = self.db_session.query(Artifact).filter(Artifact.author.has(name='admin')).count()
        self.assertEqual(count, 2)
        for forensic_artifact in artifact_reader.ReadDirectory( 'test_data', extension='yaml'):
            artifact = get_artifact(self.db_session, forensic_artifact, author='admin', replace=True)
            self.db_session.add(artifact)
        count = self.db_session.query(Artifact).filter(Artifact.author.has(name='admin')).count()
        self.assertEqual(count, 3)

    def test_replace_some_artifacts(self):
        from artificer.lib.artifacts import get_artifact
        from artificer.models import Artifact
        from artifacts import reader
        artifact_reader = reader.YamlArtifactsReader()
        count = self.db_session.query(Artifact).filter(Artifact.author.has(name='user')).count()
        self.assertEqual(count, 1)
        for forensic_artifact in artifact_reader.ReadFile( 'test_data/test_artifacts_admin.yaml'):
            artifact = get_artifact(self.db_session, forensic_artifact, author='user', replace=True)
            self.db_session.add(artifact)
        count = self.db_session.query(Artifact).filter(Artifact.author.has(name='user')).count()
        self.assertEqual(count, 3)

    def test_change_artifact_author(self):
        from artificer.models import Artifact, User
        artifact = self.db_session.query(Artifact).filter_by(name='TestArtifact1').one()
        self.assertEqual(artifact.author.name, 'admin')
        author = self.db_session.query(User).filter_by(name='user').one()
        artifact.author = author
        artifact = self.db_session.query(Artifact).filter_by(name='TestArtifact1').one()
        self.assertEqual(artifact.author.name, 'user')
