// Camera control functionality
document.addEventListener('DOMContentLoaded', function() {
    // Close camera button functionality
    const closeCameraBtn = document.getElementById('close-camera-btn');
    if (closeCameraBtn) {
        closeCameraBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to close the camera? This will stop all detection and video streaming.')) {
                // Send request to Flask to close camera
                fetch('/close_camera', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            alert('Camera closed successfully!');
                            // Stop video feed display
                            const videoFeed = document.getElementById('video-feed');
                            if (videoFeed) {
                                videoFeed.src = '';
                                videoFeed.alt = 'Camera is closed.';
                            }
                        } else {
                            alert('Error closing camera: ' + data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        alert('An error occurred while trying to close the camera.');
                    });
            }
        });
    }

    // WebSocket connection for real-time metadata
    if (typeof io !== 'undefined') {
        const socket = io();
        
        socket.on('connect', function() {
            console.log('Connected to WebSocket server!');
        });
        
        socket.on('camera_metadata', function(data) {
            console.log('Received camera metadata:', data);
            
            // Update metadata display elements
            const shutterSpeedEl = document.getElementById('shutter-speed-value');
            const analogGainEl = document.getElementById('analog-gain-value');
            const digitalGainEl = document.getElementById('digital-gain-value');
            const exposureTimeEl = document.getElementById('exposure-time-value');
            
            if (shutterSpeedEl && data.shutter_speed) {
                shutterSpeedEl.innerText = (data.shutter_speed / 1000) + ' ms';
            }
            if (analogGainEl && data.analog_gain) {
                analogGainEl.innerText = data.analog_gain;
            }
            if (digitalGainEl && data.digital_gain) {
                digitalGainEl.innerText = data.digital_gain;
            }
            if (exposureTimeEl && data.exposure_time) {
                exposureTimeEl.innerText = data.exposure_time / 1000 + ' ms';
            }
        });

        socket.on('disconnect', function() {
            console.log('Disconnected from WebSocket server');
        });

        socket.on('connect_error', function(error) {
            console.error('WebSocket connection error:', error);
        });
    }
});