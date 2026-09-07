from django import forms

from .models import Chore, Family, Profile, Reward


class BountyForm(forms.ModelForm):
    """A parent posting a one-off, higher-value task to the bounty board."""

    class Meta:
        model = Chore
        fields = ['title', 'points']
        labels = {'title': 'Bounty', 'points': 'Points'}

    def __init__(self, *args, family=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.family = family

    def clean_title(self):
        title = self.cleaned_data['title']
        if self.family and self.family.chores.filter(title=title).exists():
            raise forms.ValidationError(
                f'{self.family.name} already has a chore called "{title}".'
            )
        return title

    def save(self, commit=True):
        chore = super().save(commit=False)
        chore.family = self.family
        chore.kind = Chore.Kind.BOUNTY
        if commit:
            chore.save()
        return chore


class FamilySetupForm(forms.Form):
    """First run: name the household and the parent using it."""

    family_name = forms.CharField(max_length=100, label='Family name')
    your_name = forms.CharField(max_length=50, label='Your name')

    def create_for(self, user):
        family = Family.objects.create(name=self.cleaned_data['family_name'])
        Profile.objects.create(
            family=family,
            user=user,
            display_name=self.cleaned_data['your_name'],
            role=Profile.Role.PARENT,
        )
        return family


class ChildForm(forms.Form):
    """Adding a child. They get a profile, never an account."""

    display_name = forms.CharField(max_length=50, label='Child')

    def __init__(self, *args, family=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.family = family

    def clean_display_name(self):
        name = self.cleaned_data['display_name']
        if self.family and self.family.members.filter(display_name=name).exists():
            raise forms.ValidationError(f'{name} is already in this family.')
        return name

    def save(self):
        return Profile.objects.create(
            family=self.family,
            display_name=self.cleaned_data['display_name'],
            role=Profile.Role.CHILD,
        )


class RoutineChoreForm(forms.ModelForm):
    """A recurring chore for the weekly rotation."""

    class Meta:
        model = Chore
        fields = ['title', 'points']
        labels = {'title': 'Chore', 'points': 'Points'}

    def __init__(self, *args, family=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.family = family

    def clean_title(self):
        title = self.cleaned_data['title']
        if self.family and self.family.chores.filter(title=title).exists():
            raise forms.ValidationError(
                f'{self.family.name} already has a chore called "{title}".'
            )
        return title

    def save(self, commit=True):
        chore = super().save(commit=False)
        chore.family = self.family
        chore.kind = Chore.Kind.ROUTINE
        if commit:
            chore.save()
        return chore


class RewardForm(forms.ModelForm):
    """Something a child can buy with points."""

    class Meta:
        model = Reward
        fields = ['name', 'cost']
        labels = {'name': 'Reward', 'cost': 'Cost in points'}

    def __init__(self, *args, family=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.family = family

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.family and self.family.rewards.filter(name=name).exists():
            raise forms.ValidationError(
                f'{self.family.name} already offers "{name}".'
            )
        return name

    def save(self, commit=True):
        reward = super().save(commit=False)
        reward.family = self.family
        if commit:
            reward.save()
        return reward
