# 🏔️ BukidKnown – Bukidnon Tourism Web Platform

A centralized tourism platform for Bukidnon Province, Philippines.
Built with **Python + Streamlit + SQLite** as a student full-stack project.

---

## 🗂️ Project Structure

```
bukidknown/
├── main.py                        # App entry point + sidebar router
├── requirements.txt
├── .streamlit/
│   └── config.toml                # Theme & server config
│
├── database/
│   ├── __init__.py
│   └── db.py                      # All DB connection, schema, CRUD functions
│
├── assets/
│   └── style.css                  # Global CSS (fonts, cards, hero, etc.)
│
└── pages/
    ├── __init__.py
    ├── home.py                    # Home: hero, stats, category filters, featured
    ├── spots.py                   # All tourist spots listing
    ├── spot_detail.py             # Individual spot: about, map, reviews, booking
    ├── search.py                  # Search with keyword + category + municipality
    ├── nearby.py                  # 📍 Nearby spots with distance calculation
    ├── estimator.py               # 💰 Expense Estimator (spec formula)
    ├── businesses.py              # Nearby businesses (priority listing first)
    ├── booking.py                 # Book a tour + My bookings
    ├── reviews.py                 # ⭐ Reviews & ratings
    ├── chat.py                    # 💬 Chat support (tourist + admin inbox)
    ├── biz_dashboard.py           # 🏪 Business owner dashboard + analytics
    ├── admin.py                   # 🛠️ Admin panel (approve, verify, manage)
    ├── analytics.py               # 📊 Admin analytics dashboard
    ├── auth.py                    # Login & registration
    └── notifications.py           # 🔔 User notifications
```

---

## 🚀 Setup & Run

### 1. Extract and navigate
```bash
unzip bukidknown.zip
cd bukidknown
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the application
```bash
streamlit run main.py
```

Open **http://localhost:8501** in your browser.

---

## 👤 Demo Accounts

| Role           | Username    | Password     |
|----------------|-------------|--------------|
| 🛠️ Admin       | admin       | admin123     |
| 👤 Tourist     | tourist1    | tourist123   |
| 🏪 Business    | business1   | business123  |

---

## ✅ Features Checklist

### Tourist Features
- [x] Search destinations (keyword + category + municipality)
- [x] View destination details (description, location, fee, safety tips, images)
- [x] Expense Estimator (formula: Entrance Fee × Persons + Transport + Food)
- [x] View Nearby Businesses (priority listing first)
- [x] Book Tour Services (status: Pending → Accepted / Rejected)
- [x] Reviews & Ratings
- [x] Nearby Spots (distance-based)
- [x] Chat Support
- [x] Notifications

### Business Owner Features
- [x] Register Business (name, description, address, contact, category, photo, promotion)
- [x] Manage Listings (view status, analytics)
- [x] Priority Listing (appears at top)
- [x] View Analytics (views, clicks, inquiries)
- [x] Submit new tourist spots

### Admin Features
- [x] Approve destination listings
- [x] Manage destination data (approve / delete)
- [x] Verify businesses
- [x] Monitor platform activity
- [x] Manage bookings (accept / reject)
- [x] User management
- [x] Send notifications (individual or broadcast)
- [x] Analytics dashboard

### Additional Features
- [x] ⭐ Reviews & Ratings
- [x] 📍 Nearby Spots
- [x] 💬 Chat Support
- [x] 📊 Admin Analytics
- [x] 🔔 Notifications

---

## 💰 Expense Estimation Formula

```
Total Cost = (Entrance Fee × Number of Persons)
           + Transportation Cost
           + Food Budget
           + Other Expenses

Transportation:
  Motorcycle  = ₱200
  Bus         = ₱500
  Van         = ₱1,000
```

---

## 📋 Database Tables

| Table           | Purpose                         |
|-----------------|---------------------------------|
| users           | All user accounts + roles       |
| destinations    | Tourist spots                   |
| businesses      | Business listings               |
| bookings        | Tour booking requests           |
| reviews         | Star ratings and comments       |
| chat_messages   | Chat support messages           |
| notifications   | User notifications              |

---

## 🌐 Deploy to Streamlit Cloud

1. Push project to GitHub
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo, set **main.py** as the entry point
4. Click Deploy — your app is live!

---

## 🛠️ Tech Stack

| Layer      | Technology              |
|------------|-------------------------|
| Frontend   | Streamlit + Custom CSS  |
| Backend    | Python 3.10+            |
| Database   | SQLite                  |
| Maps       | streamlit-folium + Folium |
| Fonts      | Google Fonts (Playfair Display + DM Sans) |
| Deployment | Streamlit Cloud         |

---

## 🔐 Security

- Passwords are hashed using **SHA-256** before storage
- Role-based access control on all protected pages
- Session state managed via `st.session_state`
- Admin approval required for all spots and businesses before going public
