import random
from django.core.management.base import BaseCommand
from contacts.models import Contact, Org, Address, Profile, Teams  # Import relevant models

class Command(BaseCommand):
    help = 'Seeds the database with sample contacts'

    def handle(self, *args, **kwargs):
        try:
            # Fetch the organization where the contacts will be assigned
            org = Org.objects.get(name="Motopp")
            
            # Sample address (assume you have some address objects created in the database)
            address = Address.objects.first()  # Replace with actual logic to fetch address

            # Sample teams (if teams exist)
            teams = Teams.objects.all()[:2]  # Limit to 2 teams for simplicity
            
            # Fetch sample profiles (if profiles exist)
            profiles = Profile.objects.all()[:5]  # Fetch some profiles

            # List of sample contact data
            contacts_data = [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "primary_email": "john.doe@example.com",
                    "mobile_number": "+1234567890",
                    "title": "Manager",
                    "organization": "Example Corp",
                    "department": "Sales",
                    "language": "English",
                    "linked_in_url": "https://linkedin.com/in/johndoe",
                    "facebook_url": "https://facebook.com/johndoe",
                    "twitter_username": "johndoe",
                    "country": "USA",
                    "description": "A valuable contact in sales.",
                },
                {
                    "first_name": "Jane",
                    "last_name": "Smith",
                    "primary_email": "jane.smith@example.com",
                    "mobile_number": "+1234567891",
                    "title": "Marketing Lead",
                    "organization": "ABC Marketing",
                    "department": "Marketing",
                    "language": "French",
                    "linked_in_url": "https://linkedin.com/in/janesmith",
                    "facebook_url": "https://facebook.com/janesmith",
                    "twitter_username": "janesmith",
                    "country": "FRA",
                    "description": "Leading expert in marketing strategy.",
                },
                {
                    "first_name": "Emily",
                    "last_name": "Johnson",
                    "primary_email": "emily.johnson@example.com",
                    "mobile_number": "+1234567892",
                    "title": "Product Manager",
                    "organization": "Tech Innovations",
                    "department": "Product",
                    "language": "Spanish",
                    "linked_in_url": "https://linkedin.com/in/emilyjohnson",
                    "facebook_url": "https://facebook.com/emilyjohnson",
                    "twitter_username": "emilyjohnson",
                    "country": "ESP",
                    "description": "Expert in product development.",
                },
                {
                    "first_name": "Michael",
                    "last_name": "Brown",
                    "primary_email": "michael.brown@example.com",
                    "mobile_number": "+1234567893",
                    "title": "CTO",
                    "organization": "Future Tech",
                    "department": "Technology",
                    "language": "German",
                    "linked_in_url": "https://linkedin.com/in/michaelbrown",
                    "facebook_url": "https://facebook.com/michaelbrown",
                    "twitter_username": "michaelbrown",
                    "country": "DEU",
                    "description": "Chief Technology Officer with vast experience.",
                },
                {
                    "first_name": "Olivia",
                    "last_name": "Davis",
                    "primary_email": "olivia.davis@example.com",
                    "mobile_number": "+1234567894",
                    "title": "HR Specialist",
                    "organization": "Global Enterprises",
                    "department": "HR",
                    "language": "Italian",
                    "linked_in_url": "https://linkedin.com/in/oliviadavis",
                    "facebook_url": "https://facebook.com/oliviadavis",
                    "twitter_username": "oliviadavis",
                    "country": "ITA",
                    "description": "Experienced in global HR management.",
                },
                {
                    "first_name": "Liam",
                    "last_name": "Wilson",
                    "primary_email": "liam.wilson@example.com",
                    "mobile_number": "+1234567895",
                    "title": "Sales Director",
                    "organization": "Sales Pros",
                    "department": "Sales",
                    "language": "Portuguese",
                    "linked_in_url": "https://linkedin.com/in/liamwilson",
                    "facebook_url": "https://facebook.com/liamwilson",
                    "twitter_username": "liamwilson",
                    "country": "PRT",
                    "description": "Director of Sales with a focus on global markets.",
                },
                {
                    "first_name": "Sophia",
                    "last_name": "Martinez",
                    "primary_email": "sophia.martinez@example.com",
                    "mobile_number": "+1234567896",
                    "title": "Customer Support Manager",
                    "organization": "Service Solutions",
                    "department": "Support",
                    "language": "Dutch",
                    "linked_in_url": "https://linkedin.com/in/sophiamartinez",
                    "facebook_url": "https://facebook.com/sophiamartinez",
                    "twitter_username": "sophiamartinez",
                    "country": "NLD",
                    "description": "Specializing in customer support and relations.",
                }
            ]

            # Iterate over the contacts and create them in the database
            for contact_data in contacts_data:
                contact = Contact.objects.create(
                    salutation="Mr." if random.choice([True, False]) else "Ms.",
                    first_name=contact_data["first_name"],
                    last_name=contact_data["last_name"],
                    primary_email=contact_data["primary_email"],
                    mobile_number=contact_data["mobile_number"],
                    title=contact_data["title"],
                    organization=contact_data["organization"],
                    department=contact_data["department"],
                    language=contact_data["language"],
                    address=address,
                    description=contact_data["description"],
                    linked_in_url=contact_data["linked_in_url"],
                    facebook_url=contact_data["facebook_url"],
                    twitter_username=contact_data["twitter_username"],
                    org=org,
                    country=contact_data["country"],
                    is_active=True
                )

                # Assign teams and users to contact
                contact.teams.set(teams)
                contact.assigned_to.set(profiles)

                self.stdout.write(self.style.SUCCESS(f'Successfully added contact {contact.first_name} {contact.last_name}'))

            self.stdout.write(self.style.SUCCESS('Successfully seeded contacts!'))

        except Org.DoesNotExist:
            self.stdout.write(self.style.ERROR('Organization with the given ID does not exist'))
