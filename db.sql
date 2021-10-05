-- Table: public.users

-- DROP TABLE public.users;

CREATE TABLE IF NOT EXISTS public.users
(
    telegram_id numeric NOT NULL,
    name character varying(128) COLLATE pg_catalog."default",
    pic character varying(255) COLLATE pg_catalog."default",
    job character varying(4000) COLLATE pg_catalog."default",
    interest character varying(4000) COLLATE pg_catalog."default",
    city character varying(4000) COLLATE pg_catalog."default",
    skill character varying(4000) COLLATE pg_catalog."default",
    type numeric,
    enabled numeric,
    run_cnt numeric,
    is_new integer,
    is_admin integer,
    wizard_stage character varying(32) COLLATE pg_catalog."default",
    CONSTRAINT users_pkey PRIMARY KEY (telegram_id)
)

TABLESPACE pg_default;

CREATE UNIQUE INDEX iu_users_id
    ON public.users USING btree
    (telegram_id ASC NULLS LAST)
    TABLESPACE pg_default;
-- Table: public.pair

-- DROP TABLE public.pair;

CREATE TABLE IF NOT EXISTS public.pair
(
    telegram_id1 numeric NOT NULL,
    telegram_id2 numeric NOT NULL,
    date date,
    status integer
)

TABLESPACE pg_default;

-- Index: i_pair_date

-- DROP INDEX public.i_pair_date;

CREATE INDEX i_pair_date
    ON public.pair USING btree
    (date ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: i_pair_user1

-- DROP INDEX public.i_pair_user1;

CREATE INDEX i_pair_user1
    ON public.pair USING btree
    (telegram_id1 ASC NULLS LAST, telegram_id2 ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: i_pair_user2

-- DROP INDEX public.i_pair_user2;

CREATE INDEX i_pair_user2
    ON public.pair USING btree
    (telegram_id2 ASC NULLS LAST, telegram_id1 ASC NULLS LAST)
    TABLESPACE pg_default;
-- Table: public.opinion

-- DROP TABLE public.opinion;

CREATE TABLE IF NOT EXISTS public.opinion
(
    telegram_id1 numeric NOT NULL,
    telegram_id2 numeric NOT NULL,
    date date,
    opinion character varying(4000) COLLATE pg_catalog."default"
)

TABLESPACE pg_default;

ALTER TABLE public.opinion
    OWNER to swineflzqohoxc;
-- Index: i_opinion_date

-- DROP INDEX public.i_opinion_date;

CREATE INDEX i_opinion_date
    ON public.opinion USING btree
    (date ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: i_opinion_user1

-- DROP INDEX public.i_opinion_user1;

CREATE INDEX i_opinion_user1
    ON public.opinion USING btree
    (telegram_id1 ASC NULLS LAST, telegram_id2 ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: i_opinion_user2

-- DROP INDEX public.i_opinion_user2;

CREATE INDEX i_opinion_user2
    ON public.opinion USING btree
    (telegram_id2 ASC NULLS LAST, telegram_id1 ASC NULLS LAST)
    TABLESPACE pg_default;	
