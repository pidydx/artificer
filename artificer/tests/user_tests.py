from artificer.tests.base_tests import BaseTest

class TestUsers(BaseTest):
    def setUp(self):
        super(TestUsers, self).setUp()
        self.init_database()

    def test_create_user(self):
        from artificer.models import User
        count = self.db_session.query(User).filter_by(name='admin').count()
        self.assertEqual(count, 1)

    def test_delete_user(self):
        from artificer.models import User
        user = self.db_session.query(User).filter_by(name='admin').one()
        self.db_session.delete(user)
        count = self.db_session.query(User).filter_by(name='admin').count()
        self.assertEqual(count, 0)
