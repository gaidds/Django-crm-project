import random
import uuid
from django.core.management.base import BaseCommand
from common.models import Address

COUNTRIES = [
    ("US", "United States"),
    ("CA", "Canada"),
    ("FR", "France"),
    ("DE", "Germany"),
    # Add more countries if needed
]

# Sample addresses data
ADDRESSES = [
    {
        "address_line": "",  # Address line left empty
        "street": "Main Street",
        "city": "New York",
        "state": "NY",
        "postcode": "10001",
        "country": "US",
    },
    {
        "address_line": "",  # Address line left empty
        "street": "Elm Street",
        "city": "Los Angeles",
        "state": "CA",
        "postcode": "90001",
        "country": "US",
    },
    {
        "address_line": "",  # Address line left empty
        "street": "Oak Street",
        "city": "Toronto",
        "state": "Ontario",
        "postcode": "M5H 2N2",
        "country": "CA",
    },
    {
        "address_line": "",  # Address line left empty
        "street": "Pine Street",
        "city": "Paris",
        "state": "Île-de-France",
        "postcode": "75001",
        "country": "FR",
    },
    {
        "address_line": "",  # Address line left empty
        "street": "Maple Street",
        "city": "Berlin",
        "state": "Berlin",
        "postcode": "10115",
        "country": "DE",
    },
]

class Command(BaseCommand):
    help = "Seed the Address table with sample data"

    def handle(self, *args, **kwargs):
        # Loop over the sample data and create Address objects
        for address_data in ADDRESSES:
            address, created = Address.objects.get_or_create(
                address_line=address_data["address_line"],  # This will now be empty
                street=address_data["street"],
                city=address_data["city"],
                state=address_data["state"],
                postcode=address_data["postcode"],
                country=address_data["country"],
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Successfully created address: {address.get_complete_address()}'))
            else:
                self.stdout.write(self.style.WARNING(f'Address already exists: {address.get_complete_address()}'))
