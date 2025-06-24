import logging

import streamlit as st

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Main Streamlit application entry point."""
    st.set_page_config(
        page_title="MusicTool",
        page_icon="🎵",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🎵 MusicTool MVP")
    st.write("Welcome to your music collection manager!")

    st.info("This is the initial setup. The application is ready for development.")

    # Display basic system info
    st.subheader("System Status")
    col1, col2 = st.columns(2)

    with col1:
        st.metric("Database", "Not connected", delta="Setup required")

    with col2:
        st.metric("Data Sources", "0", delta="None configured")

    logger.info("MusicTool application started")


if __name__ == "__main__":
    main()
