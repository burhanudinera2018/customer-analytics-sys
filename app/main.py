"""
Main Streamlit Application - FINAL VERSION
Integrates all three tasks into a unified interface
Dengan perbaikan untuk Kudos System, AI Assistant context, dan error handling
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os
from pathlib import Path
import logging
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Import modules dengan error handling
try:
    from app.modules.data_processor import DataProcessor
    from app.modules.kudos_system import KudosSystem
    from app.modules.order_bot import OrderBot
    from app.modules.ai_assistant import AIAssistant
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

# Page config
st.set_page_config(
    page_title="AI-Powered Customer Analytics",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan lebih baik
st.markdown("""
<style>
    .stButton button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #FF6B6B;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .success-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #D4EDDA;
        color: #155724;
        border-left: 4px solid #28A745;
    }
    .error-message {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #F8D7DA;
        color: #721C24;
        border-left: 4px solid #DC3545;
    }
    .kudos-card {
        padding: 1.2rem;
        border-radius: 0.8rem;
        background-color: #f8f9fa;
        margin: 0.8rem 0;
        border-left: 4px solid #FF4B4B;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .kudos-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.8rem;
        text-align: center;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 1rem;
        margin: 0.5rem 0;
        max-width: 80%;
    }
    .user-message {
        background-color: #007AFF;
        color: white;
        margin-left: auto;
    }
    .assistant-message {
        background-color: #E9ECEF;
        color: black;
        margin-right: auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state dengan error handling
def init_session_state():
    """Initialize all session state variables"""
    
    if 'processor' not in st.session_state:
        try:
            st.session_state.processor = DataProcessor("data")
            logger.info("✅ DataProcessor initialized")
        except Exception as e:
            st.error(f"Failed to initialize DataProcessor: {e}")
            st.session_state.processor = None
    
    if 'kudos' not in st.session_state:
        try:
            st.session_state.kudos = KudosSystem()
            logger.info("✅ KudosSystem initialized")
        except Exception as e:
            st.error(f"Failed to initialize KudosSystem: {e}")
            st.session_state.kudos = None
    
    if 'order_bot' not in st.session_state:
        try:
            st.session_state.order_bot = OrderBot()
            logger.info("✅ OrderBot initialized")
        except Exception as e:
            st.error(f"Failed to initialize OrderBot: {e}")
            st.session_state.order_bot = None
    
    if 'ai_assistant' not in st.session_state:
        try:
            st.session_state.ai_assistant = AIAssistant()
            logger.info("✅ AIAssistant initialized")
        except Exception as e:
            st.warning(f"AI Assistant initialization warning: {e}")
            st.session_state.ai_assistant = None

# Initialize
init_session_state()

# Sidebar navigation
with st.sidebar:
    st.title("🤖 AI Analytics Hub")
    st.divider()
    
    # Navigation with icons
    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "👥 Kudos System", "🤖 OrderBot", "🔍 Analytics", "💬 AI Assistant"],
        key="navigation",
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # System Status
    st.markdown("### 📊 System Status")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.kudos:
            try:
                users_count = len(st.session_state.kudos.get_users_list())
                st.metric("Users", users_count, delta=None)
            except:
                st.metric("Users", "❌")
        else:
            st.metric("Users", "❌")
    
    with col2:
        if st.session_state.processor:
            try:
                # Quick check if data loaded
                metrics = st.session_state.processor.calculate_metrics()
                if metrics.get('total_customers', 0) > 0:
                    st.metric("Data", "✅")
                else:
                    st.metric("Data", "⚠️")
            except:
                st.metric("Data", "❌")
        else:
            st.metric("Data", "❌")
    
    st.divider()
    
    # Portfolio Project
    st.markdown("""
    ### 📁 Portfolio Project
    - ✅ Task 1: Debugging & Refactoring
    - ✅ Task 2: Kudos System (Spec-Driven)
    - ✅ Task 3: OrderBot (Agentic AI)
    """)
    
    st.divider()
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    with col2:
        if st.button("🧹 Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Cache cleared!")
            st.rerun()
    
    # Debug section
    with st.expander("🔧 Debug Info"):
        st.write(f"🐍 Python: {sys.version.split()[0]}")
        st.write(f"📁 Path: {Path(__file__).parent.name}")
        if st.session_state.processor:
            st.write(f"👥 Customers: {len(st.session_state.processor.customers)}")
        if st.session_state.kudos:
            try:
                st.write(f"🎉 Kudos DB: Connected")
            except:
                st.write(f"🎉 Kudos DB: Error")

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def format_currency(value):
    """Format currency with $ sign"""
    return f"${value:,.2f}"

def get_data_context():
    """Get formatted data context for AI Assistant"""
    if not st.session_state.processor:
        return {}
    
    try:
        metrics = st.session_state.processor.calculate_metrics()
        
        # Get top customers in readable format
        top_customers = []
        for cust in metrics.get('top_customers', [])[:5]:
            if isinstance(cust, dict):
                top_customers.append({
                    'name': cust.get('name', 'Unknown'),
                    'total_spent': cust.get('total_spent', 0)
                })
        
        return {
            "total_customers": metrics.get('total_customers', 0),
            "total_transactions": metrics.get('total_transactions', 0),
            "total_revenue": metrics.get('total_revenue', 0),
            "average_transaction_value": metrics.get('average_transaction_value', 0),
            "category_breakdown": metrics.get('category_breakdown', {}),
            "top_customers": top_customers
        }
    except Exception as e:
        logger.error(f"Error getting data context: {e}")
        return {}

# ============================================================================
# DASHBOARD PAGE
# ============================================================================
if page == "📊 Dashboard":
    st.title("📊 Customer Analytics Dashboard")
    
    if not st.session_state.processor:
        st.error("❌ DataProcessor not initialized. Please check logs.")
        st.stop()
    
    # Load data dengan caching
    @st.cache_data(ttl=60)
    def load_dashboard_data():
        processor = st.session_state.processor
        try:
            processor.load_data("customers.csv")
            processor.process_transactions("transactions.csv")
            return processor.calculate_metrics()
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return None
    
    try:
        with st.spinner("🔄 Loading dashboard data..."):
            metrics = load_dashboard_data()
        
        if not metrics:
            st.warning("⚠️ No data found. Please ensure customers.csv and transactions.csv exist in the data folder.")
            
            # Show file structure help
            with st.expander("📁 Required File Structure"):
                st.code("""
data/
├── customers.csv
└── transactions.csv
                """)
                
            # Sample data button
            if st.button("📝 Create Sample Data"):
                # Create sample data files
                data_dir = Path("data")
                data_dir.mkdir(exist_ok=True)
                
                # Customers CSV
                customers_data = """customer_id,name,email,join_date
C001,John Smith,john.smith@email.com,2023-01-15
C002,Jane Doe,jane.doe@email.com,2023-02-20
C003,Bob Johnson,bob.johnson@email.com,2023-03-10
C004,Alice Brown,alice.brown@email.com,2023-04-05
C005,Charlie Wilson,charlie.wilson@email.com,2023-05-12"""
                
                # Transactions CSV
                transactions_data = """transaction_id,customer_id,amount,date,category
T001,C001,150.50,2024-01-10,electronics
T002,C002,75.25,2024-01-11,clothing
T003,C001,200.00,2024-01-12,electronics
T004,C003,45.75,2024-01-13,food
T005,C002,120.00,2024-01-14,clothing
T006,C004,89.99,2024-01-15,books
T007,C005,300.00,2024-01-16,electronics
T008,C001,25.50,2024-01-17,food
T009,C003,180.00,2024-01-18,clothing
T010,C002,95.25,2024-01-19,books"""
                
                with open(data_dir / "customers.csv", "w") as f:
                    f.write(customers_data)
                with open(data_dir / "transactions.csv", "w") as f:
                    f.write(transactions_data)
                
                st.success("✅ Sample data created! Refreshing...")
                st.cache_data.clear()
                st.rerun()
            
            st.stop()
        
        # Key metrics in nice cards
        st.markdown("### 📈 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Customers",
                metrics.get('total_customers', 0),
                help="Number of unique customers"
            )
        
        with col2:
            st.metric(
                "Total Transactions",
                metrics.get('total_transactions', 0),
                help="Total number of transactions"
            )
        
        with col3:
            st.metric(
                "Total Revenue",
                format_currency(metrics.get('total_revenue', 0)),
                help="Total revenue from all transactions"
            )
        
        with col4:
            st.metric(
                "Avg Transaction",
                format_currency(metrics.get('average_transaction_value', 0)),
                help="Average transaction value"
            )
        
        st.divider()
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Category Breakdown")
            category_data = metrics.get('category_breakdown', {})
            if category_data:
                category_df = pd.DataFrame(
                    list(category_data.items()),
                    columns=['Category', 'Count']
                )
                fig = px.pie(
                    category_df,
                    values='Count',
                    names='Category',
                    title="Transactions by Category",
                    hole=0.3,
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No category data available")
        
        with col2:
            st.markdown("### 🏆 Top Customers")
            top_customers = metrics.get('top_customers', [])
            if top_customers:
                # Convert to DataFrame for display
                df_data = []
                for cust in top_customers[:5]:
                    if isinstance(cust, dict):
                        df_data.append({
                            'Name': cust.get('name', 'Unknown'),
                            'Total Spent': format_currency(cust.get('total_spent', 0)),
                            'Transactions': cust.get('transaction_count', 0)
                        })
                
                df = pd.DataFrame(df_data)
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Name": "Customer Name",
                        "Total Spent": "Total Spent",
                        "Transactions": "Transactions"
                    }
                )
                
                # Bar chart for top customers
                fig = px.bar(
                    df_data,
                    x='Name',
                    y=[float(c['Total Spent'].replace('$', '').replace(',', '')) for c in df_data],
                    title="Top Customers by Revenue",
                    labels={'y': 'Total Spent', 'Name': 'Customer'},
                    color_discrete_sequence=['#FF4B4B']
                )
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No top customers data available")
        
        # Data Summary
        with st.expander("📋 Data Summary"):
            st.json(metrics)
            
    except Exception as e:
        st.error(f"❌ Error loading dashboard: {str(e)}")
        logger.error(f"Dashboard error: {e}", exc_info=True)

# ============================================================================
# KUDOS SYSTEM PAGE
# ============================================================================
elif page == "👥 Kudos System":
    st.title("👥 Employee Kudos System")
    
    if not st.session_state.kudos:
        st.error("⚠️ Kudos System not initialized")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reconnect Database", use_container_width=True):
                try:
                    st.session_state.kudos = KudosSystem()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
        with col2:
            st.code("python fix_kudos_db_final.py")
        st.stop()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["💝 Send Kudos", "📰 Public Feed", "👑 Admin Panel"])
    
    # ===== TAB 1: SEND KUDOS =====
    with tab1:
        st.markdown("### 💝 Send Appreciation")
        
        # Get users list dengan caching
        @st.cache_data(ttl=10)
        def get_users():
            return st.session_state.kudos.get_users_list()
        
        users = get_users()
        
        if not users:
            st.warning("⚠️ No users found in database.")
            st.info("Please run the database seed script:")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 Refresh Users", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()
            with col2:
                if st.button("🔧 Run Seed Script", use_container_width=True):
                    with st.spinner("Running seed script..."):
                        try:
                            result = subprocess.run(
                                ["python", "seed_database.py"],
                                capture_output=True,
                                text=True
                            )
                            if result.returncode == 0:
                                st.success("✅ Database seeded successfully!")
                                st.cache_data.clear()
                                st.rerun()
                            else:
                                st.error(f"Error: {result.stderr}")
                        except Exception as e:
                            st.error(f"Error: {e}")
        else:
            # Create user options dictionary
            user_options = {u['id']: f"{u['full_name']} ({u['department']})" for u in users}
            
            # Form pengiriman kudos
            with st.form(key="send_kudos_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    sender = st.selectbox(
                        "👤 From (Your Name)",
                        options=list(user_options.keys()),
                        format_func=lambda x: user_options[x],
                        key="sender"
                    )
                
                with col2:
                    default_idx = 1 if len(users) > 1 else 0
                    receiver = st.selectbox(
                        "👥 To",
                        options=list(user_options.keys()),
                        format_func=lambda x: user_options[x],
                        index=default_idx,
                        key="receiver"
                    )
                
                # Message input dengan character counter
                message = st.text_area(
                    "📝 Message",
                    max_chars=500,
                    height=120,
                    placeholder="Write your appreciation message here...",
                    help="Maximum 500 characters"
                )
                
                # Character counter with progress
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.progress(len(message)/500, text=f"{len(message)}/500 characters")
                with col2:
                    st.caption(f"**{500 - len(message)}** left")
                
                # Submit button
                submitted = st.form_submit_button(
                    "💝 Send Kudos",
                    type="primary",
                    use_container_width=True
                )
                
                if submitted:
                    if not message.strip():
                        st.error("❌ Message cannot be empty")
                    elif sender == receiver:
                        st.error("❌ Cannot send kudos to yourself")
                    else:
                        try:
                            with st.spinner("Sending kudos..."):
                                result = st.session_state.kudos.send_kudos(
                                    sender,
                                    receiver,
                                    message
                                )
                                if result:
                                    st.success("✅ Kudos sent successfully! 🎉")
                                    st.balloons()
                                    st.cache_data.clear()
                                    st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error sending kudos: {e}")
    
    # ===== TAB 2: PUBLIC FEED =====
    with tab2:
        st.markdown("### 📰 Public Kudos Feed")
        
        @st.cache_data(ttl=5)
        def get_feed():
            return st.session_state.kudos.get_public_feed(limit=50)
        
        feed = get_feed()
        
        if not feed:
            st.info("💝 No kudos yet. Be the first to send some appreciation!")
            
            # Quick action
            if st.button("📝 Send Your First Kudos", use_container_width=True):
                st.session_state.navigation = "👥 Kudos System"
                st.rerun()
        else:
            st.caption(f"📊 Showing {len(feed)} recent kudos")
            
            for k in feed:
                with st.container():
                    try:
                        created_at = datetime.fromisoformat(k['created_at']).strftime("%B %d, %Y at %H:%M")
                    except:
                        created_at = k.get('created_at', 'Unknown date')
                    
                    st.markdown(f"""
                    <div class="kudos-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <span style="font-weight: bold; color: #FF4B4B; font-size: 1.1rem;">{k['sender']}</span>
                            <span style="color: #6c757d;">→</span>
                            <span style="font-weight: bold; color: #FF4B4B; font-size: 1.1rem;">{k['receiver']}</span>
                        </div>
                        <div style="margin: 15px 0; font-style: italic; font-size: 1rem; line-height: 1.5;">
                            "{k['message']}"
                        </div>
                        <div style="text-align: right; color: #6c757d; font-size: 0.85rem;">
                            <span>🕒 {created_at}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Refresh button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Refresh Feed", use_container_width=True):
                    st.cache_data.clear()
                    st.rerun()
    
    # ===== TAB 3: ADMIN PANEL =====
    with tab3:
        st.markdown("### 👑 Admin Moderation Panel")
        
        # Get all users for admin selection
        users = get_users()
        
        if users:
            # Filter admin users
            admin_users = [u for u in users if u.get('is_admin', False)]
            
            if not admin_users:
                st.warning("⚠️ No admin users found. Please make a user admin first.")
                
                # Show option to make user admin
                with st.expander("🔧 Make a user admin"):
                    for u in users:
                        col1, col2, col3 = st.columns([3, 1, 1])
                        with col1:
                            st.write(f"{u['full_name']} (ID: {u['id']})")
                        with col2:
                            st.write("👑" if u.get('is_admin') else "👤")
                        with col3:
                            if not u.get('is_admin'):
                                if st.button(f"Make Admin", key=f"make_admin_{u['id']}"):
                                    try:
                                        # Update user to admin
                                        from sqlalchemy import create_engine, text
                                        import os
                                        db_url = os.getenv('DATABASE_URL', 'postgresql://kudos_user:kudos_password@localhost:5432/kudos_db')
                                        engine = create_engine(db_url)
                                        with engine.connect() as conn:
                                            conn.execute(text(f"UPDATE users SET is_admin = TRUE WHERE id = {u['id']}"))
                                            conn.commit()
                                        st.success(f"✅ {u['full_name']} is now admin!")
                                        st.cache_data.clear()
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {e}")
            
            # Admin selection
            admin_id = st.number_input(
                "👑 Admin ID",
                min_value=1,
                value=admin_users[0]['id'] if admin_users else 1,
                help="Enter your admin user ID"
            )
            
            # Get feed for moderation
            feed = get_feed()
            
            if not feed:
                st.info("No kudos to moderate")
            else:
                st.caption(f"📊 {len(feed)} kudos awaiting moderation")
                
                for k in feed:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            st.markdown(f"""
                            **{k['sender']}** → **{k['receiver']}**
                            *{k['message'][:70]}...*
                            """)
                        
                        with col2:
                            if st.button(f"👁️ Hide", key=f"hide_{k['id']}"):
                                try:
                                    st.session_state.kudos.moderate_kudos(
                                        k['id'],
                                        admin_id,
                                        'hide',
                                        'Hidden by admin'
                                    )
                                    st.success("✅ Hidden")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        
                        with col3:
                            if st.button(f"🗑️ Delete", key=f"del_{k['id']}"):
                                try:
                                    st.session_state.kudos.moderate_kudos(
                                        k['id'],
                                        admin_id,
                                        'delete'
                                    )
                                    st.success("✅ Deleted")
                                    st.cache_data.clear()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        
                        with col4:
                            st.caption(f"ID: {k['id']}")
                        
                        st.divider()
        else:
            st.warning("No users found in database")

# ============================================================================
# ORDERBOT PAGE
# ============================================================================
elif page == "🤖 OrderBot":
    st.title("🤖 OrderBot - Autonomous Order Processing")
    
    if not st.session_state.order_bot:
        st.error("❌ OrderBot not initialized")
        if st.button("🔄 Reinitialize OrderBot", use_container_width=True):
            try:
                st.session_state.order_bot = OrderBot()
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
        st.stop()
    
    # Agent Goal
    st.info("""
    **🎯 Agent Goal:** Autonomously process all new hardware orders from email receipt 
    to fulfillment confirmation within 5 minutes, with target accuracy of 99.5%
    """)
    
    # Agent Anatomy
    with st.expander("🔧 Agent Anatomy", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **👁️ Perception Tools:**
            - 📧 Email Reader API
            - 📄 PDF Parser
            - ☁️ Salesforce API
            - 📊 Google Sheets API
            """)
        
        with col2:
            st.markdown("""
            **🖐️ Action Tools:**
            - ✉️ Email Sender
            - 📝 Salesforce Updater
            - 📦 Inventory Manager
            - 💾 Memory/Learning
            """)
    
    # Performance Metrics
    st.markdown("### 📊 Performance Metrics")
    
    try:
        metrics = st.session_state.order_bot.get_performance_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                "Orders Processed",
                metrics.get('orders_processed', 0),
                help="Total orders processed"
            )
        with col2:
            success_rate = metrics.get('accuracy', 0)
            st.metric(
                "Success Rate",
                f"{success_rate:.1f}%",
                delta=f"{success_rate - 99.5:.1f}%" if success_rate else None,
                help="Success rate (target: 99.5%)"
            )
        with col3:
            goal = metrics.get('goal_achieved', False)
            st.metric(
                "Goal Achieved",
                "✅ Yes" if goal else "❌ No",
                help="Target: 99.5% accuracy"
            )
        with col4:
            st.metric(
                "Memory Size",
                metrics.get('learning_memory_size', 0),
                help="Learning memory entries"
            )
        
        # Failure patterns
        if metrics.get('failure_patterns'):
            with st.expander("📈 Failure Patterns"):
                st.json(metrics['failure_patterns'])
    
    except Exception as e:
        st.warning(f"Could not load metrics: {e}")
    
    st.divider()
    
    # Run OrderBot
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("🚀 Run OrderBot", type="primary", use_container_width=True):
            with st.spinner("🤖 OrderBot is processing orders..."):
                try:
                    results = st.session_state.order_bot.process_new_orders()
                    
                    if results.get('processed'):
                        st.success(f"✅ Successfully processed {len(results['processed'])} orders")
                        
                        with st.expander("✅ Successful Orders", expanded=True):
                            for order in results['processed']:
                                st.markdown(f"""
                                - **Order {order.get('order_id', 'Unknown')}**: 
                                  {order.get('customer', 'Unknown')} - 
                                  {order.get('quantity', 0)}x {order.get('product', 'Unknown')}
                                """)
                    
                    if results.get('failed'):
                        st.error(f"❌ Failed to process {len(results['failed'])} orders")
                        
                        with st.expander("❌ Failed Orders", expanded=True):
                            for order in results['failed']:
                                st.error(f"""
                                **Order {order.get('order_id', 'Unknown')}**: 
                                {order.get('error', 'Unknown error')}
                                """)
                                if order.get('details'):
                                    st.caption(order['details'])
                    
                    st.info(f"📊 Total: {results.get('total_found', 0)} orders processed")
                    
                except Exception as e:
                    st.error(f"Error running OrderBot: {e}")
    
    with col2:
        if st.button("🔄 Reset Metrics", use_container_width=True):
            try:
                st.session_state.order_bot = OrderBot()
                st.success("✅ Metrics reset")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ============================================================================
# ANALYTICS PAGE
# ============================================================================
elif page == "🔍 Analytics":
    st.title("🔍 Customer Search & Analytics")
    
    if not st.session_state.processor:
        st.error("❌ DataProcessor not initialized")
        st.stop()
    
    # Search section
    st.markdown("### 🔍 Search Customers")
    
    search_term = st.text_input(
        "Search customers by name",
        placeholder="Enter customer name...",
        help="Search will match partial names"
    )
    
    if search_term:
        with st.spinner("Searching..."):
            try:
                matches = st.session_state.processor.find_matches(search_term)
                
                if matches:
                    st.success(f"✅ Found {len(matches)} matching customers")
                    
                    # Convert to DataFrame
                    df = pd.DataFrame(matches)
                    
                    # Format currency
                    if 'total_spent' in df.columns:
                        df['total_spent'] = df['total_spent'].apply(lambda x: f"${x:,.2f}")
                    
                    # Display results
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "customer_id": "Customer ID",
                            "name": "Name",
                            "email": "Email",
                            "total_spent": "Total Spent",
                            "transaction_count": "Transactions"
                        }
                    )
                    
                    # Download button
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Results as CSV",
                        data=csv,
                        file_name=f"search_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info(f"No customers found matching '{search_term}'")
            except Exception as e:
                st.error(f"Search error: {e}")
    
    st.divider()
    
    # Quick Statistics
    st.markdown("### 📊 Quick Statistics")
    
    try:
        metrics = st.session_state.processor.calculate_metrics()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Total Customers", metrics.get('total_customers', 0))
            st.metric("Total Transactions", metrics.get('total_transactions', 0))
        
        with col2:
            st.metric("Total Revenue", format_currency(metrics.get('total_revenue', 0)))
            st.metric("Avg Transaction", format_currency(metrics.get('average_transaction_value', 0)))
        
        with st.expander("📋 Detailed Statistics"):
            st.json(metrics)
            
    except Exception as e:
        st.error(f"Error loading statistics: {e}")

# ============================================================================
# AI ASSISTANT PAGE - FIXED VERSION WITH PROPER CONTEXT
# ============================================================================
elif page == "💬 AI Assistant":
    st.title("💬 AI Assistant (Ollama Integration)")
    
    # Check AI Assistant
    if not st.session_state.ai_assistant:
        st.warning("⚠️ AI Assistant not fully initialized")
        if st.button("🔄 Initialize AI Assistant", use_container_width=True):
            try:
                st.session_state.ai_assistant = AIAssistant()
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your AI assistant. Ask me anything about your customer data!\n\n"
                          "**Try asking:**\n"
                          "• How many customers do we have?\n"
                          "• What's the total revenue?\n"
                          "• Show me category breakdown\n"
                          "• Who are our top customers?"
            }
        ]
    
    # Get current data context
    context = get_data_context()
    
    # Display data context in sidebar
    with st.sidebar:
        st.divider()
        st.markdown("### 📊 Current Data")
        if context:
            st.metric("Customers", context.get('total_customers', 0))
            st.metric("Revenue", format_currency(context.get('total_revenue', 0)))
            st.metric("Transactions", context.get('total_transactions', 0))
            
            with st.expander("📋 View Full Context"):
                st.json(context)
        else:
            st.warning("No data loaded")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me about your data..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analyzing your data..."):
                try:
                    # Get response with context
                    if st.session_state.ai_assistant:
                        response = st.session_state.ai_assistant.ask(prompt, context=context)
                    else:
                        # Fallback responses based on context
                        if context:
                            response = generate_fallback_response(prompt, context)
                        else:
                            response = "⚠️ AI Assistant is not available and no data context found."
                    
                    st.markdown(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    
                except Exception as e:
                    error_msg = f"❌ Error getting response: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Clear chat button