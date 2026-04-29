# =============================================================================
# database/db.py
# BukidKnown – SQLite database connection and all CRUD operations
# =============================================================================

import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "bukidknown.db")


# -----------------------------------------------------------------------------
# CONNECTION
# -----------------------------------------------------------------------------

def get_connection():
    """Return a SQLite connection with row_factory enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


# -----------------------------------------------------------------------------
# SCHEMA INITIALIZATION
# -----------------------------------------------------------------------------

def init_db():
    """Create all tables if they do not exist, then seed sample data."""
    conn = get_connection()
    c = conn.cursor()

    # TABLE: users
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            role     TEXT    NOT NULL DEFAULT 'tourist',
            name     TEXT    DEFAULT '',
            email    TEXT    DEFAULT '',
            created_at TEXT  DEFAULT (datetime('now'))
        )
    """)

    # TABLE: destinations
    c.execute("""
        CREATE TABLE IF NOT EXISTS destinations (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            name           TEXT    NOT NULL,
            description    TEXT,
            location       TEXT,
            category       TEXT,
            entrance_fee   REAL    DEFAULT 0,
            estimated_cost REAL    DEFAULT 0,
            image_path     TEXT    DEFAULT '',
            latitude       REAL    DEFAULT 0,
            longitude      REAL    DEFAULT 0,
            safety_tips    TEXT    DEFAULT '',
            municipality   TEXT    DEFAULT '',
            is_approved    INTEGER DEFAULT 1,
            created_at     TEXT    DEFAULT (datetime('now'))
        )
    """)

    # TABLE: businesses
    c.execute("""
        CREATE TABLE IF NOT EXISTS businesses (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER DEFAULT 0,
            business_name  TEXT    NOT NULL,
            description    TEXT,
            address        TEXT,
            contact_number TEXT,
            category       TEXT,
            image_path     TEXT    DEFAULT '',
            is_priority    INTEGER DEFAULT 0,
            is_verified    INTEGER DEFAULT 0,
            views          INTEGER DEFAULT 0,
            clicks         INTEGER DEFAULT 0,
            inquiries      INTEGER DEFAULT 0,
            created_at     TEXT    DEFAULT (datetime('now'))
        )
    """)

    # TABLE: bookings
    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            tourist_name   TEXT    NOT NULL,
            tourist_id     INTEGER DEFAULT 0,
            destination    TEXT    NOT NULL,
            destination_id INTEGER DEFAULT 0,
            agency_name    TEXT    DEFAULT 'BukidKnown Tours',
            tour_date      TEXT    DEFAULT '',
            num_persons    INTEGER DEFAULT 1,
            contact        TEXT    DEFAULT '',
            notes          TEXT    DEFAULT '',
            status         TEXT    DEFAULT 'Pending',
            created_at     TEXT    DEFAULT (datetime('now'))
        )
    """)

    # TABLE: reviews
    c.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id             INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id        INTEGER NOT NULL,
            destination_id INTEGER NOT NULL,
            rating         INTEGER NOT NULL,
            comment        TEXT    DEFAULT '',
            reviewer_name  TEXT    DEFAULT 'Anonymous',
            created_at     TEXT    DEFAULT (datetime('now'))
        )
    """)

    # TABLE: chat_messages
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            sender     TEXT    NOT NULL,
            message    TEXT    NOT NULL,
            created_at TEXT    DEFAULT (datetime('now'))
        )
    """)

    # TABLE: notifications
    c.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            title      TEXT    NOT NULL,
            message    TEXT    NOT NULL,
            is_read    INTEGER DEFAULT 0,
            created_at TEXT    DEFAULT (datetime('now'))
        )
    """)

    conn.commit()
    _seed_sample_data(conn)
    conn.close()


# -----------------------------------------------------------------------------
# SEED DATA
# -----------------------------------------------------------------------------

def _hash(pw):
    return hashlib.sha256(pw.encode()).hexdigest()


def _seed_sample_data(conn):
    """Insert sample data only on first run (when destinations table is empty)."""
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM destinations")
    if c.fetchone()[0] > 0:
        return  # Already seeded

    # ── USERS ─────────────────────────────────────────────────────────────
    users = [
        ("admin",    _hash("admin123"),    "admin",   "Admin User",     "admin@bukidknown.ph"),
        ("tourist1", _hash("tourist123"),  "tourist", "Juan dela Cruz", "juan@email.com"),
        ("business1",_hash("business123"), "business","Maria Santos",   "maria@email.com"),
    ]
    c.executemany(
        "INSERT OR IGNORE INTO users (username,password,role,name,email) VALUES (?,?,?,?,?)",
        users
    )

    # ── DESTINATIONS ──────────────────────────────────────────────────────
    destinations = [
        # Waterfalls
        (
            "Limugpud Falls",
            "A stunning twin waterfall hidden deep in the rainforest of Impasug-ong. "
            "The cascading water drops into a refreshing natural pool surrounded by lush vegetation.",
            "Impasug-ong, Bukidnon",
            "Waterfall",
            30, 350,
            "https://upload.wikimedia.org/wikipedia/commons/2/2d/Limunsudan_Falls.jpg",
            8.2916, 125.0003,
            "Wear trekking shoes. Hire a local guide. Avoid visiting after heavy rain.",
            "Impasug-ong"
        ),
        (
            "Cedar Falls",
            "A majestic multi-tiered waterfall along the Pulangui River, popular among locals "
            "for swimming and picnicking. Accessible via a short trek through farmland.",
            "Malaybalay, Bukidnon",
            "Waterfall",
            20, 250,
            "https://diri-ta-bukidnon.weebly.com/uploads/1/7/3/0/17309182/1275640_orig.jpg",
            8.1200, 125.0890,
            "No swimming alone. Bring life vest. Register at barangay hall.",
            "Malaybalay"
        ),
        # Resorts / Nature
        (
            "Lake Apo",
            "The largest lake in Mindanao and a biodiversity hotspot. Home to the endemic "
            "Philippine duck and surrounded by rolling grasslands. Perfect for bird-watching and kayaking.",
            "Quezon, Bukidnon",
            "Nature",
            50, 500,
            "https://i2.wp.com/www.projectlupad.com/wp-content/uploads/2023/06/Lake-Apo-Valencia-Copyright-to-Project-LUPAD-2-1024x576.jpg?ssl=1",
            8.0243, 125.0935,
            "Wear life vest during boat rides. No littering. Respect wildlife.",
            "Quezon"
        ),
        (
            "Panoloon Cold Spring",
            "Crystal-clear cold spring emerging from underground limestone formations. "
            "Surrounded by bamboo groves and native trees — a perfect escape from the summer heat.",
            "San Fernando, Bukidnon",
            "Nature",
            30, 200,
            "https://scontent.fcgy3-2.fna.fbcdn.net/v/t39.30808-6/607854105_904255528941956_5259530264569131108_n.jpg?_nc_cat=101&ccb=1-7&_nc_sid=7b2446&_nc_ohc=Lhu-6G9eGn0Q7kNvwEU6eaG&_nc_oc=Adr6IqtbR3WlEbKzBF3T_cze-HRPmPdtKVcCTYCILnDKp3fy4A-z77eh4YtNTavzdwY&_nc_zt=23&_nc_ht=scontent.fcgy3-2.fna&_nc_gid=018NQnaWaoZ75yPDhxm-6g&_nc_ss=7b289&oh=00_Af0vqI5EFxuL9l3h_vs23NYohxlZhpKUYruaFEADp7B5GA&oe=69F7F14A",
            7.9812, 125.0451,
            "No glass containers. Keep surroundings clean. Children must be supervised.",
            "San Fernando"
        ),
        (
            "Dahilayan Adventure Park",
            "Home to Asia's longest dual zip line at over 4,000 feet elevation. Features pine "
            "forests, ATV trails, and extreme rides. A premier adventure destination in Bukidnon.",
            "Manolo Fortich, Bukidnon",
            "Resort",
            200, 1500,
            "https://www.projectlupad.com/wp-content/uploads/2019/05/World-Class-Dahilayan-Parks-in-Mindanao-Copyright-to-Project-LUPAD-3.jpg",
            8.3627, 124.8572,
            "Follow safety briefing. Minimum age 7 for zip line. Wear closed shoes.",
            "Manolo Fortich"
        ),
        (
            "Casisang River",
            "A calm, scenic river ideal for bamboo rafting and kayaking. Surrounded by rice "
            "paddies and traditional farming communities offering a genuine rural experience.",
            "Malaybalay, Bukidnon",
            "Nature",
            80, 350,
            "https://scontent.fcgy3-1.fna.fbcdn.net/v/t39.30808-6/518215667_807025952390444_3807283006988999782_n.jpg?stp=cp6_dst-jpg_tt6&_nc_cat=107&ccb=1-7&_nc_sid=7b2446&_nc_eui2=AeHoFPFE08rn8WTnEDV3-0FU2RVVBDZ1eADZFVUENnV4AGFxQugl3ijlKW0bD68GUr8U-bgzAIYU-lzstbJmiLBX&_nc_ohc=fCb2z7zC-q4Q7kNvwGRsCgc&_nc_oc=AdqyQaNK-jI7ZOwGt7e1Pkk5f79X5lszgtZiJjodOmcSPJB7fvBpJTi9KdYyd9unYb8&_nc_zt=23&_nc_ht=scontent.fcgy3-1.fna&_nc_gid=1IJg4hSA5Vs5iDD2aWhK4w&_nc_ss=7b2a8&oh=00_Af3J2KnJDs-ncb7FPz8C7W8CooluBz66TjIRY_Q_duUahQ&oe=69F7E9C4",
            8.1431, 125.1289,
            "Wear life vest. No swimming after heavy rain. Book raft in advance.",
            "Malaybalay"
        ),
        # Hiking Spots
        (
            "Mount Kitanglad Range",
            "A UNESCO Man and Biosphere Reserve and the 2nd highest peak in the Philippines at "
            "2,899 MASL. World-class bird-watching destination with over 300 bird species recorded.",
            "Lantapan, Bukidnon",
            "Hiking",
            150, 800,
            "https://www.aseanbiodiversity.org/wp-content/uploads/2024/03/324263114_880636666688774_6644373415470633023_n.jpg",
            8.1747, 124.8801,
            "Register at DENR office. Hire DENR-accredited guide. Bring enough water and food.",
            "Lantapan"
        ),
        (
            "Mount Capistrano",
            "A beginner-friendly hiking destination offering panoramic views of Cagayan de Oro "
            "and the Macajalar Bay. Popular sunrise trek with accessible trail system.",
            "Manolo Fortich, Bukidnon",
            "Hiking",
            50, 300,
            "https://dynamic-media-cdn.tripadvisor.com/media/photo-o/0a/bf/b1/0c/the-top-of-mt-capistrano.jpg?w=1200&h=-1&s=1",
            8.4200, 124.6500,
            "Start trek before 4 AM for sunrise. Bring headlamp and rain jacket.",
            "Manolo Fortich"
        ),
        (
            "Del Monte Pineapple Plantation",
            "The iconic sprawling pineapple fields managed by Del Monte Philippines. Offers "
            "guided tours, fresh pineapple tasting, and a peek into large-scale agro-industry.",
            "Manolo Fortich, Bukidnon",
            "Cultural",
            100, 400,
            "https://i0.wp.com/dotregion10.com/wp-content/uploads/2025/05/del_monte_plantation.jpg?resize=1024%2C683&ssl=1",
            8.3765, 124.8621,
            "Stay on designated paths. No picking fruit without permission.",
            "Manolo Fortich"
        ),
        (
            "Monastery of Transfiguration",
            "A Benedictine monastery perched on a hill offering sweeping valley views. Known "
            "for its unique architecture, peaceful gardens, and handcrafted souvenir products.",
            "Malaybalay, Bukidnon",
            "Cultural",
            0, 200,
            "https://www.philippinetraveler.com/wp-content/uploads/IMG_2404.jpg",
            8.1575, 125.1278,
            "Dress modestly (no shorts/sleeveless). Maintain silence in the chapel.",
            "Malaybalay"
        ),
    ]
    c.executemany("""
        INSERT INTO destinations
            (name,description,location,category,entrance_fee,estimated_cost,
             image_path,latitude,longitude,safety_tips,municipality,is_approved)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,1)
    """, destinations)

    # ── BUSINESSES ────────────────────────────────────────────────────────
    businesses = [
        # Cafes
        (3, "Kape Bukidnon",
         "A cozy hilltop café serving locally sourced Bukidnon coffee and native delicacies. "
         "Perfect spot to relax after a long day of exploring.",
         "Sayre Highway, Malaybalay City", "09171234567", "Cafe",
         "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=600",
         1, 1),
        (3, "Highlands Brew",
         "Specialty coffee shop nestled in the pine forest of Manolo Fortich. "
         "Known for its cold brew and panoramic mountain views.",
         "Dahilayan, Manolo Fortich", "09281234567", "Cafe",
         "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=600",
         0, 1),
        # Restaurants
        (3, "Bukidnon Native Kitchen",
         "Authentic Bukidnon cuisine featuring corn-fed beef, native chicken, "
         "and locally grown vegetables. Farm-to-table dining experience.",
         "Capitol Drive, Malaybalay City", "09351234567", "Restaurant",
         "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=600",
         1, 1),
        (3, "The Pineapple Table",
         "Restaurant themed around Bukidnon's pineapple heritage. "
         "Offers pineapple-infused dishes, fresh juices, and local specialties.",
         "National Highway, Manolo Fortich", "09461234567", "Restaurant",
         "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=600",
         0, 1),
        # Tourist Shops
        (3, "Bukid Finds Souvenir Shop",
         "Curated collection of Bukidnon handicrafts, woven products, native honey, "
         "pineapple jam, and locally made fashion items.",
         "Alanib, Lantapan, Bukidnon", "09571234567", "Tourist Shop",
         "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600",
         0, 1),
    ]
    c.executemany("""
        INSERT INTO businesses
            (user_id,business_name,description,address,contact_number,
             category,image_path,is_priority,is_verified)
        VALUES (?,?,?,?,?,?,?,?,?)
    """, businesses)

    # ── SAMPLE REVIEWS ────────────────────────────────────────────────────
    reviews = [
        (2, 1, 5, "Breathtaking falls! The trek was worth it.", "Juan dela Cruz"),
        (2, 2, 4, "Lovely spot, very peaceful.", "Juan dela Cruz"),
        (2, 3, 5, "Lake Apo is absolutely stunning!", "Juan dela Cruz"),
        (2, 5, 5, "Dahilayan is a must-visit. Best zip line ever!", "Juan dela Cruz"),
        (2, 7, 5, "Mount Kitanglad is a world-class hike. Incredible birds!", "Juan dela Cruz"),
    ]
    c.executemany("""
        INSERT INTO reviews (user_id,destination_id,rating,comment,reviewer_name)
        VALUES (?,?,?,?,?)
    """, reviews)

    conn.commit()


# -----------------------------------------------------------------------------
# USER FUNCTIONS
# -----------------------------------------------------------------------------

def insert_user(username, password, role, name="", email=""):
    """Register a new user. Returns (True, msg) or (False, error)."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO users (username,password,role,name,email) VALUES (?,?,?,?,?)",
            (username, _hash(password), role, name, email)
        )
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "Username already exists."
    finally:
        conn.close()


def fetch_user_by_login(username, password):
    """Return user row if credentials match, else None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, _hash(password))
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def fetch_user_by_id(user_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def fetch_all_users():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# -----------------------------------------------------------------------------
# DESTINATION FUNCTIONS
# -----------------------------------------------------------------------------

def fetch_all_destinations(approved_only=True):
    conn = get_connection()
    if approved_only:
        rows = conn.execute(
            "SELECT * FROM destinations WHERE is_approved=1 ORDER BY name"
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM destinations ORDER BY name"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_destination_by_id(dest_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM destinations WHERE id=?", (dest_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def search_destinations(query="", category="All", municipality="All"):
    """Search destinations with optional keyword, category, and municipality filters."""
    conn = get_connection()
    sql = "SELECT * FROM destinations WHERE is_approved=1"
    params = []
    if query:
        sql += " AND (name LIKE ? OR description LIKE ? OR location LIKE ?)"
        params += [f"%{query}%", f"%{query}%", f"%{query}%"]
    if category and category != "All":
        sql += " AND category=?"
        params.append(category)
    if municipality and municipality != "All":
        sql += " AND municipality=?"
        params.append(municipality)
    sql += " ORDER BY name"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def insert_destination(data: dict):
    """Insert a new destination record."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO destinations
            (name,description,location,category,entrance_fee,estimated_cost,
             image_path,latitude,longitude,safety_tips,municipality,is_approved)
        VALUES
            (:name,:description,:location,:category,:entrance_fee,:estimated_cost,
             :image_path,:latitude,:longitude,:safety_tips,:municipality,:is_approved)
    """, data)
    conn.commit()
    conn.close()


def update_destination(dest_id, data: dict):
    conn = get_connection()
    conn.execute("""
        UPDATE destinations SET
            name=:name, description=:description, location=:location,
            category=:category, entrance_fee=:entrance_fee,
            estimated_cost=:estimated_cost, safety_tips=:safety_tips,
            municipality=:municipality, is_approved=:is_approved
        WHERE id=:id
    """, {**data, "id": dest_id})
    conn.commit()
    conn.close()


def approve_destination(dest_id):
    conn = get_connection()
    conn.execute("UPDATE destinations SET is_approved=1 WHERE id=?", (dest_id,))
    conn.commit()
    conn.close()


def delete_destination(dest_id):
    conn = get_connection()
    conn.execute("DELETE FROM destinations WHERE id=?", (dest_id,))
    conn.commit()
    conn.close()


def fetch_nearby_destinations(lat, lng, radius_km=30):
    """Return destinations within radius_km of given coordinates."""
    all_dests = fetch_all_destinations()
    nearby = []
    for d in all_dests:
        if d["latitude"] and d["longitude"]:
            dlat = d["latitude"] - lat
            dlng = d["longitude"] - lng
            dist = ((dlat ** 2 + dlng ** 2) ** 0.5) * 111.0
            if dist <= radius_km:
                d["distance_km"] = round(dist, 1)
                nearby.append(d)
    return sorted(nearby, key=lambda x: x["distance_km"])


# -----------------------------------------------------------------------------
# BUSINESS FUNCTIONS
# -----------------------------------------------------------------------------

def insert_business(data: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO businesses
            (user_id,business_name,description,address,contact_number,
             category,image_path,is_priority)
        VALUES
            (:user_id,:business_name,:description,:address,:contact_number,
             :category,:image_path,:is_priority)
    """, data)
    conn.commit()
    conn.close()


def fetch_all_businesses(verified_only=False, user_id=None):
    conn = get_connection()
    sql = "SELECT * FROM businesses WHERE 1=1"
    params = []
    if verified_only:
        sql += " AND is_verified=1"
    if user_id:
        sql += " AND user_id=?"
        params.append(user_id)
    # Priority listings first
    sql += " ORDER BY is_priority DESC, business_name ASC"
    rows = conn.execute(sql, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_business_by_id(biz_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM businesses WHERE id=?", (biz_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_business(biz_id, data: dict):
    conn = get_connection()
    conn.execute("""
        UPDATE businesses SET
            business_name=:business_name, description=:description,
            address=:address, contact_number=:contact_number,
            category=:category, image_path=:image_path,
            is_priority=:is_priority
        WHERE id=:id
    """, {**data, "id": biz_id})
    conn.commit()
    conn.close()


def verify_business(biz_id):
    conn = get_connection()
    conn.execute("UPDATE businesses SET is_verified=1 WHERE id=?", (biz_id,))
    conn.commit()
    conn.close()


def delete_business(biz_id):
    conn = get_connection()
    conn.execute("DELETE FROM businesses WHERE id=?", (biz_id,))
    conn.commit()
    conn.close()


def increment_business_stat(biz_id, stat="views"):
    """Increment views, clicks, or inquiries counter."""
    allowed = {"views", "clicks", "inquiries"}
    if stat not in allowed:
        return
    conn = get_connection()
    conn.execute(f"UPDATE businesses SET {stat}={stat}+1 WHERE id=?", (biz_id,))
    conn.commit()
    conn.close()


# -----------------------------------------------------------------------------
# BOOKING FUNCTIONS
# -----------------------------------------------------------------------------

def insert_booking(data: dict):
    conn = get_connection()
    conn.execute("""
        INSERT INTO bookings
            (tourist_name,tourist_id,destination,destination_id,
             agency_name,tour_date,num_persons,contact,notes,status)
        VALUES
            (:tourist_name,:tourist_id,:destination,:destination_id,
             :agency_name,:tour_date,:num_persons,:contact,:notes,'Pending')
    """, data)
    conn.commit()
    conn.close()


def fetch_all_bookings(user_id=None):
    conn = get_connection()
    if user_id:
        rows = conn.execute(
            "SELECT * FROM bookings WHERE tourist_id=? ORDER BY created_at DESC",
            (user_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM bookings ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_booking_status(booking_id, status):
    """Update booking status: Pending | Accepted | Rejected."""
    conn = get_connection()
    conn.execute("UPDATE bookings SET status=? WHERE id=?", (status, booking_id))
    conn.commit()
    conn.close()


# -----------------------------------------------------------------------------
# REVIEW FUNCTIONS
# -----------------------------------------------------------------------------

def insert_review(user_id, dest_id, rating, comment, reviewer_name):
    conn = get_connection()
    conn.execute("""
        INSERT INTO reviews (user_id,destination_id,rating,comment,reviewer_name)
        VALUES (?,?,?,?,?)
    """, (user_id, dest_id, rating, comment, reviewer_name))
    conn.commit()
    conn.close()


def fetch_reviews(dest_id=None):
    conn = get_connection()
    if dest_id:
        rows = conn.execute(
            "SELECT * FROM reviews WHERE destination_id=? ORDER BY created_at DESC",
            (dest_id,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM reviews ORDER BY created_at DESC"
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_avg_rating(dest_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT ROUND(AVG(rating),1) as avg_r, COUNT(*) as cnt FROM reviews WHERE destination_id=?",
        (dest_id,)
    ).fetchone()
    conn.close()
    return {"avg": row["avg_r"] or 0.0, "cnt": row["cnt"]}


# -----------------------------------------------------------------------------
# CHAT FUNCTIONS
# -----------------------------------------------------------------------------

def insert_message(user_id, sender, message):
    conn = get_connection()
    conn.execute(
        "INSERT INTO chat_messages (user_id,sender,message) VALUES (?,?,?)",
        (user_id, sender, message)
    )
    conn.commit()
    conn.close()


def fetch_messages(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM chat_messages WHERE user_id=? ORDER BY created_at ASC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_all_chat_threads():
    conn = get_connection()
    rows = conn.execute("""
        SELECT cm.user_id, u.name, u.username,
               MAX(cm.created_at) AS last_msg,
               COUNT(CASE WHEN cm.sender='user' THEN 1 END) AS user_msgs
        FROM chat_messages cm
        JOIN users u ON cm.user_id = u.id
        GROUP BY cm.user_id
        ORDER BY last_msg DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# -----------------------------------------------------------------------------
# NOTIFICATION FUNCTIONS
# -----------------------------------------------------------------------------

def insert_notification(user_id, title, message):
    conn = get_connection()
    conn.execute(
        "INSERT INTO notifications (user_id,title,message) VALUES (?,?,?)",
        (user_id, title, message)
    )
    conn.commit()
    conn.close()


def fetch_notifications(user_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM notifications WHERE user_id=? ORDER BY created_at DESC LIMIT 30",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_all_read(user_id):
    conn = get_connection()
    conn.execute("UPDATE notifications SET is_read=1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()


def count_unread(user_id):
    conn = get_connection()
    row = conn.execute(
        "SELECT COUNT(*) FROM notifications WHERE user_id=? AND is_read=0",
        (user_id,)
    ).fetchone()
    conn.close()
    return row[0]


# -----------------------------------------------------------------------------
# ANALYTICS FUNCTIONS (Admin)
# -----------------------------------------------------------------------------

def fetch_platform_analytics():
    conn = get_connection()
    stats = {}
    stats["total_users"]        = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    stats["total_tourists"]     = conn.execute("SELECT COUNT(*) FROM users WHERE role='tourist'").fetchone()[0]
    stats["total_businesses_u"] = conn.execute("SELECT COUNT(*) FROM users WHERE role='business'").fetchone()[0]
    stats["total_destinations"] = conn.execute("SELECT COUNT(*) FROM destinations WHERE is_approved=1").fetchone()[0]
    stats["pending_dests"]      = conn.execute("SELECT COUNT(*) FROM destinations WHERE is_approved=0").fetchone()[0]
    stats["total_bookings"]     = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    stats["pending_bookings"]   = conn.execute("SELECT COUNT(*) FROM bookings WHERE status='Pending'").fetchone()[0]
    stats["total_businesses"]   = conn.execute("SELECT COUNT(*) FROM businesses WHERE is_verified=1").fetchone()[0]
    stats["pending_businesses"] = conn.execute("SELECT COUNT(*) FROM businesses WHERE is_verified=0").fetchone()[0]
    stats["total_reviews"]      = conn.execute("SELECT COUNT(*) FROM reviews").fetchone()[0]
    avg = conn.execute("SELECT ROUND(AVG(rating),1) FROM reviews").fetchone()[0]
    stats["avg_rating"]         = avg or 0.0

    # Bookings by status
    rows = conn.execute("""
        SELECT status, COUNT(*) as cnt FROM bookings GROUP BY status
    """).fetchall()
    stats["bookings_by_status"] = [dict(r) for r in rows]

    # Top destinations by bookings
    rows = conn.execute("""
        SELECT destination, COUNT(*) as cnt
        FROM bookings GROUP BY destination
        ORDER BY cnt DESC LIMIT 5
    """).fetchall()
    stats["top_destinations"] = [dict(r) for r in rows]

    # Destinations by category
    rows = conn.execute("""
        SELECT category, COUNT(*) as cnt FROM destinations
        WHERE is_approved=1 GROUP BY category
    """).fetchall()
    stats["dests_by_category"] = [dict(r) for r in rows]

    # Business views
    rows = conn.execute("""
        SELECT business_name, views, clicks, inquiries
        FROM businesses WHERE is_verified=1 ORDER BY views DESC LIMIT 5
    """).fetchall()
    stats["top_businesses"] = [dict(r) for r in rows]

    conn.close()
    return stats
