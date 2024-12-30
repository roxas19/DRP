from django.contrib import admin
from .models import DiscussionPost, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('content', 'author', 'is_flagged', 'flag_count')
    readonly_fields = ('flag_count',)


class DiscussionPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'weekly_module', 'created_at', 'is_flagged', 'flag_count')
    list_filter = ('is_flagged', 'created_at', 'weekly_module')
    search_fields = ('title', 'author__name', 'weekly_module__title')
    ordering = ('-created_at',)
    inlines = [CommentInline]

    actions = ['reset_flags']

    def reset_flags(self, request, queryset):
        queryset.update(flag_count=0, is_flagged=False)
        self.message_user(request, "Selected posts have been reset.")
    reset_flags.short_description = "Reset flags for selected posts"


class CommentAdmin(admin.ModelAdmin):
    list_display = ('content', 'author', 'post', 'created_at', 'is_flagged', 'flag_count')
    list_filter = ('is_flagged', 'created_at', 'post')
    search_fields = ('content', 'author__name', 'post__title')
    ordering = ('-created_at',)

    actions = ['reset_flags']

    def reset_flags(self, request, queryset):
        queryset.update(flag_count=0, is_flagged=False)
        self.message_user(request, "Selected comments have been reset.")
    reset_flags.short_description = "Reset flags for selected comments"


admin.site.register(DiscussionPost, DiscussionPostAdmin)
admin.site.register(Comment, CommentAdmin)
