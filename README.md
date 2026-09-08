# Understanding AI Support for ECG Interpretation: A Formative Comparison of Direct Predictions and Case-Based Explanations

- Placeholder: Study describtion

## Installation

### Setting up the environment

The [uv package manager](https://docs.astral.sh/uv/getting-started/installationhttps://docs.astral.sh/uv/getting-started/installation//) is recommended to replicate the environment with the proper Python version.

``` bash
# Clone the repository
git clone https://github.com/TheSkiingBommerl/clinical-casebasedXAI-study.git
cd clinical-casebasedXAI-study

# Create a virtual environment with uv and install all dependencies
uv sync
uv pip install -e ./

# Activate the virtual environment
source .venv/bin/activate
```

### Setting up the database

#### 1. Install PostgreSQL
This project requires a working installation of [PostgreSQL](https://www.postgresql.org/download/).

<details><summary><b>Installation instructions</b></summary>

_Windows_
``` cmd
winget install PostgreSQL.PostgreSQL.18
```

_Debian - Ubuntu_
``` cmd
sudo apt install postgresql
```

_MacOS_
``` zsh
brew install postgresql@18
```

</details>

#### 2. Create the database

First, create a database (the name is arbitrary):
``` bash
createdb clinicalfriction
```

Ensure its name is listed in the `.env` file under the `DB_NAME` key:

```.env
DB_NAME=clinicalfriction
```

#### 3. Initialize the database

Open a terminal and activate the virtual environment.
Then, run `clinical-friction-init-db` to download the datasets + model and add the necessary tables to the database.

``` bash
# Activate venv on MacOS / Linux
source .venv/bin/activate

# Activate venv on Windows
.venv\Scripts\activate.bat

# Download datasets (if not already downloaded) and populate the tables
clinical-friction-init-db
```

#### 4. Initialize the database

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
