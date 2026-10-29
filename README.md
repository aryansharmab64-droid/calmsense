# CalmSense — Personalized Stress Intelligence 🧠

### Personalized Stress Level Prediction Using Wearable Sensor Data

**Project Code:** PT190
**Project Guide:** Mr. Pankaj Sharma
**Institution:** IILM University, Greater Noida
**Domain:** Machine Learning | Data Science | Healthcare Technology | Web Development

---

## 📌 About the Project

**CalmSense** is an academic wellness application designed to explore how wearable-style physiological data can be used to estimate possible stress levels and provide personalized wellness recommendations.

The system uses sensor-related features such as heart rate, heart-rate variability (HRV), skin temperature, electrodermal activity (EDA), sleep duration, and physical activity to analyze patterns associated with different stress categories.

The application aims to present understandable stress estimates, historical trends, and practical wellness suggestions through an interactive dashboard.

> **Disclaimer:** CalmSense is an academic prototype, not a medical device. It does not diagnose medical or psychological conditions. Simulated sensor readings and synthetic training data must not be interpreted as clinically validated measurements.

---

## 🎯 Project Objectives

* Explore stress-level estimation using physiological sensor features.
* Develop a web-based interface for monitoring sensor readings.
* Apply machine-learning techniques to classify possible stress levels.
* Visualize historical readings and trends through interactive charts.
* Provide understandable explanations and wellness recommendations.
* Support self-reported mood, sleep, and activity tracking.
* Demonstrate how backend development, databases, and machine learning can work together.

---

## ✨ Key Features

### 1. User Authentication

* User registration and login.
* Personalized user dashboard.
* Profile and preference management.
* Authentication-protected application pages.

### 2. Sensor Monitoring

* Simulated wearable sensor readings.
* Heart-rate and HRV monitoring.
* Skin-temperature and EDA tracking.
* Physical activity and sleep-related features.
* Historical sensor data and live-monitoring interface.

### 3. Stress-Level Prediction

The proposed classification system uses three categories:

* **Low:** Lower levels of stress-associated indicators.
* **Moderate:** Intermediate stress-associated indicators.
* **High:** Higher levels of stress-associated indicators.

The categories represent model estimates, not medical diagnoses.

### 4. Dashboard and Analytics

* Summary cards for available sensor data.
* Historical charts and trends.
* Date-range filters.
* Personal-baseline comparisons when sufficient historical data exists.
* Stress-estimation history and data-quality information.

### 5. Wellness and Self-Care

* Rule-based wellness recommendations.
* Guided breathing exercises.
* Daily mood and stress check-ins.
* Sleep logging.
* Activity tracking and personal goals.
* Notifications and wellness insights.

Recommendation availability depends on the implemented application features and available user data.

---

## 🛠️ Technology Stack

| Component           | Technology                   |
| ------------------- | ---------------------------- |
| Backend             | Python, Django               |
| Frontend            | HTML, CSS, JavaScript        |
| UI Templates        | Django Template Language     |
| Database            | SQLite for local development |
| Machine Learning    | Scikit-learn                 |
| Data Processing     | NumPy, Pandas                |
| Model Serialization | Joblib                       |
| Version Control     | Git and GitHub               |

The final technology stack depends on the installed dependencies and the implementation available in the repository.

---

## 🏗️ System Architecture

CalmSense follows a modular web-application architecture.

```text
             User
              |
              v
       Web Interface
              |
              v
       Django Backend
              |
      +-------+--------+
      |       |        |
      v       v        v
   Sensors  Wellness  Analytics
      |       |        |
      +-------+--------+
              |
              v
       Database Layer
              |
              v
      Sensor Data Processing
              |
              v
       ML Prediction Service
              |
              v
      Stress-Level Estimate
              |
              v
   Dashboard and Recommendations
```

The diagram represents the intended logical architecture. Actual module connections should be verified against the implemented code.

---

## 🧠 Machine-Learning Methodology

The proposed machine-learning pipeline consists of the following stages:

1. **Data Generation or Collection:** Obtain suitable sensor-feature records.
2. **Preprocessing:** Validate input values and handle missing or invalid features.
3. **Feature Extraction:** Prepare heart rate, HRV, skin temperature, EDA, steps, and sleep duration.
4. **Model Training:** Train a classification model using appropriately labelled data.
5. **Model Evaluation:** Evaluate the model using accuracy, precision, recall, F1-score, and a confusion matrix where applicable.
6. **Prediction:** Generate a stress-category estimate from valid input features.
7. **Explanation:** Present relevant input information and limitations to the user.
8. **Visualization:** Display predictions and available historical trends.

A Random Forest classifier is the intended model described in the project implementation notes.

**Dataset limitation:** If synthetic data is used for training, the resulting performance metrics describe performance on that synthetic data. They do not establish real-world or clinical accuracy.

Actual model results should be documented only after the training and evaluation scripts have been executed successfully.

---

## 📂 Project Structure

The repository is organized into Django applications and supporting resources.

```text
calmsense/
│
├── analytics/
│   ├── migrations/
│   ├── admin.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── core/
│   ├── management/
│   ├── migrations/
│   ├── models.py
│   ├── forms.py
│   └── views.py
│
├── predictions/
├── recommendations/
├── sensors/
├── wellness/
│
├── ml/
├── static/
├── templates/
│
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

Some directories may contain additional files not shown above. The `ml/` directory must contain the required training and prediction components before the machine-learning workflow can be considered complete.

---

## ⚙️ Installation and Setup

### Prerequisites

Install the following:

* Python 3.10 or another version compatible with the project's dependencies.
* Git.
* A terminal such as Windows PowerShell.
* A web browser.

### Step 1: Clone the Repository

```bash
git clone https://github.com/aryansharmab64-droid/calmsense.git
cd calmsense
```

### Step 2: Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, you can use Command Prompt:

```cmd
venv\Scripts\activate.bat
```

### Step 3: Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If installation fails, check the Python version and the package versions specified in `requirements.txt`.

### Step 4: Configure Environment Variables

Review `.env.example` and create a local `.env` file if the project requires it.

Use a unique secret key for local development. Never commit real secrets, passwords, or API keys to GitHub.

### Step 5: Apply Database Migrations

```bash
python manage.py migrate
```

If the application contains unapplied model changes, generate migrations only after reviewing the changes:

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create an Administrator Account

```bash
python manage.py createsuperuser
```

Follow the prompts to configure the account.

### Step 7: Start the Development Server

```bash
python manage.py runserver
```

Open the following address in your browser:

http://127.0.0.1:8000/

The development server runs locally on your computer. It does not automatically deploy the application to the internet.

---

## 🧪 Testing

Run Django's system checks:

```bash
python manage.py check
```

Run the automated tests:

```bash
python manage.py test
```

Verify the following workflows before presenting the project:

* User registration and authentication.
* Sensor-reading generation and database persistence.
* Input validation and error handling.
* ML-model loading and prediction, if implemented.
* Dashboard charts and historical records.
* Wellness recommendations and check-ins.
* User-data isolation.
* Report generation, if implemented.

Only describe a feature as tested after successfully executing the relevant tests.

---

## 🔐 Security and Privacy

CalmSense should follow these practices:

* Protect authenticated routes.
* Restrict records to their authorized users.
* Validate and sanitize user inputs.
* Use Django's CSRF protections for relevant requests.
* Keep secrets and environment files out of version control.
* Avoid exposing private sensor readings through public endpoints.
* Use secure deployment settings before hosting the application publicly.

The current project should be reviewed and tested to confirm that these protections work as intended.

---

## ⚠️ Limitations

1. Simulated sensor readings are not equivalent to measurements from a real wearable device.
2. Synthetic training data cannot establish clinical validity.
3. A prediction is an estimate based on the features and training data available to the model.
4. Individual differences, physical activity, sleep, and other factors can affect physiological measurements.
5. The project does not replace professional medical assessment.
6. Actual smartwatch or Bluetooth integration requires additional implementation.
7. Production deployment requires appropriate security, monitoring, and privacy controls.

---

## 🚀 Future Scope

Potential future improvements include:

* Integration with compatible wearable devices.
* Evaluation using suitable real-world, ethically sourced datasets.
* Personalized baselines based on sufficient historical readings.
* Improved model interpretability and calibration.
* Additional time-series analysis.
* More comprehensive automated testing.
* PDF and CSV wellness reports.
* Cloud deployment with appropriate security.
* Accessibility improvements and multilingual support.

These are proposed improvements, not claims that the features are already implemented.

---

## 👨‍💻 Project Information

**Project:** Personalized Stress Level Prediction Using Wearable Sensor Data
**Product Name:** CalmSense — Personalized Stress Intelligence
**Project Code:** PT190
**Project Guide:** Mr. Vivek Krishna Mishra
**Institution:** IILM University, Greater Noida
**Degree Program:** B.Tech — Computer Science and Engineering

---

## 📜 Disclaimer

CalmSense is developed for educational and academic demonstration purposes. It is not intended to diagnose, treat, cure, or prevent any disease or mental-health condition.

All simulated readings, synthetic datasets, and model outputs must be interpreted within the limitations of the implementation. The application should not be used as a substitute for professional medical advice.

---

## ⭐ Acknowledgements

I would like to acknowledge the academic guidance and learning opportunities that support the development of this project.

This project demonstrates the application of software development, data processing, machine learning, and interactive visualization to an exploratory wellness use case.
