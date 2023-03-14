import unittest
from app import app, db, User, Todo,session


class TodoAppTestCase(unittest.TestCase):
    
    def setUp(self):
        # Set up a test database
        with app.app_context():
            app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
            app.config['TESTING'] = True
            self.app = app.test_client()
            db.drop_all()
            db.create_all()
            self.user = User(name='Test User', email='test@example.com', password='password')
            db.session.add(self.user)
            db.session.commit()
            self.todo = Todo(title='Test Todo', user_id=self.user.id)
            db.session.add(self.todo)
            db.session.commit()
    
    def tearDown(self):
        with app.app_context():
        # Drop the test database
            db.session.remove()
            db.drop_all()
    # helper method to log in as test user
    def login(self):
        return self.app.post('/login', data=dict(name='Test User', email='test@example.com', password='password'), follow_redirects=True)
    
    # helper method to log out
    def logout(self):
        return self.app.get('/logout', follow_redirects=True)
    

    
    def test_home_redirect(self):
        with app.app_context():
        # Test that the home page redirects to the signup page
            response = self.app.get('/')
            self.assertEqual(response.status_code, 302)
            
    def test_index_redirect(self):
        # Test that the todo list page redirects to the signin page if the user is not logged in
        response = self.app.get('/todo')
        self.assertEqual(response.status_code, 302)
        
    
    def test_index_logged_in(self):
        # Test that the todo list page displays the user's todos if the user is logged in
        self.login()
        response = self.app.get('/todo',follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_add_todo_item(self):
       with app.app_context():
        
        self.user = User(name='test_user', email='test1@example.com', password='test_password')
        db.session.add(self.user)
        db.session.commit()

        print(self.user.id)
        #user_id = session.get('user_id')
        
        response = self.app.post('/add', data=dict(title='new todo item'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        todo = Todo.query.filter_by(title='new todo item', user_id=self.user.id).first()
        #self.assertIsNotNone(todo)
        self.assertEqual(todo.status, 'to do')


if __name__ == 'main':
    unittest.main()