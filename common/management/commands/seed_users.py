import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from common.models import User, Profile, Org, Address  # Adjust this to your app's name
from phonenumber_field.phonenumber import PhoneNumber

class Command(BaseCommand):
    help = 'Seeds the database with an organization, 10 users, and their profiles, including phone numbers and names'

    def handle(self, *args, **kwargs):
        # Create the organization
        org = Org.objects.create(
            id=uuid.uuid4(),
            name="Motopp",
            is_active=True
        )

        # User data with first name, last name, email, and profile picture
        users_data = [
            {'email': 'john.doe@example.com', 'first_name': 'John', 'last_name': 'Doe', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ2Edj-fsSwM6n5SkEp0bhyD4JacGR7VUDKng&s', 'is_staff': False, 'country': 'US'},
            {'email': 'jane.smith@example.com', 'first_name': 'Jane', 'last_name': 'Smith', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQk4CIX0J2BGB28CMyWWipdkP29qI6Lxl40qw&s', 'is_staff': False, 'country': 'UK'},
            {'email': 'admin@example.com', 'first_name': 'Admin', 'last_name': 'User', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQptyC3YqVjqI_dKmXORLVG3ccvzhWwneBEn-KOsP5pGzIu2JbqNtA2HbXX55_KuP3-YuU&usqp=CAU', 'is_staff': True, 'country': 'US'},
            {'email': 'alice.williams@example.com', 'first_name': 'Alice', 'last_name': 'Williams', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQv1GvcdSOsa4prQJS8mMf6Azu3fJK1cgqVpw&s', 'is_staff': False, 'country': 'AU'},
            {'email': 'bob.jones@example.com', 'first_name': 'Bob', 'last_name': 'Jones', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQB7juHNraNt30984lsJ881nCUGQvQ3dGuh4XnqnDZZgU2eQPvFHXaiCwuBhGibv4Q8U3Q&usqp=CAU', 'is_staff': False, 'country': 'US'},
            {'email': 'charlie.brown@example.com', 'first_name': 'Charlie', 'last_name': 'Brown', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSD2YVe7j-eLVn6CMjkcXmPLjScSOAjuomDAapzlMQGygu1tMCVcfpcqCT9RARUkmBohrs&usqp=CAU', 'is_staff': False, 'country': 'CA'},
            {'email': 'david.johnson@example.com', 'first_name': 'David', 'last_name': 'Johnson', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQCitiI0jPn-QiIKdI4GrwwCfNc_GODINUQUA&s', 'is_staff': False, 'country': 'US'},
            {'email': 'emma.wilson@example.com', 'first_name': 'Emma', 'last_name': 'Wilson', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEF-9KHRVhgcIeh-VSrGOEMUCNQaR9HWwNbQ&s', 'is_staff': False, 'country': 'UK'},
            {'email': 'frank.miller@example.com', 'first_name': 'Frank', 'last_name': 'Miller', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQt-5qqeiPCdAXtddHWeyusyhRcMpsjNA4yTQ&s', 'is_staff': False, 'country': 'CA'},
            {'email': 'grace.lee@example.com', 'first_name': 'Grace', 'last_name': 'Lee', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJZHL8zj90StHnv3fkKSzUeoKmcZPO6T4AHnFnvDrvxPGY7syKOjyPdgldlNWpyDPOp-w&usqp=CAU', 'is_staff': False, 'country': 'AU'},
        ]

        # Profile data including roles, access rights, phone, and alternate phone
        profiles_data = [
            {'role': 'USER', 'has_sales_access': True, 'has_marketing_access': False, 'is_organization_admin': False, 'phone': '+14155552671'},
            {'role': 'SALES MANAGER', 'has_sales_access': False, 'has_marketing_access': True, 'is_organization_admin': False, 'phone': '+447911123456'},
            {'role': 'ADMIN', 'has_sales_access': True, 'has_marketing_access': True, 'is_organization_admin': True, 'phone': '+14155552672'},
            {'role': 'SALES REP', 'has_sales_access': True, 'has_marketing_access': False, 'is_organization_admin': False, 'phone': '+61455572671'},
            {'role': 'SALES MANAGER', 'has_sales_access': False, 'has_marketing_access': True, 'is_organization_admin': False, 'phone': '+14155552673'},
            {'role': 'USER', 'has_sales_access': True, 'has_marketing_access': False, 'is_organization_admin': False, 'phone': '+15145552671'},
            {'role': 'SALES REP', 'has_sales_access': False, 'has_marketing_access': False, 'is_organization_admin': False, 'phone': '+14155552674'},
            {'role': 'USER', 'has_sales_access': True, 'has_marketing_access': False, 'is_organization_admin': False, 'phone': '+447911123457'},
            {'role': 'SALES REP', 'has_sales_access': False, 'has_marketing_access': True, 'is_organization_admin': False, 'phone': '+15145552672'},
            {'role': 'ADMIN', 'has_sales_access': True, 'has_marketing_access': True, 'is_organization_admin': True, 'phone': '+61455572672'},
        ]

        for i in range(10):
            user_data = users_data[i]
            profile_data = profiles_data[i]

            # Create the user with names, email, and profile picture
            user = User.objects.create(
                id=uuid.uuid4(),
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                profile_pic=user_data['profile_pic'],
                is_active=True,
                is_staff=user_data['is_staff'],
                password=make_password('123456')  # Set the hashed password
            )

            # Optionally, create an address for the user (if needed)
            address = Address.objects.create(
                street="123 Main St",
                city="Sample City",
                postcode="12345",
                country=user_data['country']
            )

            # Create the profile for the user
            Profile.objects.create(
                user=user,
                org=org,
                role=profile_data['role'],
                phone=profile_data['phone'],  # Set the phone number
                address=address,  # Associate the address with the user
                has_sales_access=profile_data['has_sales_access'],
                has_marketing_access=profile_data['has_marketing_access'],
                is_active=True,
                is_organization_admin=profile_data['is_organization_admin'],
                date_of_joining='2023-09-01'
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded an organization, 10 users with first/last names, phone numbers, and profiles!'))
