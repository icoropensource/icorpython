# -*- coding: utf-8 -*-
import codecs
import thread
import Queue

import appplatform.storageutil as storageutil

# public.sessiontokens - status:
#   A - aktywny
#   L - wylogowany


class DBSessionUtilInit(object):

    def __init__(self, adb):
        self.db = adb

    def initSchema(self):
        asql = '''
         CREATE TABLE IF NOT EXISTS public.sessions
         (
           _oid character(32) NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
           sessionid text DEFAULT ''::text,
           tokenid text DEFAULT ''::text,
           status text DEFAULT ''::text,
           created timestamp without time zone DEFAULT now(),
           _datetime timestamp without time zone DEFAULT now(),
           _uid text DEFAULT ''::text,
           _username text DEFAULT ''::text,
           CONSTRAINT sessions_pkey PRIMARY KEY (_oid)
         ) WITH ( OIDS=FALSE );
         ALTER TABLE public.sessions OWNER TO postgres;
         CREATE INDEX IF NOT EXISTS i_icor_sessions_created ON public.sessions USING btree (created);
         CREATE INDEX IF NOT EXISTS i_icor_sessions_sessionid ON public.sessions USING btree (sessionid COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_sessions_status ON public.sessions USING btree (status COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_sessions_tokenid ON public.sessions USING btree (tokenid COLLATE pg_catalog."default");

         CREATE TABLE IF NOT EXISTS public.sessiontokens
         (
           _oid character(32) NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
           status text DEFAULT ''::text,
           created timestamp without time zone DEFAULT now(),
           _datetime timestamp without time zone DEFAULT now(),
           _uid text DEFAULT ''::text,
           _username text DEFAULT ''::text,
           CONSTRAINT sessiontokens_pkey PRIMARY KEY (_oid)
         ) WITH ( OIDS=FALSE );
         ALTER TABLE public.sessiontokens OWNER TO postgres;
         CREATE INDEX IF NOT EXISTS i_icor_sessiontokens_created ON public.sessiontokens USING btree (created);
         CREATE INDEX IF NOT EXISTS i_icor_sessiontokens_status ON public.sessiontokens USING btree (status COLLATE pg_catalog."default");

         CREATE TABLE IF NOT EXISTS public.sessionvalues
         (
           _oid character(32) NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
           tokenid text DEFAULT ''::text,
           valuetype text DEFAULT ''::text,
           valuename text DEFAULT ''::text,
           value text DEFAULT ''::text,
           status text DEFAULT ''::text,
           created timestamp without time zone DEFAULT now(),
           _datetime timestamp without time zone DEFAULT now(),
           _uid text DEFAULT ''::text,
           _username text DEFAULT ''::text,
           CONSTRAINT sessionvalues_pkey PRIMARY KEY (_oid)
         ) WITH ( OIDS=FALSE );
         ALTER TABLE public.sessionvalues OWNER TO postgres;
         CREATE INDEX IF NOT EXISTS i_icor_sessionvalues_created ON public.sessionvalues USING btree (created);
         CREATE INDEX IF NOT EXISTS i_icor_sessionvalues_status ON public.sessionvalues USING btree (status COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_sessionvalues_tokenid ON public.sessionvalues USING btree (tokenid COLLATE pg_catalog."default");
         CREATE UNIQUE INDEX IF NOT EXISTS i_icor_sessionvalues_tokenid_valuename ON public.sessionvalues USING btree (tokenid COLLATE pg_catalog."default", valuename COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_sessionvalues_value ON public.sessionvalues USING btree (lower(left(value,500)) ASC);
         CREATE INDEX IF NOT EXISTS i_icor_sessionvalues_valuename ON public.sessionvalues USING btree (valuename COLLATE pg_catalog."default");
         CREATE INDEX IF NOT EXISTS i_icor_sessionvalues_valuetype ON public.sessionvalues USING btree (valuetype COLLATE pg_catalog."default");
      '''
        self.db.ExecuteSQL(asql, atableprefix=1)
        return
