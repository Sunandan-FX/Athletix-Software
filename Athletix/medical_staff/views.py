<<<<<<< HEAD
from django.shortcuts import render

# Create your views here.
=======
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from user.models import User
from .forms import MedicalFeedbackForm, MedicalFeedbackOnRecordForm
from .models import AthleteHealthRecord, MedicalFeedback


def medical_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.role != 'medical':
            messages.error(request, 'Access denied. Medical staff only.')
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@medical_required
def dashboard(request):
    assigned_records_qs = AthleteHealthRecord.objects.select_related('athlete', 'medical_staff').filter(
        medical_staff=request.user
    )
    athletes = User.objects.filter(role='athlete', is_active=True).order_by('name')
    assigned_athletes = User.objects.filter(
        id__in=assigned_records_qs.values_list('athlete_id', flat=True).distinct(),
        role='athlete',
        is_active=True,
    ).order_by('name')
    selected_athlete_id = request.GET.get('athlete', '').strip()
    selected_athlete = None
    if selected_athlete_id.isdigit():
        selected_athlete = assigned_athletes.filter(id=int(selected_athlete_id)).first()

    records_qs = assigned_records_qs
    feedback_qs = MedicalFeedback.objects.select_related('athlete')
    if selected_athlete:
        records_qs = records_qs.filter(athlete=selected_athlete)
        feedback_qs = feedback_qs.filter(athlete=selected_athlete, medical_staff=request.user)
    else:
        feedback_qs = feedback_qs.filter(medical_staff=request.user)

    latest_health_records = records_qs.order_by('-created_at')[:12]
    latest_feedbacks = feedback_qs.order_by('-created_at')[:12]
    all_records = records_qs.select_related('athlete').order_by('athlete_id', '-created_at')

    latest_record_by_athlete = {}
    for record in all_records:
        if record.athlete_id not in latest_record_by_athlete:
            latest_record_by_athlete[record.athlete_id] = record

    athlete_health_rows = []
    if selected_athlete:
        athlete_health_rows.append(
            {
                'athlete': selected_athlete,
                'latest_record': latest_record_by_athlete.get(selected_athlete.id),
            }
        )

    injury_summary = assigned_records_qs.values('injury_status').annotate(
        total=Count('id')
    ).order_by('-total')
    recovery_watch_count = assigned_records_qs.filter(
        Q(recovery_status='watch') | Q(recovery_status='critical')
    ).count()

    feedback_form = MedicalFeedbackForm()
    if selected_athlete:
        feedback_form.fields['athlete'].queryset = assigned_athletes.filter(id=selected_athlete.id)
        feedback_form.fields['athlete'].initial = selected_athlete.id
    else:
        feedback_form.fields['athlete'].queryset = assigned_athletes

    context = {
        'athletes_count': assigned_athletes.count(),
        'records_count': assigned_records_qs.count(),
        'feedback_count': MedicalFeedback.objects.filter(medical_staff=request.user).count(),
        'recovery_watch_count': recovery_watch_count,
        'latest_health_records': latest_health_records,
        'athlete_health_rows': athlete_health_rows,
        'latest_feedbacks': latest_feedbacks,
        'injury_summary': injury_summary,
        'feedback_form': feedback_form,
        'athletes': assigned_athletes,
        'selected_athlete': selected_athlete,
        'selected_athlete_id': selected_athlete_id,
    }
    return render(request, 'medical_staff/dashboard.html', context)


@login_required
@medical_required
def add_feedback(request):
    if request.method != 'POST':
        return redirect('medical_staff:dashboard')

    form = MedicalFeedbackForm(request.POST)
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.medical_staff = request.user
        has_assigned_record = AthleteHealthRecord.objects.filter(
            athlete=feedback.athlete,
            medical_staff=request.user
        ).exists()
        if not has_assigned_record:
            messages.error(request, 'You can only send feedback to athletes assigned to you.')
            return redirect('medical_staff:dashboard')
        feedback.save()
        messages.success(request, 'Medical feedback submitted successfully.')
    else:
        messages.error(request, 'Please fix errors in feedback form.')
    return redirect('medical_staff:dashboard')


@login_required
@medical_required
def add_feedback_for_record(request, record_id):
    if request.method != 'POST':
        return redirect('medical_staff:dashboard')

    record = get_object_or_404(
        AthleteHealthRecord.objects.select_related('athlete'),
        id=record_id,
        medical_staff=request.user
    )
    form = MedicalFeedbackOnRecordForm(request.POST)
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.athlete = record.athlete
        feedback.medical_staff = request.user
        feedback.save()
        if record.medical_staff_id is None:
            record.medical_staff = request.user
            record.save(update_fields=['medical_staff'])
        messages.success(request, 'Medical feedback submitted successfully.')
    else:
        messages.error(request, 'Please fix errors in feedback form.')
    return redirect('medical_staff:dashboard')
>>>>>>> cb7b4b6 (Apply local project updates)
