import unittest

from john import app, db, Users


class DeleteRouteTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        with app.app_context():
            db.drop_all()
            db.create_all()

    def test_delete_route_accepts_get_and_removes_user(self):
        with app.app_context():
            user = Users(name='Delete Me', email='delete@example.com', color='red')
            db.session.add(user)
            db.session.commit()
            user_id = user.id

            with app.test_client() as client:
                response = client.get(f'/delete/{user_id}', follow_redirects=True)

                self.assertEqual(response.status_code, 200)
                self.assertIsNone(Users.query.get(user_id))


if __name__ == '__main__':
    unittest.main()
