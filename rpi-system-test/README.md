# Raspberry Pi 5 System Test

This project is designed to test various functionalities of the Raspberry Pi 5 system. It gathers system information, lists available cameras and their properties, takes pictures, tests Hailo-8 hardware, and performs object detection. The results of these tests are logged for review.

## Project Structure

```
raspberry-pi5-system-test
├── src
│   ├── system_info.py        # Gathers system information
│   ├── camera_test.py        # Tests camera functionalities
│   ├── hailo_test.py         # Tests Hailo-8 hardware
│   ├── object_detection.py    # Performs object detection
├── utils
│   └── logger.py             # Logging utility
├── main.py                   # Entry point of the application
├── requirements.txt          # Project dependencies
├── .gitignore                # Files to ignore in Git
└── README.md                 # Project documentation
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd raspberry-pi5-system-test
   ```

2. **Install dependencies:**
   Ensure you have Python 3 installed, then run:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the system tests, execute the main script:
```
python main.py
```

## Tests Performed

- **System Information:** Collects and displays CPU, RAM, Disk space, OS version, and Firmware version.
- **Camera Test:** Lists available cameras, retrieves their properties, and takes a picture.
- **Hailo-8 Test:** Checks the Hailo-8 hardware and retrieves relevant kernel logs.
- **Object Detection:** Executes an object detection command and saves the resulting video.

## Logging

All test results and statuses are logged to a specified log file for further analysis. Check the `utils/logger.py` for logging configurations.

## Contributing

Feel free to submit issues or pull requests for improvements or bug fixes.