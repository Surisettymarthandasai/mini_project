"""
Management command to automatically set up MySQL database and tables.
"""
import sys

import MySQLdb
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Automatically creates MySQL database and all required tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--host',
            type=str,
            default='127.0.0.1',
            help='MySQL host (default: 127.0.0.1)'
        )
        parser.add_argument(
            '--port',
            type=int,
            default=3306,
            help='MySQL port (default: 3306)'
        )
        parser.add_argument(
            '--user',
            type=str,
            default='root',
            help='MySQL username (default: root)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='root',
            help='MySQL password (default: root)'
        )
        parser.add_argument(
            '--database',
            type=str,
            default='academic_mgmt',
            help='Database name to create (default: academic_mgmt)'
        )

    def handle(self, *args, **options):
        host = options['host']
        port = options['port']
        user = options['user']
        password = options['password']
        database = options['database']

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('Academic Management System - Database Setup'))
        self.stdout.write(self.style.SUCCESS('=' * 70))
        
        # Step 1: Connect to MySQL server (without database)
        self.stdout.write('\n[1/4] Connecting to MySQL server...')
        try:
            db = MySQLdb.connect(
                host=host,
                port=port,
                user=user,
                passwd=password
            )
            cursor = db.cursor()
            self.stdout.write(self.style.SUCCESS(f'✓ Connected to MySQL at {host}:{port}'))
        except MySQLdb.Error as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to connect to MySQL: {e}'))
            self.stdout.write(self.style.WARNING('\nPlease check:'))
            self.stdout.write('  - MySQL server is running')
            self.stdout.write('  - Credentials are correct')
            self.stdout.write('  - Host and port are accessible')
            sys.exit(1)

        # Step 2: Create database if it doesn't exist
        self.stdout.write(f'\n[2/4] Creating database "{database}"...')
        try:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            self.stdout.write(self.style.SUCCESS(f'✓ Database "{database}" ready'))
            
            # Check if database was just created or already existed
            cursor.execute(f"SHOW DATABASES LIKE '{database}'")
            if cursor.fetchone():
                self.stdout.write(f'  Database is accessible and ready to use')
        except MySQLdb.Error as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to create database: {e}'))
            sys.exit(1)
        finally:
            cursor.close()
            db.close()

        # Step 3: Update Django settings with provided credentials
        self.stdout.write(f'\n[3/4] Updating Django database configuration...')
        settings.DATABASES['default']['HOST'] = host
        settings.DATABASES['default']['PORT'] = str(port)
        settings.DATABASES['default']['USER'] = user
        settings.DATABASES['default']['PASSWORD'] = password
        settings.DATABASES['default']['NAME'] = database
        self.stdout.write(self.style.SUCCESS(f'✓ Django configured to use {user}@{host}:{port}/{database}'))

        # Step 4: Test connection and create tables
        self.stdout.write(f'\n[4/4] Creating database tables...')
        try:
            # Test connection
            connection.ensure_connection()
            self.stdout.write('  Testing database connection...')
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()[0]
                self.stdout.write(f'  ✓ Connected to MySQL {version}')
            
            # Run migrations to create tables
            self.stdout.write('\n  Running migrations...')
            call_command('migrate', '--noinput', verbosity=0)
            
            # Count created tables
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = '{database}'")
                table_count = cursor.fetchone()[0]
                self.stdout.write(self.style.SUCCESS(f'✓ Created {table_count} database tables'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Failed to create tables: {e}'))
            sys.exit(1)

        # Success summary
        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('✓ DATABASE SETUP COMPLETE!'))
        self.stdout.write('=' * 70)
        self.stdout.write('\nYour database is ready. You can now:')
        self.stdout.write('  1. Run the server: python manage.py runserver')
        self.stdout.write('  2. Create admin user: python manage.py createsuperuser')
        self.stdout.write('  3. Access the application at http://127.0.0.1:8000')
        self.stdout.write('\n' + '=' * 70 + '\n')
