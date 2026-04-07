from django.contrib import admin
from .models import Sport, CoachRequest, AthleteCoach, DailyRoutine, AthleteSport


@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(CoachRequest)
class CoachRequestAdmin(admin.ModelAdmin):
    list_display = ('athlete', 'coach', 'sport', 'status', 'created_at')
    list_filter = ('status', 'sport', 'created_at')
    search_fields = ('athlete__first_name', 'athlete__last_name', 'coach__first_name', 'coach__last_name')


@admin.register(AthleteCoach)
class AthleteCoachAdmin(admin.ModelAdmin):
    list_display = ('athlete', 'coach', 'sport', 'start_date', 'is_active')
    list_filter = ('is_active', 'sport', 'start_date')
    search_fields = ('athlete__first_name', 'athlete__last_name', 'coach__first_name', 'coach__last_name')


@admin.register(DailyRoutine)
class DailyRoutineAdmin(admin.ModelAdmin):
    list_display = ('title', 'athlete', 'coach', 'sport', 'day', 'start_time', 'end_time')
    list_filter = ('day', 'sport', 'coach')
    search_fields = ('title', 'athlete__first_name', 'athlete__last_name')


@admin.register(AthleteSport)
class AthleteSportAdmin(admin.ModelAdmin):
    list_display = ('athlete', 'sport', 'skill_level', 'joined_at')
    list_filter = ('sport', 'skill_level')
    search_fields = ('athlete__first_name', 'athlete__last_name')

