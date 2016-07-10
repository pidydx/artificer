from artificer.tests.base_tests import BaseTest, ArtifactFileUpload

from pyramid import testing
from webob.multidict import MultiDict

import artifacts.definitions as fa_definitions
import artifacts.source_type as fa_sources
import artifacts.reader as fa_readers
import artifacts.artifact as fa_artifact

import pyramid.exceptions

from artificer.models import Artifact
import artificer.views.artifacts as artifact_views

TEST_ARTIFACT = {"urls": ["https://www.github.com/"],
                 "labels": ["Software"],
                 "name": "TestArtifact4",
                 "sources": [{"attributes": {"keys": ["HKEY_LOCAL_MACHINE\TEST"]}, "type": "REGISTRY_KEY"}],
                 "doc": "This artifact is for testing\n",
                 "supported_os": ["Darwin", "Linux"]
                 }


def dummy_request(db_session):
    request = testing.DummyRequest(db_session=db_session)
    request.params = MultiDict()
    return request


class TestArtifactsView(BaseTest):

    def setUp(self):
        super(TestArtifactsView, self).setUp()
        self.init_database()

    def test_list_all_artifacts(self):
        test_request = dummy_request(self.db_session)
        artifacts = artifact_views.artifacts_view(test_request)
        self.assertEqual(len(artifacts), 3)
        self.assertEqual(artifacts['TestArtifact1']['author'], 'admin')
        self.assertCountEqual(artifacts['TestArtifact1']['supported_os'], ['Windows', 'Linux'])
        self.assertCountEqual(artifacts['TestArtifact1']['labels'], ['Software'])

    def test_list_labeled_artifacts(self):
        test_request = dummy_request(self.db_session)
        test_request.params.add('labels', 'Software')
        artifacts = artifact_views.artifacts_view(test_request)
        self.assertEqual(len(artifacts), 2)
        self.assertCountEqual(artifacts.keys(), ['TestArtifact1', 'TestArtifact3'])

    def test_list_supported_os_artifacts(self):
        test_request = dummy_request(self.db_session)
        test_request.params.add('supported_os', 'Windows')
        artifacts = artifact_views.artifacts_view(test_request)
        self.assertEqual(len(artifacts), 1)
        self.assertCountEqual(artifacts.keys(), ['TestArtifact1'])

    def test_list_author_artifacts(self):
        test_request = dummy_request(self.db_session)
        test_request.params.add('author', 'user')
        artifacts = artifact_views.artifacts_view(test_request)
        self.assertEqual(len(artifacts), 1)
        self.assertCountEqual(artifacts.keys(), ['TestArtifact3'])

    def test_list_source_artifacts(self):
        test_request = dummy_request(self.db_session)
        test_request.params.add('sources', 'REGISTRY_KEY')
        artifacts = artifact_views.artifacts_view(test_request)
        self.assertEqual(len(artifacts), 1)
        self.assertCountEqual(artifacts.keys(), ['TestArtifact3'])

    def test_multifilter_artifacts(self):
        test_request = dummy_request(self.db_session)
        test_request.params.add('author', 'admin')
        test_request.params.add('labels', 'Software')
        artifacts = artifact_views.artifacts_view(test_request)
        self.assertEqual(len(artifacts), 1)
        self.assertCountEqual(artifacts.keys(), ['TestArtifact1'])

        test_request = dummy_request(self.db_session)
        test_request.params.add('author', 'user')
        test_request.params.add('labels', 'Configuration Files')
        artifacts = artifact_views.artifacts_view(test_request)
        self.assertEqual(len(artifacts), 0)

        test_request = dummy_request(self.db_session)
        test_request.params.add('supported_os', 'Darwin')
        test_request.params.add('labels', 'Software')
        artifacts = artifact_views.artifacts_view(test_request)
        self.assertEqual(len(artifacts), 1)
        self.assertCountEqual(artifacts.keys(), ['TestArtifact3'])

        test_request = dummy_request(self.db_session)
        test_request.params.add('author', 'user')
        test_request.params.add('author', 'admin')
        artifacts = artifact_views.artifacts_view(test_request)
        self.assertEqual(len(artifacts), 3)
        self.assertCountEqual(artifacts.keys(), ['TestArtifact1', 'TestArtifact2', 'TestArtifact3'])


class TestLabelsView(BaseTest):

    def setUp(self):
        super(TestLabelsView, self).setUp()
        self.init_database()

    def test_list_all_labels(self):
        labels = artifact_views.labels_view(dummy_request(self.db_session))
        self.assertEqual(len(labels), len(fa_definitions.LABELS))
        self.assertEqual(len(labels['Configuration Files']), 1)
        self.assertEqual(len(labels['Software']), 2)


class TestSupportedOSView(BaseTest):

    def setUp(self):
        super(TestSupportedOSView, self).setUp()
        self.init_database()

    def test_list_all_supported_os(self):
        supported_os = artifact_views.supported_os_view(dummy_request(self.db_session))
        self.assertEqual(len(supported_os), 3)
        self.assertEqual(len(supported_os['Linux']), 3)
        self.assertEqual(len(supported_os['Darwin']), 2)
        self.assertEqual(len(supported_os['Windows']), 1)


class TestSourcesView(BaseTest):

    def setUp(self):
        super(TestSourcesView, self).setUp()
        self.init_database()

    def test_list_all_sources(self):
        sources = artifact_views.sources_view(dummy_request(self.db_session))
        self.assertEqual(len(sources), len(fa_sources.TYPE_INDICATORS))
        self.assertEqual(len(sources['FILE']), 2)
        self.assertEqual(len(sources['REGISTRY_KEY']), 1)


class TestAuthorsView(BaseTest):

    def setUp(self):
        super(TestAuthorsView, self).setUp()
        self.init_database()

    def test_list_all_sources(self):
        authors = artifact_views.authors_view(dummy_request(self.db_session))
        self.assertEqual(len(authors), 2)
        self.assertEqual(len(authors['admin']), 2)
        self.assertEqual(len(authors['user']), 1)


class TestArtifactView(BaseTest):

    def setUp(self):
        super(TestArtifactView, self).setUp()
        self.init_database()

    def test_view_artifact(self):
        artifact = self.db_session.query(Artifact).filter_by(name='TestArtifact1').one()
        test_request = dummy_request(self.db_session)
        test_request.matchdict['id'] = artifact.id
        response = artifact_views.artifact_view(test_request)
        print(response)
        self.assertEqual(response['name'], 'TestArtifact1')

    def test_view_artifact_failure(self):
        test_request = dummy_request(self.db_session)
        test_request.matchdict['id'] = 100
        with self.assertRaises(pyramid.exceptions.HTTPNotFound):
            artifact_views.artifact_view(test_request)


class TestArtifactDelete(BaseTest):

    def setUp(self):
        super(TestArtifactDelete, self).setUp()
        self.init_database()

    def test_delete_artifact_success(self):
        artifact = self.db_session.query(Artifact).filter_by(name='TestArtifact3').one()
        test_request = dummy_request(self.db_session)
        test_request.matchdict['id'] = artifact.id
        response = artifact_views.artifact_delete(test_request)
        self.assertEqual(response.status_code, 204)
        count = self.db_session.query(Artifact).filter_by(name='TestArtifact3').count()
        self.assertEqual(count, 0)

    def test_delete_artifact_missing_failure(self):
        test_request = dummy_request(self.db_session)
        test_request.matchdict['id'] = 5
        with self.assertRaises(pyramid.exceptions.HTTPNotFound):
            artifact_views.artifact_delete(test_request)


class TestArtifactUpdate(BaseTest):
    # TODO add author failure tests

    def setUp(self):
        super(TestArtifactUpdate, self).setUp()
        self.init_database()
        self.artifact = self.db_session.query(Artifact).filter_by(name='TestArtifact3').one()
        self.test_request = dummy_request(self.db_session)
        self.test_request.matchdict['id'] = self.artifact.id
        self.test_request.params.add('artifact_data', TEST_ARTIFACT)

    def test_update_artifact_success(self):
        # Update with name change
        response = artifact_views.artifact_update(self.test_request)
        self.assertEqual(response.status_code, 204)
        artifact = self.db_session.query(Artifact).filter_by(id=self.artifact.id).one()
        self.assertEqual(artifact.name, 'TestArtifact4')

        # Update with same name
        response = artifact_views.artifact_update(self.test_request)
        self.assertEqual(response.status_code, 204)

    def test_update_artifact_artifact_exists_failure(self):
        artifact_views.artifact_update(self.test_request)

        artifact = self.db_session.query(Artifact).filter_by(name='TestArtifact2').one()
        test_request = dummy_request(self.db_session)
        test_request.matchdict['id'] = artifact.id
        test_request.params.add('artifact_data', TEST_ARTIFACT)
        response = artifact_views.artifact_update(test_request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.artifact_exists_err_msg)

    def test_update_artifact_multi_artifact_failure(self):
        self.test_request.params.add('artifact_data', TEST_ARTIFACT)
        response = artifact_views.artifact_update(self.test_request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.num_artifact_err_msg)

    def test_update_artifact_missing_failure(self):
        test_request = dummy_request(self.db_session)
        test_request.matchdict['id'] = 5
        with self.assertRaises(pyramid.exceptions.HTTPNotFound):
            artifact_views.artifact_delete(test_request)

    def test_update_artifact_invalid_artifact_failure(self):
        test_request = dummy_request(self.db_session)
        test_request.params.add('artifact_data', {"name": "TestArtifact5"})
        response = artifact_views.artifact_update(test_request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.invalid_artifact_err_msg)


class TestArtifactCreate(BaseTest):

    def setUp(self):
        super(TestArtifactCreate, self).setUp()
        self.init_database()
        self.test_request = dummy_request(self.db_session)
        self.test_request.params.add('artifact_data', TEST_ARTIFACT)

    def test_create_artifact_success(self):
        response = artifact_views.artifact_create(self.test_request)
        self.assertEqual(response.status_code, 200)
        artifact = self.db_session.query(Artifact).filter_by(id=response.body['id']).one()
        self.assertEqual(artifact.name, 'TestArtifact4')

    def test_create_artifact_artifact_exists_failure(self):
        artifact_views.artifact_create(self.test_request)
        response = artifact_views.artifact_create(self.test_request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.artifact_exists_err_msg)

    def test_create_artifact_multi_artifact_failure(self):
        self.test_request.params.add('artifact_data', TEST_ARTIFACT)
        response = artifact_views.artifact_create(self.test_request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.num_artifact_err_msg)

    def test_create_artifact_invalid_artifact_failure(self):
        test_request = dummy_request(self.db_session)
        test_request.params.add('artifact_data', {"name": "TestArtifact5"})
        response = artifact_views.artifact_create(test_request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.invalid_artifact_err_msg)


class TestArtifactsExportView(BaseTest):
    def setUp(self):
        super(TestArtifactsExportView, self).setUp()
        self.init_database()

    def test_export_artifacts(self):
        artifact_reader = fa_readers.YamlArtifactsReader()
        test_request = dummy_request(self.db_session)
        test_request.params.add('id', 1)
        test_request.params.add('id', 2)
        response = artifact_views.artifact_export_view(test_request)
        for forensic_artifact in artifact_reader.ReadFileObject(response):
            self.assertIsInstance(forensic_artifact, fa_artifact.ArtifactDefinition)


class TestArtifactsImport(BaseTest):
    # TODO test bad/empty file failures
    def setUp(self):
        super(TestArtifactsImport, self).setUp()
        self.init_database()
        self.test_request = dummy_request(self.db_session)
        upload = ArtifactFileUpload('test_data/test_artifacts_import.upload')
        self.test_request.params.add('artifact_file', upload)

    def test_import_artifacts_create(self):
        response = artifact_views.artifact_import(self.test_request)
        self.assertEqual(response.status_code, 200)

        artifact = self.db_session.query(Artifact).filter_by(id=response.body['ids'][0]).one()
        self.assertEqual(artifact.name, 'TestArtifact5')
        supported_os = [supported_os.name for supported_os in artifact.supported_os]
        self.assertEqual(supported_os, ['Darwin'])

    def test_import_artifacts_replace(self):
        response = artifact_views.artifact_import(self.test_request)
        artifact = self.db_session.query(Artifact).filter_by(id=response.body['ids'][0]).one()
        supported_os = [supported_os.name for supported_os in artifact.supported_os]
        self.assertEqual(supported_os, ['Darwin'])
        upload = ArtifactFileUpload('test_data/test_artifacts_replace.upload')
        test_request = dummy_request(self.db_session)
        test_request.params.add('artifact_file', upload)
        test_request.params.add('replace', True)
        response = artifact_views.artifact_import(test_request)
        self.assertEqual(response.status_code, 200)
        artifact = self.db_session.query(Artifact).filter_by(name="TestArtifact5").one()
        supported_os = [supported_os.name for supported_os in artifact.supported_os]
        self.assertEqual(supported_os, ['Linux'])

    def test_import_artifacts_duplicate_failure(self):
        artifact_views.artifact_import(self.test_request)
        upload = ArtifactFileUpload('test_data/test_artifacts_replace.upload')
        test_request = dummy_request(self.db_session)
        test_request.params.add('artifact_file', upload)
        response = artifact_views.artifact_import(test_request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.artifact_exists_err_msg)

    def test_import_artifacts_partial_failure(self):
        artifact_views.artifact_import(self.test_request)
        upload = ArtifactFileUpload('test_data/test_artifacts_partial.upload')
        test_request = dummy_request(self.db_session)
        test_request.params.add('artifact_file', upload)
        response = artifact_views.artifact_import(test_request)
        self.assertEqual(response.status_code, 200)
        artifact = self.db_session.query(Artifact).filter_by(name="TestArtifact6").one()

        self.assertEqual(response.body['ids'], [artifact.id])
        self.assertEqual(response.body['failed'], ['TestArtifact5'])


class TestDBFailures(BaseTest):

    def test_failing_artifacts_view(self):
        response = artifact_views.artifacts_view(dummy_request(self.db_session))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.db_err_msg)

    def test_failing_labels_view(self):
        response = artifact_views.labels_view(dummy_request(self.db_session))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.db_err_msg)

    def test_failing_supported_os_view(self):
        response = artifact_views.supported_os_view(dummy_request(self.db_session))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.db_err_msg)

    def test_failing_sources_view(self):
        response = artifact_views.sources_view(dummy_request(self.db_session))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.db_err_msg)

    def test_failing_artifact_view(self):
        test_request = dummy_request(self.db_session)
        test_request.matchdict['id'] = 1
        response = artifact_views.artifact_view(test_request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.db_err_msg)

    def test_failing_artifact_delete(self):
        test_request = dummy_request(self.db_session)
        test_request.matchdict['id'] = 1
        response = artifact_views.artifact_delete(test_request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.db_err_msg)

    def test_failing_artifact_update(self):
        test_request = dummy_request(self.db_session)
        test_request.params.add('artifact_data', TEST_ARTIFACT)
        test_request.matchdict['id'] = 1
        response = artifact_views.artifact_update(test_request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.db_err_msg)

    def test_failing_artifact_create(self):
        test_request = dummy_request(self.db_session)
        test_request.params.add('artifact_data', TEST_ARTIFACT)
        response = artifact_views.artifact_create(test_request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.db_err_msg)

    def test_failing_export_artifacts(self):
        test_request = dummy_request(self.db_session)
        test_request.params.add('id', 1)
        test_request.params.add('id', 2)
        response = artifact_views.artifact_export_view(test_request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.db_err_msg)

    def test_failing_import_artifacts(self):
        upload = ArtifactFileUpload('test_data/test_artifacts_partial.upload')
        test_request = dummy_request(self.db_session)
        test_request.params.add('artifact_file', upload)
        response = artifact_views.artifact_import(test_request)
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.text, artifact_views.db_err_msg)
