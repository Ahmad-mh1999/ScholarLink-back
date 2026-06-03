from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import (
    views_accounts,
    views_articles,
    views_categories,
    views_comments,
    views_reviews,
    views_notifications,
    views_stats,
)
from . import views_points, views_admin
from . import views_articles_moderation

urlpatterns = [
    # ─── Authentication ───
    path('auth/register/', views_accounts.RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', views_accounts.LogoutView.as_view(), name='logout'),
    path('auth/verify-email/<uidb64>/<token>/', views_accounts.VerifyEmailView.as_view(), name='verify_email'),
    path('auth/resend-verification/', views_accounts.ResendVerificationView.as_view(), name='resend_verification'),
    path('auth/forgot-password/', views_accounts.ForgotPasswordView.as_view(), name='forgot_password'),
    path('auth/reset-password/<uidb64>/<token>/', views_accounts.ResetPasswordView.as_view(), name='reset_password'),

    # ─── Users ───
    path('users/me/', views_accounts.ProfileView.as_view(), name='profile'),
    path('users/<str:username>/', views_accounts.UserDetailView.as_view(), name='user_detail'),
    path('users/<str:username>/follow/', views_accounts.FollowView.as_view(), name='follow'),

    # ─── Articles ───
    path('articles/', views_articles.ArticleListView.as_view(), name='article_list'),
    path('articles/public-journals/', views_articles.PublicJournalsListView.as_view(), name='public_journals'),
    path('articles/my/', views_articles.MyArticlesView.as_view(), name='my_articles'),
    path('articles/bookmarks/', views_articles.MyBookmarksView.as_view(), name='my_bookmarks'),
    path('articles/<slug:slug>/', views_articles.ArticleDetailView.as_view(), name='article_detail'),
    path('articles/<slug:slug>/like/', views_articles.ArticleLikeView.as_view(), name='article_like'),
    path('articles/<slug:slug>/rate/', views_articles.ArticleRatingView.as_view(), name='article_rate'),
    path('articles/<slug:slug>/bookmark/', views_articles.BookmarkView.as_view(), name='article_bookmark'),
    path('articles/<slug:slug>/citation/', views_articles.CitationView.as_view(), name='article_citation'),
    path('articles/<slug:slug>/recommendations/', views_articles.RecommendationsView.as_view(), name='article_recommendations'),
    path('articles/<int:id>/recommend-journals/', views_articles.RecommendJournalsView.as_view(), name='article_recommend_journals'),
    path('articles/<slug:slug>/comments/', views_comments.CommentListView.as_view(), name='comment_list'),

    path('articles/<slug:slug>/reviews/', views_reviews.ReviewListView.as_view(), name='review_list'),
    path('admin/dashboard/', views_accounts.AdminDashboardView.as_view(), name='admin_dashboard'),

    # ─── Comments ───
    path('comments/<int:pk>/', views_comments.CommentDetailView.as_view(), name='comment_detail'),
    path('comments/<int:pk>/like/', views_comments.CommentLikeView.as_view(), name='comment_like'),

    # ─── Reviews ───
    path('reviews/<int:pk>/', views_reviews.ReviewDetailView.as_view(), name='review_detail'),

    # ─── Categories ───
    path('categories/', views_categories.CategoryListView.as_view(), name='category_list'),
    path('categories/<slug:slug>/', views_categories.CategoryDetailView.as_view(), name='category_detail'),

    # ─── Notifications ───
    path('notifications/', views_notifications.NotificationListView.as_view(), name='notification_list'),
    path('notifications/unread/', views_notifications.UnreadCountView.as_view(), name='unread_count'),
    path('notifications/mark-all-read/', views_notifications.NotificationMarkAllReadView.as_view(), name='mark_all_read'),
    path('notifications/<int:pk>/read/', views_notifications.NotificationMarkReadView.as_view(), name='mark_read'),
    path('notifications/send/', views_notifications.SendNotificationView.as_view(), name='send_notification'),

    # ─── Stats ───
    path('stats/platform/', views_stats.PlatformStatsView.as_view(), name='platform_stats'),
    path('stats/articles-by-category/', views_stats.ArticlesByCategoryView.as_view(), name='articles_by_category'),
    path('stats/monthly-articles/', views_stats.MonthlyArticlesView.as_view(), name='monthly_articles'),
    path('stats/top-authors/', views_stats.TopAuthorsView.as_view(), name='top_authors'),
    path('stats/most-read/', views_stats.MostReadArticlesView.as_view(), name='most_read'),

    # ─── Advanced Reviews ───
    path('reviews/dashboard/', views_reviews.ReviewerDashboardView.as_view(), name='reviewer_dashboard'),
    path('reviews/<int:pk>/respond/', views_reviews.RespondToReviewRequestView.as_view(), name='respond_review'),
    path('reviews/<int:pk>/submit/', views_reviews.SubmitReviewView.as_view(), name='submit_review'),
    path('articles/<slug:slug>/assign-reviewer/', views_reviews.AssignReviewerView.as_view(), name='assign_reviewer'),
    path('articles/<slug:slug>/nominate-journal/', views_reviews.ReviewerNominateJournalView.as_view(), name='reviewer_nominate_journal'),

    # ─── Points ───
    path('points/my/', views_points.MyPointsView.as_view(), name='my_points'),
    path('points/transactions/', views_points.MyTransactionsView.as_view(), name='my_transactions'),
    path('points/leaderboard/', views_points.LeaderboardView.as_view(), name='leaderboard'),

    # ─── Admin ───
    path('admin/stats/', views_admin.AdminStatsView.as_view(), name='admin_stats'),
    path('admin/users/', views_admin.AdminUsersListView.as_view(), name='admin_users'),
    path('admin/users/<int:id>/', views_admin.AdminUserDetailView.as_view(), name='admin_user_detail'),
    path('admin/users/<int:id>/activate/', views_admin.ActivateUserView.as_view(), name='activate_user'),
    path('admin/users/<int:id>/deactivate/', views_admin.DeactivateUserView.as_view(), name='deactivate_user'),
    path('admin/articles/', views_admin.AdminArticlesListView.as_view(), name='admin_articles'),
    path('admin/articles/<slug:slug>/', views_admin.AdminArticleDetailView.as_view(), name='admin_article_detail'),
    path('admin/articles/<slug:slug>/journal-recommendations/', views_admin.AdminArticleJournalRecommendationsView.as_view(), name='admin_article_journal_recommendations'),
    path('admin/articles/<slug:slug>/assign-reviewer/', views_admin.AdminArticleAssignReviewerView.as_view(), name='admin_article_assign_reviewer'),
    path('admin/articles/<slug:slug>/nominate-journal/', views_admin.AdminArticleNominateJournalView.as_view(), name='admin_article_nominate_journal'),
    path('admin/articles/<slug:slug>/publish/', views_admin.AdminArticlePublishView.as_view(), name='admin_article_publish'),
    path('admin/articles/<slug:slug>/accept/', views_admin.AdminArticleAcceptView.as_view(), name='admin_article_accept'),
    path('admin/articles/<slug:slug>/reject/', views_admin.AdminArticleRejectView.as_view(), name='admin_article_reject'),
    path('admin/categories/', views_admin.AdminCategoriesListView.as_view(), name='admin_categories'),
    path('admin/categories/<int:id>/', views_admin.AdminCategoryDetailView.as_view(), name='admin_category_detail'),
    path('admin/send-notification/', views_admin.SendNotificationView.as_view(), name='send_notification'),

    # ─── Journals (Admin CRUD) ───
    path('admin/journals/', views_admin.AdminJournalsListCreateView.as_view(), name='admin_journals'),
    path('admin/journals/<int:id>/', views_admin.AdminJournalDetailView.as_view(), name='admin_journal_detail'),

    # moderation endpoint (used by frontend in /api/v1/articles/submission/moderate/)
    path('articles/submission/moderate/', views_articles_moderation.ArticleSubmissionModerateView.as_view(), name='article_submission_moderate'),

    # ─── Landing Page Stats (Public) ───
    path('landing-stats/', views_articles.LandingStatsView.as_view(), name='landing_stats'),
]
