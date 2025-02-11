## To run this project:

export AUDD_KEY=your_audd_api_key (in terminal running audio_recognition_services)

### Run the Microservices

python database_management_service.py
python catalogue_management_service.py
python audio_recognition_service.py

### Run the Test Suite

python -m unittest test_microservices.py