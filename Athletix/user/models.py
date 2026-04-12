from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

#this class manages users email and password properly
class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None, role='athlete', **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

# it is related to django admin
    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, name, password, role='coach', **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('athlete', 'Athlete'),
        ('coach', 'Coach'),
        ('medical', 'Medical Staff'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='athlete')
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    @property
    def first_name(self):
        return self.name.split()[0] if self.name else ''

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.get_role_display()}"

    class Meta:
        db_table = 'user_table'

# Profile of admins
class AthleteProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='athlete_profile')
    sport_type = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    fitness_level = models.CharField(
        max_length=20,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')],
        default='medium'
    )

    def __str__(self):
        return f"Athlete: {self.user.name}"

    class Meta:
        db_table = 'athlete_profile'


class CoachProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coach_profile')
    specialization = models.CharField(max_length=200, blank=True)
    experience_years = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Coach: {self.user.name}"

    class Meta:
        db_table = 'coach_profile'


class MedicalProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='medical_profile')
    license_no = models.CharField(max_length=100, unique=True, blank=True)
    specialty = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Medical: {self.user.name}"

    class Meta:
        db_table = 'medical_profile'
