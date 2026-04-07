from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import User, AthleteProfile, CoachProfile, MedicalProfile
from .forms import SignUpForm, LoginForm, ForgotPasswordForm, ProfileEditForm


# ============================================================================
# MODEL TESTS (Tests 1-13)
# ============================================================================

class UserModelTests(TestCase):
    """Tests for the custom User model"""

    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'name': 'John Doe',
            'password': 'testpass123',
            'role': 'athlete'
        }

    # Test 1: Create user with email
    def test_create_user_with_email(self):
        """Test creating a user with email is successful"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.name, self.user_data['name'])
        self.assertTrue(user.check_password(self.user_data['password']))
        self.assertEqual(user.role, 'athlete')

    # Test 2: Email normalization
    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        email = 'test@EXAMPLE.COM'
        user = User.objects.create_user(email=email, name='Test', password='test123')
        self.assertEqual(user.email, email.lower())

    # Test 3: User without email raises error
    def test_new_user_without_email_raises_error(self):
        """Test that creating user without email raises ValueError"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', name='Test', password='test123')

    # Test 4: Create superuser
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            name='Admin User',
            password='adminpass123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.role, 'coach')

    # Test 5: User string representation
    def test_user_str_representation(self):
        """Test the user string representation"""
        user = User.objects.create_user(**self.user_data)
        expected = f"{user.name} ({user.email}) - Athlete"
        self.assertEqual(str(user), expected)

    # Test 6: First name property
    def test_user_first_name_property(self):
        """Test first_name property returns first word of name"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.first_name, 'John')

    # Test 7: First name with empty name
    def test_user_first_name_empty_name(self):
        """Test first_name property with empty name"""
        user = User.objects.create_user(
            email='empty@example.com',
            name='',
            password='test123'
        )
        self.assertEqual(user.first_name, '')

    # Test 8: User default is active
    def test_user_default_is_active(self):
        """Test user is active by default"""
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(user.is_active)

    # Test 9: User default is not staff
    def test_user_default_is_not_staff(self):
        """Test user is not staff by default"""
        user = User.objects.create_user(**self.user_data)
        self.assertFalse(user.is_staff)


class AthleteProfileTests(TestCase):
    """Tests for AthleteProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='athlete@example.com',
            name='Athlete User',
            password='test123',
            role='athlete'
        )

    # Test 10: Create athlete profile
    def test_create_athlete_profile(self):
        """Test creating an athlete profile"""
        profile = AthleteProfile.objects.create(
            user=self.user,
            sport_type='Football',
            age=25,
            fitness_level='high'
        )
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.sport_type, 'Football')
        self.assertEqual(profile.age, 25)

    # Test 11: Athlete profile string representation
    def test_athlete_profile_str(self):
        """Test athlete profile string representation"""
        profile = AthleteProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), f"Athlete: {self.user.name}")

    # Test 12: Athlete profile default fitness level
    def test_athlete_profile_default_fitness_level(self):
        """Test default fitness level is medium"""
        profile = AthleteProfile.objects.create(user=self.user)
        self.assertEqual(profile.fitness_level, 'medium')


class CoachProfileTests(TestCase):
    """Tests for CoachProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='coach@example.com',
            name='Coach User',
            password='test123',
            role='coach'
        )

    # Test 13: Create coach profile
    def test_create_coach_profile(self):
        """Test creating a coach profile"""
        profile = CoachProfile.objects.create(
            user=self.user,
            specialization='Fitness Training',
            experience_years=10
        )
        self.assertEqual(profile.specialization, 'Fitness Training')
        self.assertEqual(profile.experience_years, 10)

    # Test 14: Coach profile string representation
    def test_coach_profile_str(self):
        """Test coach profile string representation"""
        profile = CoachProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), f"Coach: {self.user.name}")


class MedicalProfileTests(TestCase):
    """Tests for MedicalProfile model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='medical@example.com',
            name='Medical User',
            password='test123',
            role='medical'
        )

    # Test 15: Create medical profile
    def test_create_medical_profile(self):
        """Test creating a medical profile"""
        profile = MedicalProfile.objects.create(
            user=self.user,
            license_no='MED123456',
            specialty='Sports Medicine'
        )
        self.assertEqual(profile.license_no, 'MED123456')
        self.assertEqual(profile.specialty, 'Sports Medicine')

    # Test 16: Medical profile string representation
    def test_medical_profile_str(self):
        """Test medical profile string representation"""
        profile = MedicalProfile.objects.create(user=self.user)
        self.assertEqual(str(profile), f"Medical: {self.user.name}")


# ============================================================================
# FORM TESTS (Tests 17-26)
# ============================================================================

class SignUpFormTests(TestCase):
    """Tests for SignUpForm"""

    # Test 17: Valid signup form
    def test_valid_signup_form(self):
        """Test signup form with valid data"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'athlete',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid())

    # Test 18: Signup form password mismatch
    def test_signup_form_password_mismatch(self):
        """Test signup form with mismatched passwords"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'athlete',
            'password': 'securepass123',
            'confirm_password': 'differentpass'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('Passwords do not match', str(form.errors))

    # Test 19: Signup form short password
    def test_signup_form_short_password(self):
        """Test signup form with password less than 8 characters"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'athlete',
            'password': 'short',
            'confirm_password': 'short'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())

    # Test 20: Signup form duplicate email
    def test_signup_form_duplicate_email(self):
        """Test signup form with existing email"""
        User.objects.create_user(
            email='existing@example.com',
            name='Existing User',
            password='test123'
        )
        form_data = {
            'name': 'New User',
            'email': 'existing@example.com',
            'role': 'athlete',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    # Test 21: Signup form saves user with hashed password
    def test_signup_form_saves_user(self):
        """Test that form saves user with hashed password"""
        form_data = {
            'name': 'Test User',
            'email': 'newuser@example.com',
            'role': 'coach',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(user.check_password('securepass123'))
        self.assertEqual(user.role, 'coach')


class LoginFormTests(TestCase):
    """Tests for LoginForm"""

    # Test 22: Valid login form
    def test_valid_login_form(self):
        """Test login form with valid data"""
        form_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    # Test 23: Login form invalid email
    def test_login_form_invalid_email(self):
        """Test login form with invalid email format"""
        form_data = {
            'email': 'invalid-email',
            'password': 'testpass123'
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    # Test 24: Login form empty fields
    def test_login_form_empty_fields(self):
        """Test login form with empty fields"""
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())


class ForgotPasswordFormTests(TestCase):
    """Tests for ForgotPasswordForm"""

    # Test 25: Valid forgot password form
    def test_valid_forgot_password_form(self):
        """Test forgot password form with valid data"""
        form_data = {
            'email': 'test@example.com',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        form = ForgotPasswordForm(data=form_data)
        self.assertTrue(form.is_valid())

    # Test 26: Forgot password form password mismatch
    def test_forgot_password_mismatch(self):
        """Test forgot password form with mismatched passwords"""
        form_data = {
            'email': 'test@example.com',
            'new_password': 'newpass123',
            'confirm_password': 'different123'
        }
        form = ForgotPasswordForm(data=form_data)
        self.assertFalse(form.is_valid())


# ============================================================================
# VIEW TESTS (Tests 27-53)
# ============================================================================

class HomeViewTests(TestCase):
    """Tests for home view"""

    # Test 27: Home page status code
    def test_home_page_status_code(self):
        """Test home page returns 200"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    # Test 28: Home page uses correct template
    def test_home_page_uses_correct_template(self):
        """Test home page uses home.html template"""
        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'home.html')


class LoginViewTests(TestCase):
    """Tests for login view"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
        self.login_url = reverse('login')

    # Test 29: Login page status code
    def test_login_page_status_code(self):
        """Test login page returns 200"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    # Test 30: Login page uses correct template
    def test_login_page_uses_correct_template(self):
        """Test login page uses correct template"""
        response = self.client.get(self.login_url)
        self.assertTemplateUsed(response, 'user/login.html')

    # Test 31: Login with valid credentials
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials redirects"""
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('home'))

    # Test 32: Login with invalid credentials
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials shows error"""
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    # Test 33: Login redirects authenticated user
    def test_login_redirects_authenticated_user(self):
        """Test authenticated user is redirected from login page"""
        self.client.force_login(self.user)
        response = self.client.get(self.login_url)
        self.assertRedirects(response, reverse('home'))

    # Test 34: Login with inactive user
    def test_login_inactive_user(self):
        """Test login with inactive user shows error"""
        self.user.is_active = False
        self.user.save()
        response = self.client.post(self.login_url, {
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 200)


class SignupViewTests(TestCase):
    """Tests for signup view"""

    def setUp(self):
        self.signup_url = reverse('signup')

    # Test 35: Signup page status code
    def test_signup_page_status_code(self):
        """Test signup page returns 200"""
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)

    # Test 36: Signup page uses correct template
    def test_signup_page_uses_correct_template(self):
        """Test signup page uses correct template"""
        response = self.client.get(self.signup_url)
        self.assertTemplateUsed(response, 'user/signup.html')

    # Test 37: Signup creates user
    def test_signup_creates_user(self):
        """Test successful signup creates user"""
        response = self.client.post(self.signup_url, {
            'name': 'New User',
            'email': 'newuser@example.com',
            'role': 'athlete',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        })
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())

    # Test 38: Signup creates athlete profile
    def test_signup_creates_athlete_profile(self):
        """Test signup as athlete creates AthleteProfile"""
        self.client.post(self.signup_url, {
            'name': 'Athlete User',
            'email': 'athlete@example.com',
            'role': 'athlete',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        })
        user = User.objects.get(email='athlete@example.com')
        self.assertTrue(hasattr(user, 'athlete_profile'))

    # Test 39: Signup creates coach profile
    def test_signup_creates_coach_profile(self):
        """Test signup as coach creates CoachProfile"""
        self.client.post(self.signup_url, {
            'name': 'Coach User',
            'email': 'coach@example.com',
            'role': 'coach',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        })
        user = User.objects.get(email='coach@example.com')
        self.assertTrue(hasattr(user, 'coach_profile'))

    # Test 40: Signup creates medical profile
    def test_signup_creates_medical_profile(self):
        """Test signup as medical creates MedicalProfile"""
        self.client.post(self.signup_url, {
            'name': 'Medical User',
            'email': 'medical@example.com',
            'role': 'medical',
            'password': 'securepass123',
            'confirm_password': 'securepass123'
        })
        user = User.objects.get(email='medical@example.com')
        self.assertTrue(hasattr(user, 'medical_profile'))


class LogoutViewTests(TestCase):
    """Tests for logout view"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )

    # Test 41: Logout redirects to login
    def test_logout_redirects_to_login(self):
        """Test logout redirects to login page"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('login'))

    # Test 42: Logout requires login
    def test_logout_requires_login(self):
        """Test logout requires authentication"""
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('logout')}")


class ForgotPasswordViewTests(TestCase):
    """Tests for forgot password view"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='oldpass123'
        )
        self.forgot_url = reverse('forgot_password')

    # Test 43: Forgot password page status code
    def test_forgot_password_page_status_code(self):
        """Test forgot password page returns 200"""
        response = self.client.get(self.forgot_url)
        self.assertEqual(response.status_code, 200)

    # Test 44: Forgot password updates password
    def test_forgot_password_updates_password(self):
        """Test forgot password updates user password"""
        response = self.client.post(self.forgot_url, {
            'email': 'test@example.com',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        })
        self.assertRedirects(response, reverse('login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))

    # Test 45: Forgot password with non-existent email
    def test_forgot_password_nonexistent_email(self):
        """Test forgot password with non-existent email"""
        response = self.client.post(self.forgot_url, {
            'email': 'nonexistent@example.com',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        })
        self.assertEqual(response.status_code, 200)


class DashboardViewTests(TestCase):
    """Tests for dashboard view"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123',
            role='athlete'
        )
        AthleteProfile.objects.create(user=self.user)
        self.dashboard_url = reverse('dashboard')

    # Test 46: Dashboard requires login
    def test_dashboard_requires_login(self):
        """Test dashboard requires authentication"""
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.dashboard_url}")

    # Test 47: Dashboard accessible when logged in
    def test_dashboard_accessible_when_logged_in(self):
        """Test dashboard is accessible when logged in"""
        self.client.force_login(self.user)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

    # Test 48: Dashboard uses correct template
    def test_dashboard_uses_correct_template(self):
        """Test dashboard uses correct template"""
        self.client.force_login(self.user)
        response = self.client.get(self.dashboard_url)
        self.assertTemplateUsed(response, 'user/dashboard.html')


class ProfileViewTests(TestCase):
    """Tests for profile view"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
        self.profile_url = reverse('profile')

    # Test 49: Profile requires login
    def test_profile_requires_login(self):
        """Test profile requires authentication"""
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.profile_url}")

    # Test 50: Profile accessible when logged in
    def test_profile_accessible_when_logged_in(self):
        """Test profile is accessible when logged in"""
        self.client.force_login(self.user)
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)


class ProfileEditViewTests(TestCase):
    """Tests for profile edit view"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            name='Test User',
            password='testpass123'
        )
        self.edit_url = reverse('profile_edit')

    # Test 51: Profile edit requires login
    def test_profile_edit_requires_login(self):
        """Test profile edit requires authentication"""
        response = self.client.get(self.edit_url)
        self.assertRedirects(response, f"{reverse('login')}?next={self.edit_url}")

    # Test 52: Profile edit accessible when logged in
    def test_profile_edit_accessible_when_logged_in(self):
        """Test profile edit is accessible when logged in"""
        self.client.force_login(self.user)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)

    # Test 53: Profile edit updates user data
    def test_profile_edit_updates_user(self):
        """Test profile edit updates user data"""
        self.client.force_login(self.user)
        response = self.client.post(self.edit_url, {
            'name': 'Updated Name',
            'email': 'test@example.com',
            'phone': '1234567890',
            'address': 'New Address'
        })
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Updated Name')
        self.assertEqual(self.user.phone, '1234567890')