from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your-secret-key'

    db.init_app(app)
    migrate.init_app(app, db)

    

        # Import User model inside app context
    from app.models.user import User
    from werkzeug.security import generate_password_hash
        # Register blueprints
    from app.routes import main, api
    app.register_blueprint(main.bp)
    app.register_blueprint(api.bp)


    with app.app_context():
        db.create_all()

        from werkzeug.security import generate_password_hash
        # Create admin user if not exists

        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password=generate_password_hash('admin123')
            )
            db.session.add(admin)
            db.session.commit()   
            print("Admin user created successfully!") 
    
    

    @app.cli.command("populate-db")
    def populate_db_command():
        """Populate the database with sample data."""
        from .dummy_data import populate_database
        populate_database()
        print("Database populated with sample data!")

    return app
