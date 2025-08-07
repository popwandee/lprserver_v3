# AI Camera License Plate Detection

This project implements a vehicle license plate detection system using AI and OCR technologies. The system captures video frames from a camera, detects vehicles and license plates, processes the images for OCR, and stores the results in a SQLite database.

## Project Structure

```
aicamera
├── src
│   ├── __init__.py
│   ├── detection.py          # Main detection logic for vehicles and license plates
│   ├── camera.py             # Camera initialization and frame capturing
│   ├── database.py           # Database initialization and operations
│   ├── image_processing.py    # Image preprocessing functions
│   ├── logging_config.py      # Logging configuration setup
│   ├── model_loader.py        # Model loading from the model zoo
│   ├── ocr_process.py         # OCR processing for license plates
│   ├── similarity.py          # Functions for comparing images and strings
│   └── utils.py              # Utility functions for the project
├── db
│   └── lpr_data.db           # SQLite database for storing license plate data
├── log
│   └── detection.log          # Log file for application events and errors
├── .env.production            # Environment variables for configuration
├── requirements.txt           # Project dependencies
└── README.md                  # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd aicamera
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the environment variables in the `.env.production` file. Ensure to specify paths for the database and model URLs.

## Usage

1. Run the application:
   ```
   python src/detection.py
   ```

2. The application will start capturing video frames, detecting vehicles and license plates, and logging the results.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.