import random
from django.core.management.base import BaseCommand
from accounts.models import Account, Tags, Contact, Profile, Teams, Org, AccountEmail, AccountEmailLog

class Command(BaseCommand):
    help = 'Seeds the database with sample accounts, emails, and email logs'

    def handle(self, *args, **kwargs):
        try:
            # Fetch the organization where the accounts will be assigned
            org = Org.objects.get(name="Motopp")
            
            # Sample tags (create some if not already present)
            tags = [Tags.objects.get_or_create(name=name)[0] for name in ["New", "Important", "Review"]]

            # Sample profiles (if profiles exist)
            profiles = Profile.objects.all()[:5]  # Fetch some profiles

            # Sample teams (if teams exist)
            teams = Teams.objects.all()[:2]  # Limit to 2 teams for simplicity
            
            # Sample contacts (ensure you have some contacts created)
            contacts = Contact.objects.all()[:3]  # Fetch some contacts
            
            # Sample account data
            accounts_data = [
                {
                    "name": "Tech Innovations Ltd.",
                    "email": "contact@techinnovations.com",
                    "phone": "+1234567890",
                    "industry": "Technology",
                    "billing_address_line": "101 Innovation Drive",
                    "billing_street": "Innovation Street",
                    "billing_city": "Tech City",
                    "billing_state": "Tech State",
                    "billing_postcode": "10001",
                    "billing_country": "USA",
                    "website": "https://techinnovations.com",
                    "description": "Leading tech innovations provider.",
                    "status": "open",
                    "contact_name": "Alice Brown",
                    "is_active": True
                },
                {
                    "name": "Creative Solutions Inc.",
                    "email": "info@creativesolutions.com",
                    "phone": "+1234567891",
                    "industry": "Creative Services",
                    "billing_address_line": "202 Creative Road",
                    "billing_street": "Creative Avenue",
                    "billing_city": "Creative City",
                    "billing_state": "Creative State",
                    "billing_postcode": "20002",
                    "billing_country": "USA",
                    "website": "https://creativesolutions.com",
                    "description": "Expert in creative solutions and design.",
                    "status": "close",
                    "contact_name": "Bob White",
                    "is_active": True
                },
                {
                    "name": "Global Enterprises",
                    "email": "contact@globalenterprises.com",
                    "phone": "+1234567892",
                    "industry": "Consulting",
                    "billing_address_line": "303 Global Avenue",
                    "billing_street": "Global Street",
                    "billing_city": "Global City",
                    "billing_state": "Global State",
                    "billing_postcode": "30003",
                    "billing_country": "USA",
                    "website": "https://globalenterprises.com",
                    "description": "Global consulting services provider.",
                    "status": "open",
                    "contact_name": "Charlie Green",
                    "is_active": True
                },
                {
                    "name": "Health Solutions LLC",
                    "email": "contact@healthsolutions.com",
                    "phone": "+1234567893",
                    "industry": "Healthcare",
                    "billing_address_line": "404 Health Parkway",
                    "billing_street": "Health Road",
                    "billing_city": "Health City",
                    "billing_state": "Health State",
                    "billing_postcode": "40004",
                    "billing_country": "USA",
                    "website": "https://healthsolutions.com",
                    "description": "Providing innovative health solutions.",
                    "status": "open",
                    "contact_name": "Dana Lee",
                    "is_active": True
                }
            ]

            # Create Account instances
            for account_data in accounts_data:
                account = Account.objects.create(
                    name=account_data["name"],
                    email=account_data["email"],
                    phone=account_data["phone"],
                    industry=account_data["industry"],
                    billing_address_line=account_data["billing_address_line"],
                    billing_street=account_data["billing_street"],
                    billing_city=account_data["billing_city"],
                    billing_state=account_data["billing_state"],
                    billing_postcode=account_data["billing_postcode"],
                    billing_country=account_data["billing_country"],
                    website=account_data["website"],
                    description=account_data["description"],
                    status=account_data["status"],
                    contact_name=account_data["contact_name"],
                    is_active=account_data["is_active"],
                    org=org
                )
                
                # Assign tags, profiles, teams, and contacts
                account.tags.set([])
                account.assigned_to.set(profiles)
                account.teams.set(teams)
                account.contacts.set(contacts)

                self.stdout.write(self.style.SUCCESS(f'Successfully added account {account.name}'))

            # Sample AccountEmail data
            emails_data = [
                {
                    "from_account": Account.objects.first(),
                    "recipients": [contacts[0]],
                    "message_subject": "Welcome to Tech Innovations",
                    "message_body": "Hello, welcome to Tech Innovations!",
                    "from_email": "no-reply@techinnovations.com",
                    "rendered_message_body": "Hello, welcome to Tech Innovations!",
                    "scheduled_date_time": None,
                    "scheduled_later": False
                },
                {
                    "from_account": Account.objects.last(),
                    "recipients": [contacts[1], contacts[2]],
                    "message_subject": "Health Solutions Update",
                    "message_body": "Please read the latest update from Health Solutions.",
                    "from_email": "updates@healthsolutions.com",
                    "rendered_message_body": "Please read the latest update from Health Solutions.",
                    "scheduled_date_time": None,
                    "scheduled_later": False
                }
            ]

            # Create AccountEmail instances
            for email_data in emails_data:
                email = AccountEmail.objects.create(
                    from_account=email_data["from_account"],
                    from_email=email_data["from_email"],
                    message_subject=email_data["message_subject"],
                    message_body=email_data["message_body"],
                    rendered_message_body=email_data["rendered_message_body"],
                    scheduled_date_time=email_data["scheduled_date_time"],
                    scheduled_later=email_data["scheduled_later"]
                )
                email.recipients.set(email_data["recipients"])

                self.stdout.write(self.style.SUCCESS(f'Successfully added email with subject "{email.message_subject}"'))

            # Sample AccountEmailLog data
            email_logs_data = [
                {
                    "email": AccountEmail.objects.first(),
                    "contact": contacts[0],
                    "is_sent": True
                },
                {
                    "email": AccountEmail.objects.last(),
                    "contact": contacts[1],
                    "is_sent": False
                }
            ]

            # Create AccountEmailLog instances
            for log_data in email_logs_data:
                AccountEmailLog.objects.create(
                    email=log_data["email"],
                    contact=log_data["contact"],
                    is_sent=log_data["is_sent"]
                )

            self.stdout.write(self.style.SUCCESS('Successfully seeded accounts, emails, and email logs!'))

        except Org.DoesNotExist:
            self.stdout.write(self.style.ERROR('Organization with the given ID does not exist'))
