from django import forms

from .models import Chore


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
