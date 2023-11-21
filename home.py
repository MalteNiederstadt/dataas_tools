import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Audience & Technology Data Apps",
    page_icon="📊",  # You can use an appropriate icon
    layout="centered",  # Centered layout
)

# App title and description


# Add icons and colors for emphasis
st.markdown("<div style='text-align:center'><h1 style='color: #ff9900;'>📰</h1></div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center'><h3 style='color: #ff9900;'>A/B Tests and more</h3></div>", unsafe_allow_html=True)

# Instructions
st.header("Getting Started")
st.write("1. Use the navigation sidebar on the left to select different analysis sections.")
st.write("2. Upload your data or connect to your data source.")
st.write("3. Start exploring and visualizing your online media data.")
st.write("4. Adjust parameters and settings as needed.")

# Footer with contact information or additional details
st.sidebar.markdown("---")
st.sidebar.write("For assistance and support, contact:")
st.sidebar.write("Data Team")
#st.sidebar.write("your@email.com")

# # Sidebar with additional information or navigation links
# st.sidebar.markdown("---")
# st.sidebar.header("Navigation")
# # You can add links to different sections of your app here
# # Example: st.sidebar.markdown("[Dashboard](#dashboard)")

# # Add more content and sections as needed

