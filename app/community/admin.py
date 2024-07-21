from django.contrib import admin
from .models import (
    Community,
    CommunityDetail,
    CommunityMembership,
    CommunityJoinRequest,
    Event,
    EventCollaboration,
    EventRegistration,
    Payment,
)

# Register your models here.
@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_published', 'is_active', 'area', 'cover_image', 'logo', 'color')
    list_filter = ('is_published', 'is_active')
    search_fields = ('name', 'description')


@admin.register(CommunityDetail)
class CommunityDetailAdmin(admin.ModelAdmin):
    list_display = ('community', 'additional_info', 'rules')
    search_fields = ('community__name', 'additional_info', 'rules')


@admin.register(CommunityMembership)
class CommunityMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'community', 'role', 'joined_at')
    list_filter = ('role',)
    search_fields = ('user__username', 'community__name')


@admin.register(CommunityJoinRequest)
class CommunityJoinRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'community', 'created_at', 'status')
    list_filter = ('status',)
    search_fields = ('user__username', 'community__name')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'organized_by', 'is_free', 'fees', 'currency')
    list_filter = ('is_free', 'currency')
    search_fields = ('name', 'description', 'organized_by__name')


@admin.register(EventCollaboration)
class EventCollaborationAdmin(admin.ModelAdmin):
    list_display = ('event', 'collaborating_community', 'status')
    list_filter = ('status',)
    search_fields = ('event__name', 'collaborating_community__name')


@admin.register(EventRegistration)
class EventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'event', 'registered_at', 'payment_status')
    list_filter = ('payment_status',)
    search_fields = ('user__username', 'event__name')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('registration', 'payment_method', 'amount', 'status')
    list_filter = ('payment_method', 'status')
    search_fields = ('registration__user__username', 'registration__event__name')
