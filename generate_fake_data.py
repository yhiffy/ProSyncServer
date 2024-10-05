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


for _ in range(5):
    job = Job.objects.create(
        title=fake.job(),
        company=fake.company(),
        city=fake.city(),
        town=fake.city(),
        province=fake.state(),
        salary_min=fake.random_number(digits=5),
        salary_max=fake.random_number(digits=6),
        job_type="Full-Time",
        industry=fake.word(),
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