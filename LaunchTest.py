from appium import webdriver
from appium.options.android import UiAutomator2Options  # Import correct options class

# Create an instance of UiAutomator2Options
options = UiAutomator2Options()
options.platform_name = "Android"
options.platform_version = "14"  # Your Android version
options.device_name = "Akkim-Galaxy S22 Ultra"  # Your device name
options.app_package = "com.mayhem.ugwob"  # Your app package
options.app_activity = "com.epicgames.ue4.GameActivity"  # Your app activity
options.no_reset = True  # Keep the app state after execution

# Start Appium session with options instead of a dictionary
driver = webdriver.Remote("http://127.0.0.1:4723", options=options)


# Perform a simple action (print screen title)
print("App Launched Successfully!")

# Quit the session
driver.quit()
