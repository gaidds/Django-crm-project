import uuid
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from common.models import User, Profile, Org  # Adjust this to your app's name

class Command(BaseCommand):
    help = 'Seeds the database with an organization, 10 users, and their profiles'

    def handle(self, *args, **kwargs):
        # Create the organization
        org = Org.objects.create(
            id=uuid.uuid4(),
            name="Motopp",
            is_active=True
        )

        users_data = [
            {'email': 'john.doe@example.com', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ2Edj-fsSwM6n5SkEp0bhyD4JacGR7VUDKng&s', 'is_staff': False},
            {'email': 'jane.smith@example.com', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQk4CIX0J2BGB28CMyWWipdkP29qI6Lxl40qw&s', 'is_staff': False},
            {'email': 'admin@example.com', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQptyC3YqVjqI_dKmXORLVG3ccvzhWwneBEn-KOsP5pGzIu2JbqNtA2HbXX55_KuP3-YuU&usqp=CAU', 'is_staff': True},
            {'email': 'alice.williams@example.com', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQv1GvcdSOsa4prQJS8mMf6Azu3fJK1cgqVpw&s', 'is_staff': False},
            {'email': 'bob.jones@example.com', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQB7juHNraNt30984lsJ881nCUGQvQ3dGuh4XnqnDZZgU2eQPvFHXaiCwuBhGibv4Q8U3Q&usqp=CAU', 'is_staff': False},
            {'email': 'charlie.brown@example.com', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSD2YVe7j-eLVn6CMjkcXmPLjScSOAjuomDAapzlMQGygu1tMCVcfpcqCT9RARUkmBohrs&usqp=CAU', 'is_staff': False},
            {'email': 'david.johnson@example.com', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQCitiI0jPn-QiIKdI4GrwwCfNc_GODINUQUA&s', 'is_staff': False},
            {'email': 'emma.wilson@example.com', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSEF-9KHRVhgcIeh-VSrGOEMUCNQaR9HWwNbQ&s', 'is_staff': False},
            {'email': 'frank.miller@example.com', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQt-5qqeiPCdAXtddHWeyusyhRcMpsjNA4yTQ&s', 'is_staff': False},
            {'email': 'grace.lee@example.com', 'profile_pic': 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRJZHL8zj90StHnv3fkKSzUeoKmcZPO6T4AHnFnvDrvxPGY7syKOjyPdgldlNWpyDPOp-w&usqp=CAU', 'is_staff': False},
        ]

        profiles_data = [
            {'role': 'USER', 'has_sales_access': True, 'has_marketing_access': False, 'is_organization_admin': False},
            {'role': 'SALES MANAGER', 'has_sales_access': False, 'has_marketing_access': True, 'is_organization_admin': False},
            {'role': 'ADMIN', 'has_sales_access': True, 'has_marketing_access': True, 'is_organization_admin': True},
            {'role': 'SALES REP', 'has_sales_access': True, 'has_marketing_access': False, 'is_organization_admin': False},
            {'role': 'SALES MANAGER', 'has_sales_access': False, 'has_marketing_access': True, 'is_organization_admin': False},
            {'role': 'USER', 'has_sales_access': True, 'has_marketing_access': False, 'is_organization_admin': False},
            {'role': 'SALES REP', 'has_sales_access': False, 'has_marketing_access': False, 'is_organization_admin': False},
            {'role': 'USER', 'has_sales_access': True, 'has_marketing_access': False, 'is_organization_admin': False},
            {'role': 'SALES REP', 'has_sales_access': False, 'has_marketing_access': True, 'is_organization_admin': False},
            {'role': 'ADMIN', 'has_sales_access': True, 'has_marketing_access': True, 'is_organization_admin': True},
        ]

        for i in range(10):
            user_data = users_data[i]
            profile_data = profiles_data[i]

            user = User.objects.create(
                id=uuid.uuid4(),
                email=user_data['email'],
                profile_pic=user_data['profile_pic'],
                is_active=True,
                is_staff=user_data['is_staff'],
                password=make_password('123456')  # Set the hashed password
            )

            Profile.objects.create(
                user=user,
                org=org,
                role=profile_data['role'],
                has_sales_access=profile_data['has_sales_access'],
                has_marketing_access=profile_data['has_marketing_access'],
                is_active=True,
                is_organization_admin=profile_data['is_organization_admin'],
                date_of_joining='2023-09-01'
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded an organization, 10 users, and profiles!'))
