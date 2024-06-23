from django.core.management.base import BaseCommand
from oauth2_provider.models import Application

class Command(BaseCommand):
    help = 'Create a DOT application with client_id "public" and grant_type "password"'

    def handle(self, *args, **kwargs):
        # Define your application data
        client_id = "public"
        grant_type = Application.GRANT_PASSWORD
        application_name = "Public Application"

        # Check if the application already exists
        if Application.objects.filter(client_id=client_id).exists():
            self.stdout.write(self.style.WARNING(f'Application with client_id "{client_id}" already exists.'))
        else:
            # Create the application
            application = Application.objects.create(
                client_id=client_id,
                client_secret="",
                client_type=Application.CLIENT_PUBLIC,
                authorization_grant_type=grant_type,
                name=application_name,
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created application with client_id "{client_id}".'))

        self.stdout.write(self.style.SUCCESS('Finished creating DOT application'))
