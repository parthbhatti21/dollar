#!/usr/bin/env python3
"""
Login App - Opens daily login URLs in Chrome
Run this script to open all your daily login pages automatically.
"""

import subprocess
import sys
import time
import platform
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# URLs to open
LOGIN_URLS = [
    "https://docs.google.com/spreadsheets/d/1eT_P6eSbSZVsMpTn0Za_kOQoZkXcmOceAjYTmw5ZxL0/edit?gid=481897317#gid=481897317",
    "https://onedrive.live.com/view.aspx?resid=13A06F3921820A08!317&ithint=file%2Cxlsx&authkey=!ADs-ECufEQ0Fxe8",
    "https://app.gohighlevel.com/v2/location/VYalbi1wvMvrFSt4X5Aa/ai-agents/voice-ai",
    "https://reportify.chimneysweeps.com/",
    "https://booking.chimneysweep.com/"
]

def open_urls_in_chrome(urls):
    """
    Open multiple URLs in Chrome browser.
    
    Args:
        urls: List of URLs to open
        
    Returns:
        bool: True if all URLs opened successfully, False otherwise
    """
    system = platform.system().lower()
    success_count = 0
    
    logger.info(f"Opening {len(urls)} URLs in Chrome...")
    
    for i, url in enumerate(urls, 1):
        try:
            if system == "darwin":  # macOS
                result = subprocess.run(
                    ['open', '-a', 'Google Chrome', url],
                    capture_output=True,
                    timeout=5
                )
            elif system == "windows":
                result = subprocess.run(
                    f'start chrome "{url}"',
                    shell=True,
                    capture_output=True,
                    timeout=5
                )
            elif system == "linux":
                # Try google-chrome first, then chromium
                result = subprocess.run(
                    ['google-chrome', url],
                    capture_output=True,
                    timeout=5
                )
                if result.returncode != 0:
                    result = subprocess.run(
                        ['chromium', url],
                        capture_output=True,
                        timeout=5
                    )
            else:
                logger.error(f"Unsupported platform: {system}")
                return False
            
            if result.returncode == 0:
                success_count += 1
                logger.info(f"✅ Opened URL {i}/{len(urls)}")
            else:
                logger.warning(f"⚠️  Failed to open URL {i}: {url}")
            
            # Small delay between opening tabs
            if i < len(urls):
                time.sleep(0.3)
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏱️  Timeout opening URL {i}: {url}")
        except Exception as e:
            logger.error(f"❌ Error opening URL {i}: {e}")
    
    if success_count == len(urls):
        logger.info(f"🎉 Successfully opened all {len(urls)} URLs!")
        return True
    elif success_count > 0:
        logger.warning(f"⚠️  Opened {success_count}/{len(urls)} URLs")
        return True
    else:
        logger.error("❌ Failed to open any URLs")
        return False

def main():
    """Main function to run the login app."""
    print("=" * 60)
    print("🚀 Login App - Opening Daily Login Pages")
    print("=" * 60)
    print()
    
    success = open_urls_in_chrome(LOGIN_URLS)
    
    print()
    if success:
        print("✅ Login pages opened successfully!")
        print("📋 Check your Chrome browser for the opened tabs.")
    else:
        print("❌ Some URLs failed to open. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main()


