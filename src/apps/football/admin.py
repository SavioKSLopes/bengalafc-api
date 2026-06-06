from django.contrib import admin
from .models import (
    Competition,
    Fixture,
    Player,
    PlayerStatistic,
    Stage,
    Team,
    TeamStatistic,
)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "external_id", "name", "code", "country", "is_active")
    search_fields = ("name", "code", "country")
    list_filter = ("is_active", "country")
    ordering = ("name",)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "external_id",
        "name",
        "team",
        "position",
        "number",
        "is_active",
    )
    search_fields = ("name", "position", "nationality")
    list_filter = ("position", "is_active", "team")
    ordering = ("name",)


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ("id", "external_id", "name", "type", "season")
    search_fields = ("name", "type")
    list_filter = ("season", "type")
    ordering = ("-season", "name")


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ("id", "competition", "name", "order")
    search_fields = ("name",)
    list_filter = ("competition",)
    ordering = ("competition", "order", "name")


@admin.register(Fixture)
class FixtureAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "external_id",
        "competition",
        "stage",
        "home_team",
        "away_team",
        "kickoff_at",
        "status",
    )
    search_fields = ("home_team__name", "away_team__name", "venue")
    list_filter = ("competition", "stage", "status")
    ordering = ("kickoff_at",)


@admin.register(PlayerStatistic)
class PlayerStatisticAdmin(admin.ModelAdmin):
    list_display = ("id", "player", "fixture", "minutes", "goals", "assists", "rating")
    search_fields = (
        "player__name",
        "fixture__home_team__name",
        "fixture__away_team__name",
    )
    list_filter = ("fixture__competition",)
    ordering = ("-fixture__kickoff_at",)


@admin.register(TeamStatistic)
class TeamStatisticAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "team",
        "fixture",
        "possession",
        "shots",
        "yellow_cards",
        "red_cards",
    )
    search_fields = (
        "team__name",
        "fixture__home_team__name",
        "fixture__away_team__name",
    )
    list_filter = ("fixture__competition",)
    ordering = ("-fixture__kickoff_at",)
