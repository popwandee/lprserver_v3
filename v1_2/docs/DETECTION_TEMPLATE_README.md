# Detection Template - AI Camera System

## Overview

The detection template provides a comprehensive table view for displaying license plate recognition results with advanced features including pagination, sorting, filtering, and search capabilities.

## Features

### 📊 Statistics Dashboard
- **Total Detections**: Shows the total number of detections in the database
- **Today's Detections**: Displays detections from the current day
- **Average Confidence**: Shows the average confidence score across all detections
- **Unique Plates**: Count of unique license plates detected

### 🔍 Search & Filtering
- **License Plate Search**: Real-time search by license plate number
- **Date Range Filter**: Filter by date range (from/to)
- **Items per Page**: Configurable pagination (10, 25, 50, 100 items)
- **Clear Filters**: One-click filter reset

### 📋 Data Table
- **Sortable Columns**: Click headers to sort by:
  - License Plate
  - Confidence
  - Timestamp
  - Exposure Time
  - Analog Gain
- **Image Preview**: Thumbnail images with modal view
- **Action Buttons**: View details and download images
- **Responsive Design**: Works on desktop and mobile devices

### 📄 Pagination
- **Page Navigation**: Previous/Next buttons
- **Page Numbers**: Direct page navigation
- **Results Info**: Shows current page range and total count

### 📤 Export Functionality
- **CSV Export**: Download filtered data as CSV file
- **Filtered Export**: Export respects current search and filter settings
- **Timestamped Files**: Automatic filename generation with timestamp

## File Structure

```
v2/
├── templates/
│   └── detection.html          # Main detection template
├── static/
│   ├── css/
│   │   └── detection.css       # Styles for detection template
│   ├── js/
│   │   └── detection.js        # JavaScript functionality
│   └── images/                 # Directory for detection images
├── simple_app.py               # Main application with detection routes
├── database_manager.py         # Database operations for detection data
└── run_simple_app.sh          # Startup script
```

## API Endpoints

### GET `/detection`
- Renders the detection template page

### GET `/api/detection_data`
- Returns paginated detection data
- Query parameters:
  - `page`: Page number (default: 1)
  - `per_page`: Items per page (default: 10)
  - `sort_by`: Sort field (default: timestamp)
  - `sort_order`: Sort direction (asc/desc, default: desc)
  - `search`: Search term for license plate
  - `date_from`: Start date filter
  - `date_to`: End date filter

### GET `/api/detection_stats`
- Returns detection statistics
- Response includes total detections, today's count, average confidence, and top plates

### GET `/api/export_detection_data`
- Exports detection data as CSV
- Respects current filter settings
- Returns downloadable CSV file

## Database Schema

The detection template works with the following database tables:

### `camera_metadata`
- `id`: Primary key
- `frame_id`: Unique frame identifier
- `timestamp`: Detection timestamp
- `exposure_time`: Camera exposure setting
- `analog_gain`: Camera gain setting
- `lux`: Brightness level
- `image_filename`: Original image filename
- `processed_image_filename`: Image with bounding boxes

### `detection_results`
- `id`: Primary key
- `frame_id`: Links to camera_metadata
- `license_plate_text`: Detected license plate
- `lp_confidence`: Detection confidence (0-100)
- `lp_image_filename`: Cropped license plate image
- `lp_box_x/y/w/h`: Bounding box coordinates

## Usage

### Starting the Application
```bash
cd v2
./run_simple_app.sh
```

### Accessing the Detection Page
1. Start the application
2. Navigate to `http://localhost:5000`
3. Click "Detection Results" in the navigation
4. Or directly access `http://localhost:5000/detection`

### Using the Interface
1. **View Statistics**: Statistics cards show at the top
2. **Search**: Use the search box to find specific license plates
3. **Filter by Date**: Set date range to narrow results
4. **Sort**: Click column headers to sort data
5. **Navigate**: Use pagination controls to browse pages
6. **Export**: Click "Export Data" to download CSV
7. **View Images**: Click image thumbnails to see full-size images

## Customization

### Styling
- Modify `static/css/detection.css` to change appearance
- CSS variables are defined at the top for easy color customization
- Responsive design breakpoints are included

### Functionality
- Edit `static/js/detection.js` to modify behavior
- The `DetectionTable` class handles all table operations
- Event handlers can be customized for specific needs

### Database Queries
- Modify `database_manager.py` methods for different data requirements
- Add new filter options by extending the query building logic

## Browser Compatibility

- **Chrome**: Full support
- **Firefox**: Full support
- **Safari**: Full support
- **Edge**: Full support
- **Mobile browsers**: Responsive design supported

## Performance Considerations

- **Pagination**: Large datasets are paginated for performance
- **Debounced Search**: Search input is debounced to reduce API calls
- **Image Optimization**: Thumbnails are used for table display
- **Database Indexing**: Ensure proper indexes on frequently queried fields

## Troubleshooting

### Common Issues

1. **No data displayed**
   - Check database connection
   - Verify detection data exists in database
   - Check browser console for JavaScript errors

2. **Images not loading**
   - Ensure `static/images/` directory exists
   - Check file permissions
   - Verify image filenames in database

3. **Export not working**
   - Check browser download settings
   - Verify CSV generation in server logs
   - Ensure proper MIME type headers

4. **Search not working**
   - Check database query syntax
   - Verify search parameter handling
   - Check browser console for errors

### Debug Mode
Enable debug logging by setting `FLASK_ENV=development` in the startup script.

## Future Enhancements

- **Real-time Updates**: WebSocket integration for live data
- **Advanced Analytics**: Charts and graphs for data visualization
- **Bulk Operations**: Select multiple items for batch actions
- **User Authentication**: Role-based access control
- **API Rate Limiting**: Protect against excessive requests
- **Data Archiving**: Automatic cleanup of old records 