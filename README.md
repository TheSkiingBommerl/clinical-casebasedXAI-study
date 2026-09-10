# Prediction, Precedent, or Both? Comparing Direct Predictions and Retrieved Cases for AI-Supported ECG Interpretation

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

<details>
  <summary><b>Installation instructions</b></summary>

  <p><em>Windows</em></p>
  <pre><code class="language-cmd">winget install PostgreSQL.PostgreSQL.18</code></pre>

  <p><em>Debian - Ubuntu</em></p>
  <pre><code class="language-cmd">sudo apt install postgresql</code></pre>

  <p><em>MacOS</em></p>
  <pre><code class="language-zsh">brew install postgresql@18</code></pre>
</details>

#### 2. Create the database

First, create a database (the name is arbitrary):
``` bash
createdb AIdiagnosticsupport
```

Ensure its name is listed in the `.env` file under the `DB_NAME` key:

```.env
DB_NAME=AIdiagnosticsupport
```

#### 3. Initialize the database

Open a terminal and activate the virtual environment.
Then, run `AI-diagnostic-support-init-db` to download the datasets + model and add the necessary tables to the database.

The initialization script downloads the following datasets and models:
- **CODE-test** (from [Zenedo](https://zenodo.org/records/3765780/)): _ a large scale annotated dataset of 12-lead ECGs_
- **PTB-XL** (from [PhysioNet](https://physionet.org/content/ptb-xl/1.0.3/)): _a large publicly available electrocardiography dataset_
- **ECG-FM finetuned on MIMIC IV** (From [HuggingFace](https://huggingface.co/wanglab/ecg-fm/tree/main)): _a foundation model for electrocardogram (ECG) analysis_
- **Automatic Diagnosis of the 12-Lead ECG** (from [Zenedo](Automatic Diagnosis of the 12-Lead {{ECG}})): _Automatic diagnosis of the 12-lead ECG using a deep neural network_

``` bash
# Activate venv on MacOS / Linux
source .venv/bin/activate

# Activate venv on Windows
.venv\Scripts\activate.bat

# Download datasets (if not already downloaded) and populate the tables
AI-diagnostic-support-init-db
```

### Initializing the study

The necessary tables and files must be generated before running either of the tools.

#### Initialize the similarity comparison

``` bash
# In the activated virtual environment, run:
AI-diagnostic-support-init-similarity
```

#### Initialize the decision support

``` bash
# In the activated virtual environment, run:
AI-diagnostic-support-init-support
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

# Study Description

## Similarity Comparison - Retrieval Calibration as Design Rationale
Check if any of the three similarity measures clearly misaligned with human similarity perception. 

The methods compared were: 
- Dynamic Time Warping (DTW)
- Embedding similarity of the A-ECG-D model
- Embedding similarity of the ECG-FM model

**Data Used:** 
- CODE-test

**Models Used:**
- [Automatic ECG Diagnosis](https://github.com/antonior92/automatic-ecg-diagnosis)
- [ECG FM](https://github.com/bowang-lab/ecg-fm)

**Embedding extraction:** See folder [automatic_ecg_diagnosis](src/AI_diagnostic_support/automatic_ecg_diagnosis) and [ecg_embeddings](src/AI_diagnostic_support/__init__.pyecg_embeddings)

**Similarity measurement:** See folder [similarity_measure](src/AI_diagnostic_support/similarity_measure)

**Data preprocessing** (before displayed on website)**:**
- ECG filtering: See [signal_filtering](src/AI_diagnostic_support/signal_filtering)

**Interface:**
A website was created to present the ECG signals to the medical professionals. The code for the website can be found here: [Similarity Comparison](website/similarity_comparison).

**Analysis:** See folder [statistics/similarity_comparison](statistics/similarity_comparison)

## Decision Support Tool - Diagnostic Decision-Support Study
Clinician-facing web prototype for a simulated multi-label ECG interpretation task, comparing direct AI predictions and retrieved case examples, presented individually and together, against a no-AI baseline.

**Data Used:**
- [PTB-XL](https://physionet.org/content/ptb-xl/1.0.3/)

**Models Used:**
- [Automatic ECG Diagnosis](https://github.com/antonior92/automatic-ecg-diagnosis): Follow this [instructions](automatic-ecg-diagnosis/README.md)

**Data preprocessing** (before displayed on website)**:**
- Dataset filtering: See file [filter_ptbxl_datafile](src/AI_diagnostic_support/database/transform_and_load/ptb/data_processing/filter_ptbxl_datafile)
- ECG filtering: See folder [signal_filtering](src/AI_diagnostic_support/signal_filtering).

**Interface:**
On the website medical professionals diagnosed 20 ECG cases, five per configuration, and then completed a questionnaire.
The code for the website can be found here: [Decision Support Tool](website/decision_support_tool).

**Analysis:** See folder [statistics/decision_support_tool](statistics/decision_support_tool)
