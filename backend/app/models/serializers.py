def user_public(row):
    if not row:
        return None
    return {
        "id": row["id"],
        "username": row["username"],
        "displayName": row["display_name"],
        "bio": row["bio"],
        "role": row["role"],
        "avatarUrl": f"/images/{row['avatar_image_id']}" if row["avatar_image_id"] else None,
    }


def post_public(row):
    return {
        "id": row["id"],
        "caption": row["caption"] or "",
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
        "imageUrl": f"/images/{row['image_id']}",
        "author": {
            "id": row["author_id"],
            "username": row["username"],
            "displayName": row["display_name"],
            "avatarUrl": f"/images/{row['avatar_image_id']}" if row["avatar_image_id"] else None,
        },
        "likeCount": row["like_count"],
        "commentCount": row["comment_count"],
        "likedByMe": bool(row["liked_by_me"]),
    }
