from django.core.management.base import BaseCommand
from app.core.models import Region, Area

class Command(BaseCommand):
    help = 'Populate Region and Area models'

    def handle(self, *args, **kwargs):
        # Define your data
        regions_data = [
            {"name": "Southern Region", "country": "Pakistan"},
            {"name": "Northern Region", "country": "Pakistan"},
        ]

        areas_data = [
            {"name": "Mubarak Jamatkhana", "city": "Hyderbad", "council": "Hyderbad", "region": "Southern Region"},
            {"name": "Aminabad Jamatkhana", "city": "Hyderbad", "council": "Hyderbad", "region": "Southern Region"},
            {"name": "Alibad Jamatkhana", "city": "Hyderbad", "council": "Hyderbad", "region": "Southern Region"},
            {"name": "Karimabad Jamatkhana", "city": "Karachi", "council": "Karachi", "region": "Southern Region"},
            {"name": "Garden Jamatkhana", "city": "Karachi", "council": "Karachi", "region": "Southern Region"},
            {"name": "Kharadhar Jamatkhana", "city": "Karachi", "council": "Karachi", "region": "Southern Region"},
            {"name": "Darkhana Jamatkhana", "city": "Karachi", "council": "Karachi", "region": "Southern Region"},
            {"name": "Clifton Jamatkhana", "city": "Karachi", "council": "Karachi", "region": "Southern Region"},
            {"name": "Defense Jamatkhana", "city": "Karachi", "council": "Karachi", "region": "Southern Region"},
        ]

        # Populate regions
        for region_data in regions_data:
            region, created = Region.objects.get_or_create(
                name=region_data["name"],
                defaults={"country": region_data["country"]},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created region: {region.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Region already exists: {region.name}'))

        # Populate areas
        for area_data in areas_data:
            try:
                region = Region.objects.get(name=area_data["region"])
                area, created = Area.objects.get_or_create(
                    name=area_data["name"],
                    city=area_data["city"],
                    council=area_data["council"],
                    defaults={"region": region},
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Successfully created area: {area.name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'Area already exists: {area.name}'))
            except Region.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Region does not exist for area: {area_data["name"]}'))

        self.stdout.write(self.style.SUCCESS('Finished populating regions and areas'))
