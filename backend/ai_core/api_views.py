from __future__ import annotations

from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from core.i18n import get_user_language, translate

from .models import SocialMediaPost
from .publish_instagram import publish_to_instagram
from .publish_linkedin import publish_to_linkedin
from .publish_tiktok import publish_to_tiktok
from .social_media import generate_social_image, generate_social_post, save_generated_post


_ALLOWED_PLATFORMS = {
    SocialMediaPost.PLATFORM_INSTAGRAM,
    SocialMediaPost.PLATFORM_TIKTOK,
    SocialMediaPost.PLATFORM_LINKEDIN,
}

_SOCIAL_COPY = {
    "ro": {
        "topic_required": "Campul topic este obligatoriu.",
        "invalid_platform": "Platforma selectata nu este valida.",
        "post_id_required": "Campul post_id este obligatoriu.",
        "post_not_found": "Postarea nu a fost gasita.",
        "ownership_forbidden": "Nu ai acces la aceasta postare.",
        "post_generated": "Postare generata si salvata ca ciorna.",
        "platform_mismatch": "Platforma solicitata nu corespunde cu platforma postarii.",
        "already_published": "Postarea a fost deja publicata.",
    },
    "en": {
        "topic_required": "topic is required",
        "invalid_platform": "invalid platform",
        "post_id_required": "post_id is required",
        "post_not_found": "post not found",
        "ownership_forbidden": "You do not have access to this post.",
        "post_generated": "Post generated and saved as draft.",
        "platform_mismatch": "Requested platform does not match post platform.",
        "already_published": "Post is already published.",
    },
}


def _social_text(user, key: str) -> str:
    return translate(_SOCIAL_COPY, get_user_language(user)).get(key, _SOCIAL_COPY["en"][key])


def _serialize_post(post: SocialMediaPost) -> dict:
    return {
        "id": post.pk,
        "platform": post.platform,
        "title": post.title,
        "body": post.body,
        "hashtags": post.hashtags,
        "image_url": post.image_url,
        "video_url": post.video_url,
        "owner": post.owner,
        "owner_user_id": post.owner_user_id,
        "wellness_topic": post.wellness_topic,
        "status": post.status,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "posted_at": post.posted_at.isoformat() if post.posted_at else None,
        "publish_log": post.publish_log,
    }


class SocialPostsListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        queryset = SocialMediaPost.objects.filter(owner_user=request.user).order_by("-created_at")

        platform = (request.query_params.get("platform") or "").strip().lower()
        if platform:
            queryset = queryset.filter(platform=platform)

        status_value = (request.query_params.get("status") or "").strip().lower()
        if status_value:
            queryset = queryset.filter(status=status_value)

        search = (request.query_params.get("search") or "").strip()
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(wellness_topic__icontains=search)
                | Q(body__icontains=search)
            )

        return Response({"items": [_serialize_post(post) for post in queryset]})


class SocialGenerateView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        platform = (request.data.get("platform") or SocialMediaPost.PLATFORM_INSTAGRAM).strip().lower()
        topic = (request.data.get("topic") or "").strip()

        if not topic:
            return Response({"detail": _social_text(request.user, "topic_required")}, status=status.HTTP_400_BAD_REQUEST)

        if platform not in _ALLOWED_PLATFORMS:
            return Response({"detail": _social_text(request.user, "invalid_platform")}, status=status.HTTP_400_BAD_REQUEST)

        generated = generate_social_post(topic=topic, platform=platform)
        generated["image_url"] = generate_social_image(
            f"{generated.get('wellness_topic', topic)} {platform} social post"
        )
        saved = save_generated_post(
            {
                **generated,
                "owner_user": request.user,
                "status": SocialMediaPost.STATUS_DRAFT,
                "publish_log": "Auto-saved from Social API generator.",
            }
        )

        return Response(
            {
                "post": _serialize_post(saved),
                "detail": _social_text(request.user, "post_generated"),
            },
            status=status.HTTP_201_CREATED,
        )


class SocialPublishView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        post_id = request.data.get("post_id")
        platform = (request.data.get("platform") or "").strip().lower()

        if not post_id:
            return Response({"detail": _social_text(request.user, "post_id_required")}, status=status.HTTP_400_BAD_REQUEST)
        if platform not in _ALLOWED_PLATFORMS:
            return Response({"detail": _social_text(request.user, "invalid_platform")}, status=status.HTTP_400_BAD_REQUEST)

        post = SocialMediaPost.objects.filter(pk=post_id).first()
        if not post:
            return Response({"detail": _social_text(request.user, "post_not_found")}, status=status.HTTP_404_NOT_FOUND)

        if post.owner_user_id != request.user.id:
            return Response({"detail": _social_text(request.user, "ownership_forbidden")}, status=status.HTTP_403_FORBIDDEN)

        if post.platform != platform:
            return Response(
                {
                    "detail": _social_text(request.user, "platform_mismatch"),
                    "post_platform": post.platform,
                },
                status=status.HTTP_409_CONFLICT,
            )

        if post.status == SocialMediaPost.STATUS_POSTED:
            return Response(
                {
                    "detail": _social_text(request.user, "already_published"),
                    "post": _serialize_post(post),
                },
                status=status.HTTP_200_OK,
            )

        publishers = {
            SocialMediaPost.PLATFORM_INSTAGRAM: publish_to_instagram,
            SocialMediaPost.PLATFORM_TIKTOK: publish_to_tiktok,
            SocialMediaPost.PLATFORM_LINKEDIN: publish_to_linkedin,
        }
        ok, message = publishers[platform](post)
        post.refresh_from_db()

        if ok:
            return Response(
                {
                    "detail": message,
                    "post": _serialize_post(post),
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "detail": message,
                "post": _serialize_post(post),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
