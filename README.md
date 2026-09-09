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
```signals

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

The initialization script downloads the following datasets and models:
- **CODE-15%** (from [Zenedo](https://zenodo.org/records/3765780/)): _ a large scale annotated dataset of 12-lead ECGs_
- **PTB-XL** (from [PhysioNet](https://physionet.org/content/ptb-xl/1.0.3/)): _a large publicly available electrocardiography dataset_
- **ECG-FM finetuned on MIMIC IV** (From [HuggingFace](https://huggingface.co/wanglab/ecg-fm/tree/main)): _a foundation model for electrocardogram (ECG) analysis_
- **Automatic Diagnosis of the 12-Lead ECG** (from [Zenedo](Automatic Diagnosis of the 12-Lead {{ECG}})): _Automatic diagnosis of the 12-lead ECG using a deep neural network_

``` bash
# Activate venv on MacOS / Linux
source .venv/bin/activate

# Activate venv on Windows
.venv\Scripts\activate.bat

# Download datasets (if not already downloaded) and populate the tables
clinical-friction-init-db
```

### Initializing the experiments

The necessary tables and files for each of the two experiments must be generated before running either of the tools.

#### Initialize the similarity comparison experiment

``` bash
# In the activated virtual environment, run:
clinical-friction-init-similarity
```

#### Initialize the decision support experiment

``` bash
# In the activated virtual environment, run:
clinical-friction-init-support
```

## Hosting the website

The websites for the experiments were hosted on our own server and users were managed using LDAP (Lightweight Directory Access Protocol) and for authentication we used OAuth2 with Authelia. Each participant received their individual credentials.

### Using your own Oauth 2 endpoint

Setting up a OAuth2 provider is nontrivial.
We used [LLDAP](https://github.com/lldap/lldap) for the user management and [Authelia](https://www.authelia.com/).
A domain name is needed.

If you know how to do this, rename `example_secrets.toml` in the `.streamlit` to `secrets.toml` and fill it in.

### Bypassing the login to demo the tool.

It is possible to bypass the login checks when running locally by setting the following environment variabe:

``` bash
# Set this environment variable to bypass the login.
# Valid suffixes are _0_0 up to _0_7
export CF_BYPASS_LOGIN=participant_0_1
```

The hosted tool will recognize you as this participant.


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
