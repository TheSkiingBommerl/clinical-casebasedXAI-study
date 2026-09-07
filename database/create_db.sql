DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_type') THEN
        CREATE TYPE gender_type AS ENUM ('FEMALE', 'MALE');
    END IF;
END $$;

-- Code-test Data
CREATE SCHEMA IF NOT EXISTS "code-test";

CREATE TABLE IF NOT EXISTS "code-test".patient_data (
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
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'gender_type') THEN
        CREATE TYPE gender_type AS ENUM ('FEMALE', 'MALE');
    END IF;
END $$;
CREATE TABLE IF NOT EXISTS "code-test".filtered_ecgs (
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

CREATE TABLE IF NOT EXISTS "code-test".dnn_annotations(
    id int8 NOT NULL,
    "1dAVb" int2 NOT NULL,
    rbbb int2 NOT NULL,

    lbbb int2 NOT NULL,
    sb int2 NOT NULL,
    af int2 NOT NULL,
    st int2 NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "code-test".prediction_certanties (
    id int8 NOT NULL,
    "1dAVb" numeric NOT NULL,
    rbbb numeric NOT NULL,
    lbbb numeric NOT NULL,
    sb numeric NOT NULL,
    af numeric NOT NULL,
    st numeric NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS "code-test".gold_lable(
    id int8 NOT NULL,
    "1dAVb" int2 NOT NULL,
    rbbb int2 NOT NULL,
    lbbb int2 NOT NULL,
    sb int2 NOT NULL,
    af int2 NOT NULL,
    st int2 NOT NULL,
    PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS"code-test".aed_model_embeddings (
  embedding _numeric
);

CREATE TABLE IF NOT EXISTS "code-test".fm_model_embeddings (
  id int8 PRIMARY KEY,
  embedding _numeric
);

-- PTB-XL DATA
CREATE SCHEMA IF NOT EXISTS "ptb-xl";

CREATE TABLE IF NOT EXISTS "ptb-xl".patient_data AS
TABLE "code-test".patient_data
WITH NO DATA;

CREATE TABLE IF NOT EXISTS "ptb-xl".dnn_annotations AS
TABLE "code-test".dnn_annotations
WITH NO DATA;


CREATE TABLE IF NOT EXISTS "ptb-xl".prediction_certanties AS
TABLE "code-test".prediction_certanties
WITH NO DATA;

CREATE TABLE IF NOT EXISTS "ptb-xl".gold_lable AS
TABLE "code-test".gold_lable
WITH NO DATA;

CREATE TABLE IF NOT EXISTS "ptb-xl".AED_model_embeddings AS
TABLE "code-test".aed_model_embeddings
WITH NO DATA;


CREATE TABLE IF NOT EXISTS "ptb-xl".filtered_ecgs AS
TABLE "code-test".filtered_ecgs
WITH NO DATA;
