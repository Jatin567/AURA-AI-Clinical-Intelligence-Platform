import pytest
from datetime import date, datetime, timedelta, timezone
from app.patients import (
    PatientProfile,
    EmergencyContact,
    ProfileValidationError,
    ProfileService,
    InMemoryPatientRepository,
    AuthService,
    InMemoryIdentityRepository,
    InMemorySessionRepository,
    BcryptPasswordService,
    AuthError
)

@pytest.fixture
def auth_service():
    return AuthService(
        InMemoryIdentityRepository(),
        InMemorySessionRepository(),
        BcryptPasswordService()
    )

@pytest.fixture
def profile_service():
    return ProfileService(InMemoryPatientRepository())

def test_auth_flow(auth_service):
    # Registration
    user = auth_service.register("test@test.com", "Password123")
    assert user.email == "test@test.com"
    assert user.is_active is True

    # Duplicate registration fails
    with pytest.raises(AuthError):
        auth_service.register("test@test.com", "otherpassword")

    # Failed login
    with pytest.raises(AuthError):
        auth_service.login("test@test.com", "WrongPassword")

    # Successful login
    session = auth_service.login("test@test.com", "Password123")
    assert session.user_id == user.user_id
    assert session.is_active is True

    # Validate session
    validated_user = auth_service.validate_session(session.session_id)
    assert validated_user is not None
    assert validated_user.user_id == user.user_id

    # Logout
    auth_service.logout(session.session_id)
    assert auth_service.validate_session(session.session_id) is None


def test_profile_validation_pass(profile_service):
    profile = PatientProfile(
        patient_id="p1",
        user_id="u1",
        full_name="John Doe",
        date_of_birth=date(1990, 1, 1),
        biological_sex="M",
        height=180.0,
        weight=75.0,
        blood_group="O+"
    )
    # Should not raise
    saved = profile_service.create_profile(profile)
    assert saved.patient_id == "p1"
    
    retrieved = profile_service.get_profile("p1")
    assert retrieved is not None
    assert retrieved.full_name == "John Doe"

def test_profile_validation_fail_dob(profile_service):
    profile = PatientProfile(
        patient_id="p2",
        user_id="u1",
        full_name="Future Doe",
        date_of_birth=date.today() + timedelta(days=10),
        biological_sex="M"
    )
    with pytest.raises(ProfileValidationError, match="Date of birth must be in the past"):
        profile_service.create_profile(profile)

def test_profile_validation_fail_blood(profile_service):
    profile = PatientProfile(
        patient_id="p3",
        user_id="u1",
        full_name="Blood Doe",
        date_of_birth=date(1990, 1, 1),
        biological_sex="M",
        blood_group="Z+"
    )
    with pytest.raises(ProfileValidationError, match="Invalid blood group"):
        profile_service.create_profile(profile)

def test_profile_validation_fail_duplicates(profile_service):
    profile = PatientProfile(
        patient_id="p4",
        user_id="u1",
        full_name="Meds Doe",
        date_of_birth=date(1990, 1, 1),
        biological_sex="M"
    )
    profile.medications.current_medications = ["Aspirin", "Aspirin"]
    with pytest.raises(ProfileValidationError, match="Duplicate medications found"):
        profile_service.create_profile(profile)

def test_multiple_profiles_per_user(profile_service):
    profile1 = PatientProfile(patient_id="p1", user_id="u1", full_name="A", date_of_birth=date(1990, 1, 1), biological_sex="M")
    profile2 = PatientProfile(patient_id="p2", user_id="u1", full_name="B", date_of_birth=date(1995, 1, 1), biological_sex="F")
    
    profile_service.create_profile(profile1)
    profile_service.create_profile(profile2)
    
    profiles = profile_service.get_profiles_for_user("u1")
    assert len(profiles) == 2
