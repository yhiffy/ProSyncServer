import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django
django.setup()

from faker import Faker
from job.models import Job, JobBookmark
from user_auth.models import User
import uuid
from django.utils import timezone
import random

fake = Faker()


users = list(User.objects.all())
jobs = list(Job.objects.all())   


for _ in range(10):
    user = User.objects.create(
        id=uuid.uuid4(),
        email=fake.email(),
        password=fake.password(),
        full_name=fake.name(),
        is_active=True
    )
    users.append(user)  


for _ in range(60):
    job = Job.objects.create(
        title=fake.job(),
        company=fake.company(),
        city=fake.city(),
        town=fake.city(),
        province=fake.state(),
        salary_min = fake.random_int(min=10000, max=60000),
        salary_max = fake.random_int(min=60001, max=200000),
        job_type=fake.random_element(elements=["Perm", "Temp", "Contract"]),
        industry = fake.random_element(elements=[
    "Information Technology", "Finance", "Healthcare", "Education", "Manufacturing",
    "Retail", "Telecommunications", "Energy", "Transportation", "Construction",
    "Hospitality", "Real Estate", "Agriculture", "Media and Entertainment", "Pharmaceuticals",
    "Automotive", "Aerospace and Defense", "Consulting", "Food and Beverage", "Non-Profit",
    "Insurance", "Legal Services", "Advertising and Marketing", "Environmental Services",
    "Public Sector", "Textiles", "Logistics", "Mining", "Chemical Industry", "Biotechnology"
]),
        profession=fake.job(),
        experience_level=fake.random_element(elements=('entry', 'mid', 'senior', 'executive')),
        description_title=fake.sentence(),
        description=fake.text(),
        application_deadline=timezone.now().date()
    )
    jobs.append(job)  

for _ in range(10):
    user = random.choice(users)  
    job = random.choice(jobs)  

    if isinstance(user, User) and isinstance(job, Job):
        if not JobBookmark.objects.filter(user=user, job=job).exists():
            JobBookmark.objects.create(
                user=user,
                job=job,
                saved_at=timezone.now()
            )

print("generate fake data successfully!")