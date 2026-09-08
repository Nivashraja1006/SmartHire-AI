import unittest

from app import create_app, db, socketio
from app.models import Notification, Role, User


class Phase8TestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        db.session.add_all([Role(name=Role.ADMIN), Role(name=Role.RECRUITER), Role(name=Role.CANDIDATE)])
        role = Role.query.filter_by(name=Role.RECRUITER).one()
        self.user = User(full_name='Realtime Recruiter', email='realtime@example.com', role=role)
        self.user.set_password('password-123')
        db.session.add(self.user)
        db.session.commit()
        self.client = self.app.test_client()
        self.client.post('/login', data={'email': self.user.email, 'password': 'password-123'})

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def test_notification_ownership_and_read_apis(self):
        notification = Notification(user_id=self.user.id, title='Test', message='Realtime test')
        db.session.add(notification)
        db.session.commit()
        response = self.client.get('/api/notifications')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['unread_count'], 1)
        response = self.client.post(f'/api/notifications/{notification.id}/read')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(db.session.get(Notification, notification.id).is_read)
        self.client.post('/api/notifications/read-all')
        self.assertEqual(self.client.get('/api/notifications').get_json()['unread_count'], 0)

    def test_authenticated_socket_room(self):
        socket_client = socketio.test_client(self.app, flask_test_client=self.client)
        self.assertTrue(socket_client.is_connected())
        result = socket_client.emit('join_recruiter_room', {}, callback=True)
        self.assertEqual(result['success'], True)
        socket_client.disconnect()


if __name__ == '__main__':
    unittest.main()