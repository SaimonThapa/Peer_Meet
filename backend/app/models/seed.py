import bcrypt


PIXEL_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d4948445200000001000000010802000000907753de"
    "0000000c4944415408d763f8ffff3f0005fe02fea73581e80000000049454e44ae426082"
)


def password_hash(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def seed_database(conn):
    existing = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()["count"]
    if existing:
        return

    users = [
        ("admin", "Admin Simon", "admin@example.test", "AdminPass123!", "admin", "Lab admin account."),
        ("alice", "Alice Wonderlands", "alice@example.test", "Password123!", "user", "Street-photo learner and fixture user."),
        ("bob", "Bob", "bob@example.test", "Password123!", "user", "Fixture account for profile and IDOR labs."),
        ("casey", "Sagun Ghimire", "sagun@ghimire.test", "Password123!", "user", "Security student testing social flows."),
    ]
    for username, display_name, email, password, role, bio in users:
        conn.execute(
            "INSERT INTO users (username, display_name, email, password_hash, role, bio) VALUES (?, ?, ?, ?, ?, ?)",
            (username, display_name, email, password_hash(password), role, bio),
        )

    for owner_id in [1, 2, 3]:
        image_id = conn.execute(
            "INSERT INTO images (owner_id, binary_data, mime_type, byte_size) VALUES (?, ?, ?, ?)",
            (owner_id, PIXEL_PNG, "image/png", len(PIXEL_PNG)),
        ).lastrowid
        conn.execute(
            "INSERT INTO posts (author_id, image_id, caption, seeded) VALUES (?, ?, ?, 1)",
            (owner_id, image_id, f"Synthetic capstone post from user {owner_id}."),
        )

    conn.execute("INSERT INTO follows (follower_id, following_id) VALUES (2, 3)")
    conn.execute("INSERT INTO likes (user_id, post_id) VALUES (2, 1)")
    conn.execute("INSERT INTO comments (post_id, author_id, body) VALUES (1, 2, 'Seeded comment for QA.')")
