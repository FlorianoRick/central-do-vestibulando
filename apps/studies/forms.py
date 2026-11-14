from django import forms

from apps.admissions.models import EntranceExam
from .models import MockExamResult, StudyPlan, StudySession, StudySubject


class StudyPlanForm(forms.ModelForm):
    weekly_hours = forms.IntegerField(label="Horas disponíveis por semana", min_value=1, max_value=60, initial=7)
    daily_goal_minutes = forms.IntegerField(label="Meta diária em minutos", min_value=10, max_value=600, initial=60)

    class Meta:
        model = StudyPlan
        fields = ("title", "target_exams", "subjects", "weekly_hours", "daily_goal_minutes", "notes")
        widgets = {
            "target_exams": forms.CheckboxSelectMultiple(),
            "subjects": forms.CheckboxSelectMultiple(),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["target_exams"].queryset = EntranceExam.objects.filter(
            is_active=True,
            institution__is_active=True,
        ).select_related("institution")
        self.fields["subjects"].queryset = StudySubject.objects.filter(is_active=True)
        self.fields["weekly_hours"].help_text = "De 1 a 60 horas."


class StudySessionForm(forms.ModelForm):
    duration_minutes = forms.IntegerField(label="Duração em minutos", min_value=10, max_value=600, initial=60)

    class Meta:
        model = StudySession
        fields = ("subject", "scheduled_for", "duration_minutes", "topic", "difficult_topic", "status", "notes")
        widgets = {
            "scheduled_for": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"].queryset = StudySubject.objects.filter(is_active=True)


class MockExamResultForm(forms.ModelForm):
    class Meta:
        model = MockExamResult
        fields = ("title", "exam", "taken_on", "score", "maximum_score", "notes")
        widgets = {"taken_on": forms.DateInput(attrs={"type": "date"}), "notes": forms.Textarea(attrs={"rows": 2})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["exam"].queryset = EntranceExam.objects.filter(
            is_active=True,
            institution__is_active=True,
        ).select_related("institution")

    def clean(self):
        cleaned_data = super().clean()
        score = cleaned_data.get("score")
        maximum_score = cleaned_data.get("maximum_score")
        if score is not None and score < 0:
            self.add_error("score", "A pontuação não pode ser negativa.")
        if maximum_score is not None and maximum_score <= 0:
            self.add_error("maximum_score", "A pontuação máxima deve ser maior que zero.")
        if score is not None and maximum_score is not None and score > maximum_score:
            self.add_error("score", "A pontuação não pode ser maior que a pontuação máxima.")
        return cleaned_data


class SyllabusCompareForm(forms.Form):
    exams = forms.ModelMultipleChoiceField(
        label="Selecione até três vestibulares",
        queryset=EntranceExam.objects.none(),
        required=True,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["exams"].queryset = EntranceExam.objects.filter(
            is_active=True,
            institution__is_active=True,
        ).select_related("institution")

    def clean_exams(self):
        exams = self.cleaned_data["exams"]
        if len(exams) > 3:
            raise forms.ValidationError("Escolha no máximo três processos seletivos.")
        return exams
