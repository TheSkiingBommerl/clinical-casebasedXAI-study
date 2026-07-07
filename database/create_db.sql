CREATE TYPE gender_type AS ENUM ('FEMALE', 'MALE');

-- Code 15 Data
CREATE SCHEMA "code-15";

CREATE TABLE "code-15".patient_data (
    id     bigint      NOT NULL,
    gender gender_type NOT NULL,
    age    integer     NOT NULL,
    di     numeric[],
    dii    numeric[],
    diii   numeric[],
    avr    numeric[],
    avl    numeric[],
    avf    numeric[],
    v1     numeric[],
    v2     numeric[],
    v3     numeric[],
    v4     numeric[],
    v5     numeric[],
    v6     numeric[],
    PRIMARY KEY (id)
);

CREATE TABLE "code-15".filtered_ecgs (
    id     bigint      NOT NULL,
    di     numeric[],
    dii    numeric[],
    diii   numeric[],
    avr    numeric[],
    avl    numeric[],
    avf    numeric[],
    v1     numeric[],
    v2     numeric[],
    v3     numeric[],
    v4     numeric[],
    v5     numeric[],
    v6     numeric[],
    PRIMARY KEY (id)
);

CREATE TABLE "code-15".dnn_annotations(
    id int8 NOT NULL,
    "1dAVb" int2 NOT NULL,
    rbbb int2 NOT NULL,
    lbbb int2 NOT NULL,
    sb int2 NOT NULL,
    af int2 NOT NULL,
    st int2 NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE "code-15".prediction_certanties (
    id int8 NOT NULL,
    "1dAVb" numeric NOT NULL,
    rbbb numeric NOT NULL,
    lbbb numeric NOT NULL,
    sb numeric NOT NULL,
    af numeric NOT NULL,
    st numeric NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE "code-15".gold_lable(
    id int8 NOT NULL,
    "1dAVb" int2 NOT NULL,
    rbbb int2 NOT NULL,
    lbbb int2 NOT NULL,
    sb int2 NOT NULL,
    af int2 NOT NULL,
    st int2 NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE "code-15".aed_model_embeddings (
  id int8 PRIMARY KEY, 
  embedding _numeric
);

CREATE TABLE "code-15".fm_model_embeddings (
  id int8 PRIMARY KEY, 
  embedding _numeric
);

-- PTB-XL DATA
CREATE SCHEMA "ptb-xl";

CREATE TABLE "ptb-xl".patient_data AS
TABLE "code-15".patient_data
WITH NO DATA;

CREATE TABLE "ptb-xl".dnn_annotations AS
TABLE "code-15".dnn_annotations
WITH NO DATA;

CREATE TABLE "ptb-xl".prediction_certanties AS
TABLE "code-15".prediction_certanties
WITH NO DATA;

CREATE TABLE "ptb-xl".gold_lable AS
TABLE "code-15".gold_lable
WITH NO DATA;

CREATE TABLE "ptb-xl".AED_model_embeddings AS
TABLE "code-15".aed_model_embeddings
WITH NO DATA;


CREATE TABLE "ptb-xl".filtered_ecgs AS
TABLE "code-15".filtered_ecgs
WITH NO DATA;

