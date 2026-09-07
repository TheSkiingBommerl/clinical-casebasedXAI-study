# Understanding AI Support for ECG Interpretation: A Formative Comparison of Direct Predictions and Case-Based Explanations

- Placeholder: Study describtion

## Set-up 

- To install the required packages, run the installation script in the repository:
    `pip install -r requirements.txt`

- To set up the database, follow the instructions provided [here](database/README.md)

## Experiments
The websites for the experiments were hosted on our own server and users were managed using LDAP (Lightweight Directory Access Protocol) and for authentication we used OAuth2 with Authelia. Each participant received their individual credentials.

### Experiment 1 - Retrieval Calibration as Design Rationale
To choose a fitting ... three similarity methods were ranked by medical professionals.

The methods compared were: 
- Dynamic Time Warping (DTW)
- In-domain embedding similarity
- Out-of-domain embedding similarity

Data Used: 
- CODE-test: Follow the instructions at [Automatic ECG Diagnosis](https://github.com/antonior92/automatic-ecg-diagnosis) to download them.

Data preprocessing:
- ECG filtering: See [folder](signal_filtering).

Models Used:
- [Automatic ECG Diagnosis](https://github.com/antonior92/automatic-ecg-diagnosis): Follow this [instructions](automatic-ecg-diagnosis/README.md)
- [ECG FM](): Follow this [instructions](ecg-fm/README.md)

Similarity measurement:
...

Interface:
A website was created to present the ECG signals to the medical professianals. The code for the website can be foudn here: [Similarity Comparison](website/similarity_comparison).

### Experiment 2 - Diagnostic Decision-Support Study
Introduction ...

Data Used:
- [PTB-XL](https://physionet.org/content/ptb-xl/1.0.3/)

Data preprocessing:
- Dataset filtering: See file [filter_ptbxl_datafile](database\transform_and_load\ptb\data_processing\filter_ptbxl_datafile)
- ECG filtering: See folder [signal_filtering](signal_filtering).

Models Used:
- [Automatic ECG Diagnosis](https://github.com/antonior92/automatic-ecg-diagnosis): Follow this [instructions](automatic-ecg-diagnosis/README.md)




