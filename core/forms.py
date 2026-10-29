from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import UserProfile

User = get_user_model()


def _style(form):
    for f in form.fields.values():
        w = f.widget
        if isinstance(w, forms.CheckboxInput):
            w.attrs["class"] = "form-check-input"
        elif isinstance(w, forms.Select):
            w.attrs["class"] = "form-select cs-input"
        else:
            w.attrs["class"] = "form-control cs-input"


class RegisterForm(UserCreationForm):
    display_name = forms.CharField(max_length=60, label="Display name")
    email = forms.EmailField(required=False, label="Email (optional)")
    consent = forms.BooleanField(
        required=True,
        label="I understand this is an academic wellness-awareness prototype, not a medical tool, "
              "and I agree to my entries being stored in this application's local database.",
    )

    class Meta:
        model = User
        fields = ("username", "display_name", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.profile
            profile.display_name = self.cleaned_data["display_name"].strip()
            profile.consent_optional_data = True
            profile.save()
        return user


class StyledAuthForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            "display_name", "age_range", "preferred_units", "default_range",
            "resting_hr_baseline", "wellness_goals",
            "notify_checkin", "notify_stress", "notify_data",
        ]
        labels = {
            "notify_checkin": "Daily check-in reminders",
            "notify_stress": "Elevated stress-estimate notifications",
            "notify_data": "Missing or stale data notifications",
            "resting_hr_baseline": "Typical resting heart rate (BPM, optional)",
        }
        widgets = {"wellness_goals": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _style(self)