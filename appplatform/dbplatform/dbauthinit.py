# -*- coding: utf-8 -*-


class DBAuthUtilInit(object):

    def __init__(self, adb):
        self.db = adb

    def initSchema(self):
        aPGSystemMaxConnections = self.db.GetConfigValue('PGSystemMaxConnections', 400)
        asql = '''
         ALTER SYSTEM SET max_connections = %d;
      ''' % (aPGSystemMaxConnections, )
        aPGSystemWALCompression = self.db.GetConfigValue('PGSystemWALCompression', 1)
        asql = '''
         ALTER SYSTEM SET wal_compression = %d;
      ''' % (aPGSystemWALCompression, )
        self.db.ExecuteSQL(asql, atableprefix=1)
        asql = '''
         CREATE TABLE IF NOT EXISTS public.users
         (
           _oid character(32) NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
           uid text DEFAULT ''::text,
           username text DEFAULT ''::text,
           description text DEFAULT ''::text,
           password text DEFAULT ''::text,
           passwordexpiration integer DEFAULT 0,
           passwordhistory text DEFAULT ''::text,
           passwordlastchange timestamp without time zone DEFAULT now(),
           passwordmustchange text DEFAULT ''::text,
           vcfemail text DEFAULT ''::text,
           vcffirstname text DEFAULT ''::text,
           vcflastname text DEFAULT ''::text,
           vcfphone text DEFAULT ''::text,
           vcflogin text DEFAULT ''::text,
           vcfid text DEFAULT ''::text,
           wwwdisabled text DEFAULT ''::text,
           status text DEFAULT ''::text,
           created timestamp without time zone DEFAULT now(),
           variables text DEFAULT ''::text,
           groups jsonb DEFAULT '{}'::jsonb,
           params jsonb DEFAULT '{}'::jsonb,
           CONSTRAINT icor_users_pkey PRIMARY KEY (_oid)
         ) WITH ( OIDS=FALSE );
         ALTER TABLE public.users OWNER TO postgres;
         CREATE INDEX IF NOT EXISTS i_icor_users_uid ON public.users USING btree (uid COLLATE pg_catalog."default");
         CREATE UNIQUE INDEX IF NOT EXISTS i_icor_users_username ON public.users USING btree (username COLLATE pg_catalog."default");
         CREATE UNIQUE INDEX IF NOT EXISTS i_icor_users_username_lower ON public.users USING btree (lower(username) COLLATE pg_catalog."default" ASC);
         CREATE INDEX IF NOT EXISTS i_icor_users_passwordexpiration ON public.users USING btree (passwordexpiration);
         CREATE INDEX IF NOT EXISTS i_icor_users_passwordlastchange ON public.users USING btree (passwordlastchange);
         CREATE INDEX IF NOT EXISTS i_icor_users_passwordmustchange ON public.users USING btree (passwordmustchange COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_users_vcfemail ON public.users USING btree (vcfemail COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_users_vcffirstname ON public.users USING btree (vcffirstname COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_users_vcflastname ON public.users USING btree (vcflastname COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_users_vcfphone ON public.users USING btree (vcfphone COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_users_vcflogin ON public.users USING btree (vcflogin COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_users_vcfid ON public.users USING btree (vcfid COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_users_wwwdisabled ON public.users USING btree (wwwdisabled COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_users_status ON public.users USING btree (status COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_users_created ON public.users USING btree (created);
         CREATE INDEX IF NOT EXISTS i_icor_users_groups ON public.users USING GIN (groups);
         CREATE INDEX IF NOT EXISTS i_icor_users_params ON public.users USING GIN (params);
      '''
        self.db.ExecuteSQL(asql, atableprefix=1)
        asql = '''
         CREATE TABLE IF NOT EXISTS public.useroperations
         (
           _oid character(32) NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
           uid text DEFAULT ''::text,
           odatetime timestamp without time zone DEFAULT now(),
           okind text DEFAULT ''::text,
           otype text DEFAULT ''::text,
           ovalue text DEFAULT ''::text,
           oinfo text DEFAULT ''::text,
           ooidref text DEFAULT ''::text,
           ostatus text DEFAULT ''::text,
           ovariables text DEFAULT ''::text,
           oparams jsonb DEFAULT '{}'::jsonb,
           oposition integer DEFAULT 0,
           onumber1 integer DEFAULT 0,
           onumber2 integer DEFAULT 0,
           odatetime2 timestamp without time zone DEFAULT now(),
           CONSTRAINT icor_useroperations_pkey PRIMARY KEY (_oid)
         ) WITH ( OIDS=FALSE );
         ALTER TABLE public.useroperations OWNER TO postgres;
         CREATE INDEX IF NOT EXISTS i_icor_useroperations_uid ON public.useroperations USING btree (uid COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_useroperations_odatetime ON public.useroperations USING btree (odatetime);
         CREATE INDEX IF NOT EXISTS i_icor_useroperations_odatetime2 ON public.useroperations USING btree (odatetime2);
         CREATE INDEX IF NOT EXISTS i_icor_useroperations_okind ON public.useroperations USING btree (okind COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_useroperations_otype ON public.useroperations USING btree (otype COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_useroperations_ovalue ON public.useroperations USING btree (left(ovalue,500) COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_useroperations_ooidref ON public.useroperations USING btree (ooidref COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_useroperations_ostatus ON public.useroperations USING btree (ostatus COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_useroperations_oparams ON public.useroperations USING GIN (oparams);
         CREATE INDEX IF NOT EXISTS i_icor_useroperations_oposition ON public.useroperations USING btree (oposition);
         CREATE INDEX IF NOT EXISTS i_icor_useroperations_onumber1 ON public.useroperations USING btree (onumber1);
         CREATE INDEX IF NOT EXISTS i_icor_useroperations_onumber2 ON public.useroperations USING btree (onumber2);
      '''
        self.db.ExecuteSQL(asql, atableprefix=1)
        asql = '''
         CREATE TABLE IF NOT EXISTS public.settings
         (
           _oid character(32) NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
           appid text DEFAULT ''::text,
           key text DEFAULT ''::text,
           name text DEFAULT ''::text,
           status text DEFAULT ''::text,
           uid text DEFAULT ''::text,
           created timestamp without time zone DEFAULT now(),
           value jsonb DEFAULT '{}'::jsonb,
           CONSTRAINT icor_settings_pkey PRIMARY KEY (_oid)
         ) WITH ( OIDS=FALSE );
         ALTER TABLE public.settings OWNER TO postgres;
         CREATE INDEX IF NOT EXISTS i_icor_settings_appid ON public.settings USING btree (appid COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_settings_key ON public.settings USING btree (key COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_settings_name ON public.settings USING btree (name COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_settings_status ON public.settings USING btree (status COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_settings_uid ON public.settings USING btree (uid COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_settings_created ON public.settings USING btree (created);
         CREATE INDEX IF NOT EXISTS i_icor_settings_value ON public.settings USING GIN (value);
      '''
        self.db.ExecuteSQL(asql, atableprefix=1)
        # okind:
        #    news
        #    post
        #    promotion
        # otype:
        # ostatus:
        #    "T1","W trakcie pracy","|P1"
        #    "S1","Do sprawdzenia","T1"
        #    "P1","Do poprawki","S1|Z1"
        #    "X1","Odrzucony","S1|Z1"
        #    "A1","Archiwalny","Z1"
        #    "Z1","Zatwierdzony do publikacji","S1"
        # oprioritydisplay:
        #    "N1","Normalny - poziom 1"
        #    "N0","Normalny - poziom 0"
        #    "N2","Normalny - poziom 2"
        #    "A0","Przypięty - poziom 0"
        #    "A1","Przypięty - poziom 1"
        #    "A2","Przypięty - poziom 2"
        # opriorityitem:
        #    "00","Ignorowany"
        #    "03","Normalny"
        #    "01","Niski"
        #    "05","Wysoki"
        asql = '''
         CREATE TABLE IF NOT EXISTS public.usercontent
         (
           _oid character(32) NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
           uid text DEFAULT ''::text,
           odatetime timestamp without time zone DEFAULT now(),
           okind text DEFAULT ''::text,
           otype text DEFAULT ''::text,
           ooidref text DEFAULT ''::text,
           ostatus text DEFAULT ''::text,
           oparams jsonb DEFAULT '{}'::jsonb,
           odatetimefrom timestamp without time zone DEFAULT now(),
           odatetimeto timestamp without time zone DEFAULT now(),
           odatetimeviewfrom timestamp without time zone DEFAULT now(),
           odatetimeviewto timestamp without time zone DEFAULT now(),
           otitle text DEFAULT ''::text,
           osubtitle text DEFAULT ''::text,
           oauthor text DEFAULT ''::text,
           oabstract text DEFAULT ''::text,
           otext text DEFAULT ''::text,
           ocomment text DEFAULT ''::text,
           oprioritydisplay text DEFAULT ''::text,
           opriorityitem text DEFAULT ''::text,
           oposition integer DEFAULT 0,
           ocategories jsonb DEFAULT '{}'::jsonb,
           CONSTRAINT icor_usercontent_pkey PRIMARY KEY (_oid)
         ) WITH ( OIDS=FALSE );
         ALTER TABLE public.usercontent OWNER TO postgres;
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_uid ON public.usercontent USING btree (uid COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_odatetime ON public.usercontent USING btree (odatetime);
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_okind ON public.usercontent USING btree (okind COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_otype ON public.usercontent USING btree (otype COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_ooidref ON public.usercontent USING btree (ooidref COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_ostatus ON public.usercontent USING btree (ostatus COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_oparams ON public.usercontent USING GIN (oparams);
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_odatetimefrom ON public.usercontent USING btree (odatetimefrom);
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_odatetimeto ON public.usercontent USING btree (odatetimeto);
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_odatetimeviewfrom ON public.usercontent USING btree (odatetimeviewfrom);
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_odatetimeviewto ON public.usercontent USING btree (odatetimeviewto);
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_otitle ON public.usercontent USING btree (otitle COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_osubtitle ON public.usercontent USING btree (osubtitle COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_oauthor ON public.usercontent USING btree (oauthor COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_oabstract ON public.usercontent USING btree (left(oabstract,500) COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_otext ON public.usercontent USING btree (left(otext,500) COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_ocomment ON public.usercontent USING btree (left(ocomment,500) COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_oprioritydisplay ON public.usercontent USING btree (oprioritydisplay COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_opriorityitem ON public.usercontent USING btree (opriorityitem COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_oposition ON public.usercontent USING btree (oposition);
         CREATE INDEX IF NOT EXISTS i_icor_usercontent_ocategories ON public.usercontent USING GIN (ocategories);
      '''
        self.db.ExecuteSQL(asql, atableprefix=1)
        return
