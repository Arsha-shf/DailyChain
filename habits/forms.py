from django import forms
from .models import Habit

class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = [
            "name",
            "category",
            "color",
            "icon",
            "frequency",
            "times_per_week"
        ]

        widgets = {
            "name": forms.TextInput(attrs={
                "class": "w-full rounded-2xl border border-neutral-700 bg-neutral-900 px-4 py-3 text-white placeholder-neutral-500 focus:border-indigo-500 focus:outline-none"
            }),
            "category": forms.TextInput(attrs={
                "class": "w-full rounded-2xl border border-neutral-700 bg-neutral-900 px-4 py-3 text-white placeholder-neutral-500 focus:border-indigo-500 focus:outline-none"
            }),
            "color": forms.TextInput(attrs={
                "class": "w-full rounded-2xl border border-neutral-700 bg-neutral-900 px-4 py-3 text-white placeholder-neutral-500 focus:border-indigo-500 focus:outline-none"
            }),
            "icon": forms.TextInput(attrs={
                "class": "w-full rounded-2xl border border-neutral-700 bg-neutral-900 px-4 py-3 text-white placeholder-neutral-500 focus:border-indigo-500 focus:outline-none"
            }),
            "frequency": forms.Select(attrs={
                "class": "w-full rounded-2xl border border-neutral-700 bg-neutral-900 px-4 py-3 text-white focus:border-indigo-500 focus:outline-none"
            }),
            "times_per_week": forms.NumberInput(attrs={
                "class": "w-full rounded-2xl border border-neutral-700 bg-neutral-900 px-4 py-3 text-white placeholder-neutral-500 focus:border-indigo-500 focus:outline-none"
            }),
        }
