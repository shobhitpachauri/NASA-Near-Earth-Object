# Near-Earth Objects Hazard Monitor 🌍☄️

## Project Overview

The Near-Earth Objects Hazard Monitor is a web application designed to monitor and analyze potentially hazardous near-Earth objects (NEOs). The application provides real-time data visualization of NEOs, including their relative velocities, miss distances, and other relevant metrics. It aims to enhance public awareness and scientific understanding of NEOs that could pose a threat to Earth.

## Features

- **Real-time Monitoring**: Fetches and displays real-time data on NEOs from NASA's API.
- **Dynamic Visualization**: Utilizes interactive plots to visualize the relationship between miss distance and relative velocity of hazardous objects.
- **Threshold Analysis**: Implements threshold lines to easily identify objects that exceed defined safety limits.
- **Historical Data Tracking**: Maintains a history of detected hazardous objects for analysis over time.

## Technologies Used

- **Backend**: 
  - **Flask**: A lightweight WSGI web application framework for Python, used to create the API that serves NEO data.
  - **Pandas**: A data manipulation library for Python, used to handle and process data.
  - **NumPy**: A library for numerical computations in Python, used for generating random data and calculations.
  - **Requests**: A simple HTTP library for Python, used to make API calls to NASA's data sources.

- **Frontend**: 
  - **Streamlit**: An open-source app framework for Machine Learning and Data Science projects, used to create the web interface for the application.
  - **Plotly**: A graphing library for Python, used to create interactive plots and visualizations.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/shobhitpachauri/NASA-Near-Earth-Object
   cd NASA-Near-Earth-Object
   ```

2. **Set Up the Backend**:
   - Navigate to the `backend` directory.
   - Install the required packages:
     ```bash
     pip install -r requirements.txt
     ```
   - Run the Flask application:
     ```bash
     python app.py
     ```

3. **Set Up the Frontend**:
   - Navigate to the `frontend` directory.
   - Install the required packages:
     ```bash
     pip install -r requirements.txt
     ```
   - Run the Streamlit application:
     ```bash
     streamlit run app.py
     ```

## Usage

- Open your web browser and navigate to `http://localhost:8501` to access the Near-Earth Objects Hazard Monitor.
- The application will display real-time data on hazardous NEOs, including a threshold plot and metrics for analysis.

## Future Enhancements

- Integrate additional data sources for more comprehensive analysis (e.g., meteorite landings, fireball events).
- Implement user authentication for personalized data tracking.
- Enhance the user interface for better usability and aesthetics.

## Acknowledgments

- NASA for providing the data APIs.
- The open-source community for the libraries and frameworks used in this project.
