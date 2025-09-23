import pandas as pd
from superset.app import create_app
from superset import db, security_manager
from superset.initialization import SupersetAppInitializer

# CONFIG
EXCEL_FILE = "superset_users_roles.xlsx"
SHEET_NAME = 0

# Create and initialize Superset app
app = create_app()
try:
    SupersetAppInitializer(app).init_app()
except Exception as e:
    print(f"ℹ️ Superset app already initialized — skipping init_app()\n{e}")

df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

with app.app_context():
    for _, row in df.iterrows():
        username = str(row['username']).strip()
        email = str(row['email']).strip()
        first_name = str(row.get('first_name', '')).strip()
        last_name = str(row.get('last_name', '')).strip()
        password = str(row.get('password', '')).strip()
        role_name = str(row.get('role_name', '')).strip()

        # --- CREATE OR GET ROLE ---
        role = None
        if role_name:
            role = security_manager.find_role(role_name)
            if not role:
                print(f"🆕 Creating new role: {role_name}")
                role = security_manager.add_role(role_name)

            # Optional: Assign permissions if listed
            permissions = row.get('permissions')
            if pd.notna(permissions):
                for perm in str(permissions).split(","):
                    perm = perm.strip()
                    if not perm:
                        continue
                    pv = security_manager.find_permission_view_menu(perm, "all_datasource_access")
                    if pv:
                        print(f"  ➕ Adding permission '{perm}' to role '{role_name}'")
                        security_manager.add_permission_role(role, pv)

        # --- CREATE USER ---
        user = security_manager.find_user(username=username)
        if not user:
            print(f"👤 Creating user: {username}")
            user = security_manager.add_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                role=[role] if role else [],
                password=password,
            )
        else:
            print(f"✅ User already exists: {username}")
