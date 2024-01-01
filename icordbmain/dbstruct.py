# -*- coding: utf-8 -*-
import types

from psycopg2.extras import Json

import icorexceptions
import appplatform.storageutil as storageutil
import appplatform.startutil as startutil

import dbclasses

CLASSES_System_ICORClass = 460
CLASSES_System_ICORField = 461
CLASSES_System_ICORMethod = 462

CLASSES_System_ICORClass_aBaseCID = 4091
CLASSES_System_ICORClass_aBasePath = 4100
CLASSES_System_ICORClass_aClassName = 4101
CLASSES_System_ICORClass_aFields = 4110
CLASSES_System_ICORField_aIDClassField = 4151
CLASSES_System_ICORField_aFieldName = 4150

PG_FIELDS = 1
PG_ALLDATA = 2

cv_eq = 1
cv_le = 2
cv_ge = 4
cv_not = 8
cv_neq = cv_not + cv_eq
cv_nle = cv_not + cv_le
cv_nge = cv_not + cv_ge
cv_leeq = cv_eq + cv_le
cv_geeq = cv_eq + cv_ge
cv_nleeq = cv_not + cv_eq + cv_le
cv_ngeeq = cv_not + cv_eq + cv_ge


class ICORDBStruct(object):

    def __init__(self, adb):
        self.db = adb
        self._cidfieldname2fdata = {}
        self._cidmethodname2mdata = {}
        self._cid2cdata = {}
        self._fid2fieldnamecid = {}
        self._fid2data = {}
        afname = startutil.GetLogTempFileName('dbstruct')
        self.mlog = startutil.MLog(afname, aconsole=0)

    def initSchema(self, asqlonly=0):
        print 'Init DB: struct'
        d = {'PGUser': self.db.GetConfigValue('PGUser'), 'PGSchema': self.db.GetConfigValue('PGSchema'), }
        # manually create user
        # manually create database
        asql = '''
         CREATE EXTENSION IF NOT EXISTS "uuid-ossp" SCHEMA public VERSION "1.1";
         CREATE SCHEMA IF NOT EXISTS %(PGSchema)s AUTHORIZATION %(PGUser)s;
         CREATE SCHEMA IF NOT EXISTS icor AUTHORIZATION %(PGUser)s;
         CREATE SCHEMA IF NOT EXISTS mlogs AUTHORIZATION %(PGUser)s;
         CREATE SCHEMA IF NOT EXISTS mtemp AUTHORIZATION %(PGUser)s;
         CREATE SCHEMA IF NOT EXISTS msnapshots AUTHORIZATION %(PGUser)s;
         CREATE SCHEMA IF NOT EXISTS mhistory AUTHORIZATION %(PGUser)s;
         CREATE SCHEMA IF NOT EXISTS test AUTHORIZATION %(PGUser)s;

         CREATE TABLE IF NOT EXISTS icor.cmschapteroperation
         (
            _oid character(32) COLLATE pg_catalog."default" NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
            chapterid integer DEFAULT 0,
            uid integer DEFAULT 0,
            username text COLLATE pg_catalog."default" DEFAULT ''::text,
            created timestamp without time zone DEFAULT now(),
            priority text COLLATE pg_catalog."default" DEFAULT ''::text,
            operationtype text COLLATE pg_catalog."default" DEFAULT ''::text,
            itemoid text COLLATE pg_catalog."default" DEFAULT ''::text,
            finished timestamp without time zone DEFAULT now(),
            timeoperation numeric(19,4) DEFAULT 0.0,
            status text COLLATE pg_catalog."default" DEFAULT ''::text,
            CONSTRAINT cmschapteroperation_pkey PRIMARY KEY (_oid)
         ) WITH ( OIDS = FALSE ) TABLESPACE pg_default;
         ALTER TABLE icor.cmschapteroperation OWNER to %(PGUser)s;
         COMMENT ON TABLE icor.cmschapteroperation IS 'cms chapters';
         CREATE INDEX IF NOT EXISTS i_icor_cmschapteroperation_chapterid ON icor.cmschapteroperation USING btree (chapterid) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapteroperation_created ON icor.cmschapteroperation USING btree (created) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapteroperation_itemoid ON icor.cmschapteroperation USING btree (itemoid COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapteroperation_operationtype ON icor.cmschapteroperation USING btree (operationtype COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapteroperation_priority ON icor.cmschapteroperation USING btree (priority COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapteroperation_status ON icor.cmschapteroperation USING btree (status COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapteroperation_timeoperation ON icor.cmschapteroperation USING btree (timeoperation) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapteroperation_uid ON icor.cmschapteroperation USING btree (uid) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapteroperation_username ON icor.cmschapteroperation USING btree (username COLLATE pg_catalog."default") TABLESPACE pg_default;

         CREATE TABLE IF NOT EXISTS icor.cmschapterstate
         (
            _oid character(32) COLLATE pg_catalog."default" NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
            chapterid integer DEFAULT 0,
            title text COLLATE pg_catalog."default" DEFAULT ''::text,
            cmsid integer DEFAULT 0,
            cmsname text COLLATE pg_catalog."default" DEFAULT ''::text,
            created timestamp without time zone DEFAULT now(),
            priority text COLLATE pg_catalog."default" DEFAULT ''::text,
            operationoid text COLLATE pg_catalog."default" DEFAULT ''::text,
            status text COLLATE pg_catalog."default" DEFAULT ''::text,
            statusauto text COLLATE pg_catalog."default" DEFAULT ''::text,
            CONSTRAINT cmschapterstate_pkey PRIMARY KEY (_oid)
         ) WITH ( OIDS = FALSE) TABLESPACE pg_default;
         ALTER TABLE icor.cmschapterstate OWNER to %(PGUser)s;
         COMMENT ON TABLE icor.cmschapterstate IS 'cms chapters';
         CREATE UNIQUE INDEX IF NOT EXISTS i_icor_cmschapterstate_chapterid ON icor.cmschapterstate USING btree (chapterid) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapterstate_cmsid ON icor.cmschapterstate USING btree (cmsid) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapterstate_cmsname ON icor.cmschapterstate USING btree (cmsname COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapterstate_created ON icor.cmschapterstate USING btree (created) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapterstate_operationoid ON icor.cmschapterstate USING btree (operationoid COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapterstate_priority ON icor.cmschapterstate USING btree (priority COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapterstate_status ON icor.cmschapterstate USING btree (status COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapterstate_statusauto ON icor.cmschapterstate USING btree (statusauto COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmschapterstate_title ON icor.cmschapterstate USING btree (title COLLATE pg_catalog."default") TABLESPACE pg_default;

         CREATE TABLE IF NOT EXISTS icor.cmsdata
         (
            cmsid integer DEFAULT 0,
            name text COLLATE pg_catalog."default" DEFAULT ''::text,
            value text COLLATE pg_catalog."default" DEFAULT ''::text
         ) WITH (OIDS = FALSE) TABLESPACE pg_default;
         ALTER TABLE icor.cmsdata OWNER to %(PGUser)s;
         CREATE INDEX IF NOT EXISTS i_icor_cmsdata_cmsid ON icor.cmsdata USING btree (cmsid) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_cmsdata_cmsid_name ON icor.cmsdata USING btree (cmsid, name COLLATE pg_catalog."default") TABLESPACE pg_default;

         CREATE SEQUENCE IF NOT EXISTS icor.executormethods_meid_seq INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 43462 CACHE 1 NO CYCLE;
         ALTER SEQUENCE icor.executormethods_meid_seq OWNER TO %(PGUser)s;
         GRANT ALL ON SEQUENCE icor.executormethods_meid_seq TO %(PGUser)s;
         CREATE TABLE IF NOT EXISTS icor.executormethods
         (
            meid integer NOT NULL DEFAULT nextval('icor.executormethods_meid_seq'::regclass),
            cid integer DEFAULT 0,
            name text COLLATE pg_catalog."default" DEFAULT ''::text,
            fieldname text COLLATE pg_catalog."default" DEFAULT ''::text,
            oid integer DEFAULT 0,
            value text COLLATE pg_catalog."default" DEFAULT ''::text,
            uid integer DEFAULT 0,
            isparallel integer DEFAULT 0,
            isqueued integer DEFAULT 0,
            eventtime timestamp without time zone DEFAULT now(),
            eventtime_ready timestamp without time zone DEFAULT now(),
            eventtime_deleted timestamp without time zone DEFAULT now(),
            eventtime_working timestamp without time zone DEFAULT now(),
            eventtime_done timestamp without time zone DEFAULT now(),
            status text COLLATE pg_catalog."default" DEFAULT ''::text,
            priority text COLLATE pg_catalog."default" DEFAULT ''::text,
            pid integer DEFAULT 0,
            result text COLLATE pg_catalog."default" DEFAULT ''::text,
            output text COLLATE pg_catalog."default" DEFAULT ''::text,
            CONSTRAINT executormethods_pkey PRIMARY KEY (meid)
         ) WITH (OIDS = FALSE) TABLESPACE pg_default;
         ALTER TABLE icor.executormethods  OWNER to %(PGUser)s;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_cid ON icor.executormethods USING btree (cid) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_eventtime ON icor.executormethods USING btree (eventtime) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_eventtime_deleted ON icor.executormethods USING btree (eventtime_deleted) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_eventtime_done ON icor.executormethods USING btree (eventtime_done) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_eventtime_ready ON icor.executormethods USING btree (eventtime_ready) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_eventtime_working ON icor.executormethods USING btree (eventtime_working) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_fieldname ON icor.executormethods USING btree (fieldname COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_meid ON icor.executormethods USING btree (meid) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_name ON icor.executormethods USING btree (name COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_oid ON icor.executormethods USING btree (oid) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_pid ON icor.executormethods USING btree (pid) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_priority ON icor.executormethods USING btree (priority COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_status ON icor.executormethods USING btree (status COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_executormethods_uid ON icor.executormethods USING btree (uid) TABLESPACE pg_default; 

         CREATE TABLE IF NOT EXISTS icor.semaphores
         (
            name text COLLATE pg_catalog."default" NOT NULL DEFAULT ''::text,
            value integer DEFAULT 1,
            CONSTRAINT semaphores_pkey PRIMARY KEY (name)
         ) WITH (OIDS = FALSE) TABLESPACE pg_default;
         ALTER TABLE icor.semaphores OWNER to %(PGUser)s;
         CREATE INDEX IF NOT EXISTS i_icor_semaphores_name ON icor.semaphores USING btree (name COLLATE pg_catalog."default") TABLESPACE pg_default;


         CREATE TABLE IF NOT EXISTS icor.syncfiles
         (
            _oid character(32) COLLATE pg_catalog."default" NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
            srcpath text COLLATE pg_catalog."default" DEFAULT ''::text,
            dstpath text COLLATE pg_catalog."default" DEFAULT ''::text,
            created timestamp without time zone DEFAULT now(),
            closed timestamp without time zone DEFAULT now(),
            copystart timestamp without time zone DEFAULT now(),
            copyfinish timestamp without time zone DEFAULT now(),
            filesize integer DEFAULT 0,
            firstwrite timestamp without time zone DEFAULT now(),
            writecnt integer DEFAULT 0,
            writemax integer DEFAULT 0,
            timesave numeric(19,4) DEFAULT 0.0,
            timecopy numeric(19,4) DEFAULT 0.0,
            pathpriority text COLLATE pg_catalog."default" DEFAULT ''::text,
            digest text COLLATE pg_catalog."default" DEFAULT ''::text,
            status text COLLATE pg_catalog."default" DEFAULT ''::text,
            statusdelete text COLLATE pg_catalog."default" DEFAULT ''::text,
            CONSTRAINT syncfiles_pkey PRIMARY KEY (_oid)
         ) WITH (OIDS = FALSE) TABLESPACE pg_default;
         ALTER TABLE icor.syncfiles OWNER to %(PGUser)s;
         COMMENT ON TABLE icor.syncfiles IS 'file synchronization';
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_closed ON icor.syncfiles USING btree (closed) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_copyfinish ON icor.syncfiles USING btree (copyfinish) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_copystart ON icor.syncfiles USING btree (copystart) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_created ON icor.syncfiles USING btree (created) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_digest ON icor.syncfiles USING btree (digest COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_dstpath ON icor.syncfiles USING btree (dstpath COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_filesize ON icor.syncfiles USING btree (filesize) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_firstwrite ON icor.syncfiles USING btree (firstwrite) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_pathpriority ON icor.syncfiles USING btree (pathpriority COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_srcpath ON icor.syncfiles USING btree (srcpath COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_status ON icor.syncfiles USING btree (status COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_statusdelete ON icor.syncfiles USING btree (statusdelete COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_timecopy ON icor.syncfiles USING btree (timecopy) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_timesave ON icor.syncfiles USING btree (timesave) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_writecnt ON icor.syncfiles USING btree (writecnt) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfiles_writemax ON icor.syncfiles USING btree (writemax) TABLESPACE pg_default;

         CREATE TABLE IF NOT EXISTS icor.syncfilesarchive
         (
            _oid character(32) COLLATE pg_catalog."default" NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
            srcpath text COLLATE pg_catalog."default" DEFAULT ''::text,
            dstpath text COLLATE pg_catalog."default" DEFAULT ''::text,
            created timestamp without time zone DEFAULT now(),
            closed timestamp without time zone DEFAULT now(),
            copystart timestamp without time zone DEFAULT now(),
            copyfinish timestamp without time zone DEFAULT now(),
            filesize integer DEFAULT 0,
            firstwrite timestamp without time zone DEFAULT now(),
            writecnt integer DEFAULT 0,
            writemax integer DEFAULT 0,
            timesave numeric(19,4) DEFAULT 0.0,
            timecopy numeric(19,4) DEFAULT 0.0,
            pathpriority text COLLATE pg_catalog."default" DEFAULT ''::text,
            digest text COLLATE pg_catalog."default" DEFAULT ''::text,
            status text COLLATE pg_catalog."default" DEFAULT ''::text,
            statusdelete text COLLATE pg_catalog."default" DEFAULT ''::text,
            CONSTRAINT syncfilesarchive_pkey PRIMARY KEY (_oid)
         ) WITH (OIDS = FALSE) TABLESPACE pg_default;
         ALTER TABLE icor.syncfilesarchive OWNER to %(PGUser)s;
         COMMENT ON TABLE icor.syncfilesarchive IS 'file synchronization';
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_closed ON icor.syncfilesarchive USING btree (closed) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_copyfinish ON icor.syncfilesarchive USING btree (copyfinish) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_copystart ON icor.syncfilesarchive USING btree (copystart) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_created ON icor.syncfilesarchive USING btree (created) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_digest ON icor.syncfilesarchive USING btree (digest COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_dstpath ON icor.syncfilesarchive USING btree (dstpath COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_filesize ON icor.syncfilesarchive USING btree (filesize) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_firstwrite ON icor.syncfilesarchive USING btree (firstwrite) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_pathpriority ON icor.syncfilesarchive USING btree (pathpriority COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_srcpath ON icor.syncfilesarchive USING btree (srcpath COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_status ON icor.syncfilesarchive USING btree (status COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_statusdelete ON icor.syncfilesarchive USING btree (statusdelete COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_timecopy ON icor.syncfilesarchive USING btree (timecopy) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_timesave ON icor.syncfilesarchive USING btree (timesave) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_writecnt ON icor.syncfilesarchive USING btree (writecnt) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncfilesarchive_writemax ON icor.syncfilesarchive USING btree (writemax) TABLESPACE pg_default;

         CREATE TABLE IF NOT EXISTS icor.syncpaths
         (
            _oid character(32) COLLATE pg_catalog."default" NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
            dstpath text COLLATE pg_catalog."default" DEFAULT ''::text,
            pathlevel integer DEFAULT 0,
            digest text COLLATE pg_catalog."default" DEFAULT ''::text,
            digestcopied text COLLATE pg_catalog."default" DEFAULT ''::text,
            pathpriority text COLLATE pg_catalog."default" DEFAULT ''::text,
            srcoid text COLLATE pg_catalog."default" DEFAULT ''::text,
            status text COLLATE pg_catalog."default" DEFAULT ''::text,
            created timestamp without time zone DEFAULT now(),
            CONSTRAINT syncpaths_pkey PRIMARY KEY (_oid)
         ) WITH (OIDS = FALSE) TABLESPACE pg_default;
         ALTER TABLE icor.syncpaths OWNER to %(PGUser)s;
         COMMENT ON TABLE icor.syncpaths IS 'file synchronization';
         CREATE INDEX IF NOT EXISTS i_icor_syncpaths_created ON icor.syncpaths USING btree (created) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncpaths_digest ON icor.syncpaths USING btree (digest COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncpaths_digestcopied ON icor.syncpaths USING btree (digestcopied COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE UNIQUE INDEX IF NOT EXISTS i_icor_syncpaths_dstpath ON icor.syncpaths USING btree (dstpath COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncpaths_pathlevel ON icor.syncpaths USING btree (pathlevel) TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncpaths_pathpriority ON icor.syncpaths USING btree (pathpriority COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncpaths_srcoid ON icor.syncpaths USING btree (srcoid COLLATE pg_catalog."default") TABLESPACE pg_default;
         CREATE INDEX IF NOT EXISTS i_icor_syncpaths_status ON icor.syncpaths USING btree (status COLLATE pg_catalog."default") TABLESPACE pg_default;
      ''' % d

        bsql = '''
         CREATE TABLE IF NOT EXISTS data_main2.alldata
         (
            _oid text COLLATE pg_catalog."default" NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
            c integer DEFAULT 0,
            o integer DEFAULT 0,
            u integer DEFAULT 0,
            l timestamp without time zone DEFAULT now(),
            s integer DEFAULT 0,
            v jsonb DEFAULT '{}'::jsonb,
            CONSTRAINT alldata_pkey PRIMARY KEY (_oid)
         );

         CREATE INDEX IF NOT EXISTS i_icor_alldata_c ON data_main2.alldata USING btree (c);
         CREATE INDEX IF NOT EXISTS i_icor_alldata_o ON data_main2.alldata USING btree (o);
         CREATE unique INDEX IF NOT EXISTS i_icor_alldata_co ON data_main2.alldata USING btree (c, o);
         CREATE INDEX IF NOT EXISTS i_icor_alldata_u ON data_main2.alldata USING btree (u);
         CREATE INDEX IF NOT EXISTS i_icor_alldata_l ON data_main2.alldata USING btree (l);
         CREATE INDEX IF NOT EXISTS i_icor_alldata_s ON data_main2.alldata USING btree (s);
         CREATE INDEX IF NOT EXISTS i_icor_alldata_v ON data_main2.alldata USING GIN (v);

         CREATE TABLE IF NOT EXISTS data_main2.alldatav
         (
            i serial PRIMARY KEY,
            _oid text DEFAULT ''::text,
            c integer DEFAULT 0,
            o integer DEFAULT 0,
            u integer DEFAULT 0,
            l timestamp without time zone DEFAULT now(),
            a text DEFAULT ''::text,
            s integer DEFAULT 0,
            v jsonb DEFAULT '{}'::jsonb
         );

         CREATE INDEX IF NOT EXISTS i_icor_alldatav_oid ON data_main2.alldatav USING btree (_oid);
         CREATE INDEX IF NOT EXISTS i_icor_alldatav_c ON data_main2.alldatav USING btree (c);
         CREATE INDEX IF NOT EXISTS i_icor_alldatav_o ON data_main2.alldatav USING btree (o);
         CREATE INDEX IF NOT EXISTS i_icor_alldatav_cos ON data_main2.alldatav USING btree (c, o, s desc);
         CREATE INDEX IF NOT EXISTS i_icor_alldatav_u ON data_main2.alldatav USING btree (u);
         CREATE INDEX IF NOT EXISTS i_icor_alldatav_l ON data_main2.alldatav USING btree (l);
         CREATE INDEX IF NOT EXISTS i_icor_alldatav_a ON data_main2.alldatav USING btree (a);
         CREATE INDEX IF NOT EXISTS i_icor_alldatav_s ON data_main2.alldatav USING btree (s);
         CREATE INDEX IF NOT EXISTS i_icor_alldatav_v ON data_main2.alldatav USING GIN (v);

         -- function trigger
         DROP TRIGGER IF EXISTS tr_alldata_insert ON data_main2.alldata;
         DROP TRIGGER IF EXISTS tr_alldata_update ON data_main2.alldata;
         DROP TRIGGER IF EXISTS tr_alldata_delete ON data_main2.alldata;
         DROP FUNCTION IF EXISTS data_main2.tr_alldata_insert() CASCADE;
         DROP FUNCTION IF EXISTS data_main2.tr_alldata_update() CASCADE;
         DROP FUNCTION IF EXISTS data_main2.tr_alldata_delete() CASCADE;

         CREATE OR REPLACE FUNCTION data_main2.tr_alldata_insert() RETURNS TRIGGER AS
         $BODY$
         BEGIN
            INSERT into data_main2.alldatav(_oid,c,o,u,l,a,s,v) VALUES(new._oid,new.c,new.o,new.u,new.l,'insert',new.s,new.v);
            RETURN new;
         END;
         $BODY$
         language plpgsql;

         CREATE OR REPLACE FUNCTION data_main2.tr_alldata_update() RETURNS TRIGGER AS
         $BODY$
         BEGIN
            INSERT into data_main2.alldatav(_oid,c,o,u,l,a,s,v) VALUES(new._oid,new.c,new.o,new.u,new.l,'update',new.s,new.v);
            RETURN new;
         END;
         $BODY$
         language plpgsql;

         CREATE OR REPLACE FUNCTION data_main2.tr_alldata_delete() RETURNS TRIGGER AS
         $BODY$
         BEGIN
            INSERT into data_main2.alldatav(_oid,c,o,u,a,s,v) VALUES(old._oid,old.c,old.o,old.u,'delete',old.s,old.v);
            RETURN old;
         END;
         $BODY$
         language plpgsql;

         -- insert trigger

         CREATE TRIGGER tr_alldata_insert AFTER INSERT ON data_main2.alldata FOR EACH row EXECUTE PROCEDURE data_main2.tr_alldata_insert();

         CREATE TRIGGER tr_alldata_update AFTER UPDATE ON data_main2.alldata FOR EACH row EXECUTE PROCEDURE data_main2.tr_alldata_update();

         CREATE TRIGGER tr_alldata_delete BEFORE DELETE ON data_main2.alldata FOR EACH row EXECUTE PROCEDURE data_main2.tr_alldata_delete();
      '''
        asql = asql + bsql.replace('data_main2', self.db.GetConfigValue('PGSchema'))
        if asqlonly:
            return asql
        cur = self.db.GetCursor()
        try:
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return asql

    ### Utils
    def GetCorrectPath(self, s, aappendslash=1):
        s = s.replace('/', '\\')
        s = s.replace('_', '\\')
        if aappendslash:
            if s[-1:] != '\\':
                s = s + '\\'
        else:
            if s[-1:] == '\\':
                s = s[:-1]
        return s

    ### Data structures:
    def CreateField(self, afid, aDefaultTypeID, aDefaultTypeModifier, aschema=None, asqlonly=0):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.CreateField')

    def CreateClass(self, acid, aschema='', asqlonly=1):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.CreateClass')

    ### Obsluga wartosci
    def UpdateFieldValue(self, afid, aoid, auid, alastmodification, avalue):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.UpdateFieldValue')

    def UpdateClassOID(self, cid, aoid, auid, alastmodification):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.UpdateClassOID')

    def ClearClassObjects(self, cid, aschema):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.ClearClassObjects')

    def GetRepositoryStruct(self, aschema=None):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.GetRepositoryStruct')

    def GetFIDByCIDFieldname(self, acid, afieldname, aschema=None):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.GetFIDByCIDFieldname')

    def GetFieldValuesAsDict(self, afid, aschema=None):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.GetFieldValuesAsDict')

    def GetFieldOIDsAsList(self, afid, aschema=None):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.GetFieldOIDsAsList')

    ### Zarzadzanie tabelami
    def GetSchemaTablesList(self, aschema=None):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.GetSchemaTablesList')

    def DeleteSchemaTables(self, aschema=None, asqlonly=1):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.DeleteSchemaTables')

    def GetFieldTablesList(self):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.GetFieldTablesList')

    def GetFieldIDList(self):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.GetFieldIDList')

    def CheckFieldTables(self):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.CheckFieldTables')

    def RemoveFieldTables(self, afid):
        raise icorexceptions.ICORExceptionDBStructObsolete('dbstruct.RemoveFieldTables')

    ### All Data
    def AllData_GetValueDictFromJSON(self, djson, fields=None, autfconvert=1):
        d = {}
        for k, v in djson.items():
            if k[:1] == 'v':
                k = k[1:]
                if autfconvert:
                    k = storageutil.UTF8_To_CP1250(k)
                if (fields is None) or (k in fields):
                    if autfconvert and isinstance(v, types.StringTypes):
                        v = storageutil.UTF8_To_CP1250(v)
                    d[k] = v
        return d

    def AllData_UpdateObject(self, cid, aoid, auid, alastmodification=None, avalue=None):
        if (type(alastmodification) in [type([]), type(())]) or (not alastmodification):
            adt = storageutil.tdatetime2fmtstr(alastmodification)
        else:
            adt = alastmodification
        if not avalue:
            avalue = {}
        ret = ''
        cur = self.db.GetCursor()
        try:
            asql = '''
            INSERT INTO %s.alldata as t1 (c,o,u,l,v)
            VALUES (%%s,%%s,%%s,%%s,%%s)
            ON CONFLICT (c,o) DO UPDATE SET u=EXCLUDED.u, l=greatest(t1.l,EXCLUDED.l), v=t1.v || EXCLUDED.v returning _oid;
         ''' % (self.db.schema, )
            cur.execute(asql, (cid, aoid, auid, adt, Json(avalue)))
            res = cur.fetchall()
            if res:
                ret = storageutil.UTF8_To_CP1250(res[0][0])
        finally:
            self.db.CloseCursor(cur)
        return ret

    ### ICOR API
    def API_ClassExists(self, UID, acid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        akey = (aschema, acid)
        if self._cid2cdata.has_key(akey):
            return self._cid2cdata[akey][0]
        ret = -1, '', {}
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s and o=%%s;
         ''' % (aschema, )
            cur.execute(asql, (CLASSES_System_ICORClass, acid, ))
            ret = cur.rowcount
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetClassID(self, UID, astr, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        dtypes={
           'string':storageutil.mt_String,
           'integer':storageutil.mt_Integer,
           'bool':storageutil.mt_Boolean,
           'boolean':storageutil.mt_Boolean,
           'datetime':storageutil.mt_DateTime,
           'date':storageutil.mt_DateTime,
           'time':storageutil.mt_DateTime,
           'double':storageutil.mt_Double,
        } # yapf: disable
        if dtypes.has_key(astr):
            return dtypes[astr]

        ret = dtypes.get(astr.lower(), -1)
        if ret >= 0:
            return ret
        astr = self.GetCorrectPath(astr, aappendslash=0)
        l = astr.split('\\')
        abasepath = '\\'.join(l[:-1])
        aclassname = l[-1]
        cid = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s and v @>%%s;
         ''' % (aschema, )
            dsearch = {'iaBasePath': abasepath.lower(), 'iaClassName': aclassname.lower()}
            cur.execute(asql, (CLASSES_System_ICORClass, Json(dsearch)))
            res = cur.fetchall()
            if res:
                cid = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return cid

    def API_GetFieldValue(self, UID, cid, fname, oid, aschema=None, afid=-1, alldata=PG_FIELDS, adefault=None):
        if aschema is None:
            aschema = self.db.schema
        if adefault is not None:
            ret = adefault
        else:
            ret = ''
        cur = self.db.GetCursor()
        try:
            asql = '''
            select coalesce(v->>'v%s',%%s) from %s.alldata where c=%%s and o=%%s;
         ''' % (fname, aschema, )
            cur.execute(asql, (ret, cid, oid, ))
            res = cur.fetchall()
            if res:
                ret = storageutil.UTF8_To_CP1250(res[0][0])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldValueInt(self, UID, cid, fname, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = 0
        cur = self.db.GetCursor()
        try:
            asql = '''
            select coalesce((v->'v%s')::integer,0) from %s.alldata where c=%%s and o=%%s;
         ''' % (fname, aschema, )
            cur.execute(asql, (cid, oid, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldValueFloat(self, UID, cid, fname, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = 0.0
        cur = self.db.GetCursor()
        try:
            asql = '''
            select coalesce((v->'v%s')::numeric(26,12),0) from %s.alldata where c=%%s and o=%%s;
         ''' % (fname, aschema, )
            cur.execute(asql, (cid, oid, ))
            res = cur.fetchall()
            if res:
                ret = float(res[0][0])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldValueDateTime(self, UID, cid, fname, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = [1899, 12, 30, 0, 0, 0, 0]
        cur = self.db.GetCursor()
        try:
            asql = '''
            select coalesce(v->>'v%s','') from %s.alldata where c=%%s and o=%%s;
         ''' % (fname, aschema, )
            cur.execute(asql, (cid, oid, ))
            res = cur.fetchall()
            if res:
                ret = list(storageutil.getStrAsDateTime(res[0][0]))
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldValueDate(self, UID, cid, fname, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = [1899, 12, 30]
        cur = self.db.GetCursor()
        try:
            asql = '''
            select coalesce(v->>'v%s','') from %s.alldata where c=%%s and o=%%s;
         ''' % (fname, aschema, )
            cur.execute(asql, (cid, oid, ))
            res = cur.fetchall()
            if res:
                ret = list(storageutil.getStrAsDate(res[0][0]))
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldValueTime(self, UID, cid, fname, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = [0, 0, 0, 0]
        cur = self.db.GetCursor()
        try:
            asql = '''
            select coalesce(v->>'v%s','') from %s.alldata where c=%%s and o=%%s;
         ''' % (fname, aschema, )
            cur.execute(asql, (cid, oid, ))
            res = cur.fetchall()
            if res:
                ret = list(storageutil.getStrAsTimeL(res[0][0]))
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldValuePyTime(self, UID, cid, fname, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = [1899, 12, 30, 0, 0, 0, 5, 364, -1]
        cur = self.db.GetCursor()
        try:
            asql = '''
            select EXTRACT(YEAR FROM coalesce(v->>'v%s','1899-12-30')::timestamp)::integer y,EXTRACT(MONTH FROM coalesce(v->>'v%s','1899-12-30')::timestamp)::integer m,EXTRACT(DAY FROM coalesce(v->>'v%s','1899-12-30')::timestamp)::integer d,EXTRACT(HOUR FROM coalesce(v->>'v%s','1899-12-30')::timestamp)::integer hh,EXTRACT(MINUTE FROM coalesce(v->>'v%s','1899-12-30')::timestamp)::integer mm,EXTRACT(SECOND FROM coalesce(v->>'v%s','1899-12-30')::timestamp)::integer ss,EXTRACT(ISODOW FROM coalesce(v->>'v%s','1899-12-30')::timestamp)::integer-1 dow,EXTRACT(DOY FROM coalesce(v->>'v%s','1899-12-30')::timestamp)::integer doy from %s.alldata where c=%%s and o=%%s;
         ''' % (fname, fname, fname, fname, fname, fname, fname, fname, aschema,
                )
            cur.execute(asql, (cid, oid, ))
            res = cur.fetchall()
            if res:
                ret = [res[0][0], res[0][1], res[0][2], res[0][3], res[0][4], res[0][5], res[0][6], res[0][7], -1]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldValueLastModification(self, UID, cid, fname, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = [1899, 12, 30, 0, 0, 0, 0]
        cur = self.db.GetCursor()
        try:
            asql = '''
            select EXTRACT(YEAR FROM coalesce(v->>'l%s','1899-12-30')::timestamp)::integer y,EXTRACT(MONTH FROM coalesce(v->>'l%s','1899-12-30')::timestamp)::integer m,EXTRACT(DAY FROM coalesce(v->>'l%s','1899-12-30')::timestamp)::integer d,EXTRACT(HOUR FROM coalesce(v->>'l%s','1899-12-30')::timestamp)::integer hh,EXTRACT(MINUTE FROM coalesce(v->>'l%s','1899-12-30')::timestamp)::integer mm,EXTRACT(SECOND FROM coalesce(v->>'l%s','1899-12-30')::timestamp)::integer ss from %s.alldata where c=%%s and o=%%s;
         ''' % (fname, fname, fname, fname, fname, fname, aschema,
                )
            cur.execute(asql, (cid, oid, ))
            res = cur.fetchall()
            if res:
                ret = [res[0][0], res[0][1], res[0][2], res[0][3], res[0][4], res[0][5], 0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_ValueExists(self, UID, cid, fname, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = 0
        cur = self.db.GetCursor()
        try:
            asql = '''
            select (v ? 'v%s')::int from %s.alldata where c=%%s and o=%%s;
         ''' % (fname, aschema, )
            cur.execute(asql, (cid, oid, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_ObjectExists(self, UID, cid, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s and o=%%s;
         ''' % (aschema, )
            cur.execute(asql, (cid, oid, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetObjectCount(self, UID, cid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        if not self.API_ClassExists(UID, cid, aschema):
            return -1
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select count(*) from %s.alldata where c=%%s;
         ''' % (aschema, )
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFirstObjectID(self, UID, cid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s order by o limit 1;
         ''' % (aschema, )
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetLastObjectID(self, UID, cid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s order by o desc limit 1;
         ''' % (aschema, )
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetNextObjectID(self, UID, cid, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s and o>=%%s order by o limit 2;
         ''' % (aschema, )
            cur.execute(asql, (cid, oid))
            res = cur.fetchall()
            if (len(res) == 2) and (res[0][0] == oid):
                ret = res[1][0]
            if (len(res) >= 1) and (res[0][0] != oid):
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetPrevObjectID(self, UID, cid, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s and o<=%%s order by o desc limit 2;
         ''' % (aschema, )
            cur.execute(asql, (cid, oid))
            res = cur.fetchall()
            if (len(res) == 2) and (res[0][0] == oid):
                ret = res[1][0]
            elif (len(res) >= 1) and (res[0][0] != oid):
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFirstFieldValueID(self, UID, cid, fname, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s order by v->>'i%s',o limit 1;
         ''' % (aschema, fname)
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetLastFieldValueID(self, UID, cid, fname, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s order by v->>'i%s' desc,o desc limit 1;
         ''' % (aschema, fname)
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetNextFieldValueID(self, UID, cid, fname, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s and v->>'i%s' > (select v->>'i%s' from %s.alldata where c=%%s and o=%%s) order by v->>'i%s',o limit 1;
         ''' % (aschema, fname, fname, aschema, fname)
            cur.execute(asql, (cid, cid, oid))
            res = cur.fetchall()
            if (len(res) == 1):
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetPrevFieldValueID(self, UID, cid, fname, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s and v->>'i%s' < (select v->>'i%s' from %s.alldata where c=%%s and o=%%s) order by v->>'i%s',o limit 1;
         ''' % (aschema, fname, fname, aschema, fname)
            cur.execute(asql, (cid, cid, oid))
            res = cur.fetchall()
            if (len(res) == 1):
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetObjectIDByPosition(self, UID, cid, apos, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select nth_value(o, %d+1) over (order by c,o) as o2 from %s.alldata where c=%%s order by c,o desc limit 1;
         ''' % (apos, aschema, )
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
            if ret is None:
                ret = -1
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetValueIDByPosition(self, UID, cid, fname, apos, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select nth_value(o, %d+1) over (order by c,v->'i%s',o) as o2 from %s.alldata where c=%%s order by c,v->'i%s' desc, o desc limit 1;
         ''' % (apos, fname, aschema, fname, )
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
            if ret is None:
                ret = -1
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldValueByPosition(self, UID, cid, fname, apos, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = ''
        cur = self.db.GetCursor()
        try:
            asql = '''
            select coalesce(v->>'v%s','') from %s.alldata where c=%%s order by c,v->>'i%s',o offset %%s limit 1;
         ''' % (fname, aschema, fname, )
            cur.execute(asql, (cid, apos))
            res = cur.fetchall()
            if res:
                ret = storageutil.UTF8_To_CP1250(res[0][0])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldObjectsCount(self, UID, cid, fname, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = 0
        cur = self.db.GetCursor()
        try:
            asql = '''
            select count(*) as cnt from %s.alldata where c=%%s;
         ''' % (aschema, )
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_IsObjectDeleted(self, UID, cid, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select tv.o as o1
            from %s.alldatav tv
            left join %s.alldata tc on tc.c=tv.c and tc.o=tv.o
            where tv.o=%%s and tc.o is null
            limit 1;
         ''' % (aschema, aschema, )
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldsList(self, UID, cid, aschema=None, alldata=PG_FIELDS, aslist=0, asfielddata=0):
        if aschema is None:
            aschema = self.db.schema
        ret = ''
        retl = []
        cur = self.db.GetCursor()
        try:
            asql = '''
            select coalesce(v->>'vaFields','') from %s.alldata where c=%%s and o=%%s;
         ''' % (aschema, )
            cur.execute(asql, (CLASSES_System_ICORClass, cid, ))
            res = cur.fetchall()
            if res and res[0][0]:
                arefs = dbclasses.FieldRefIterator(storageutil.UTF8_To_CP1250(res[0][0]))
                lfids = []
                for afid, acid in arefs.refs:
                    if not self._fid2fieldnamecid.has_key((aschema, afid)):
                        lfids.append(str(afid))
                if lfids:
                    cur = self.db.GetCursor(cur)
                    asql = '''
                  select o,v->>'vaFieldName',v from %s.alldata where c=%%s and o in (%s);
               ''' % (aschema, ','.join(lfids))
                    cur.execute(asql, (CLASSES_System_ICORField, ))
                    res = cur.fetchall()
                    for arec in res:
                        afname = storageutil.UTF8_To_CP1250(arec[1])
                        self._fid2fieldnamecid[(aschema, arec[0])] = afname, cid
                        self._cidfieldname2fdata[(aschema, cid, afname)] = arec[0], arec[1], arec[2]
                        self._fid2data[(aschema, arec[0])] = arec[2]
                for afid, acid in arefs.refs:
                    if asfielddata:
                        fdata = self._fid2data[aschema, afid]
                        retl.append(fdata)
                    else:
                        bfname, bcid = self._fid2fieldnamecid[aschema, afid]
                        retl.append(bfname)
                if not asfielddata:
                    ret = ':'.join(retl)
                    if ret:
                        ret = ret + ':'
        finally:
            self.db.CloseCursor(cur)
        if aslist or asfielddata:
            return retl
        return ret

    def API_GetFirstClass(self, UID, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s order by c,o limit 1;
         ''' % (aschema, )
            cur.execute(asql, (CLASSES_System_ICORClass, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetNextClass(self, UID, cid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s and o>=%%s order by c,o limit 2;
         ''' % (aschema, )
            cur.execute(asql, (CLASSES_System_ICORClass, cid))
            res = cur.fetchall()
            if (len(res) == 2) and (res[0][0] == cid):
                ret = res[1][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldNextValue(self, UID, cid, fname, fvalue, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        fvalue = storageutil.CP1250_To_UTF8(fvalue)
        ret = (-1, '', {})
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o,coalesce(v->>'v%s','') as vv,v from %s.alldata where c=%%s
            and v->>'v%s'>%%s
            order by v->>'i%s',o limit 1
            ;
         ''' % (fname, aschema, fname, fname)
            cur.execute(asql, (cid, fvalue, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0], storageutil.UTF8_To_CP1250(res[0][1]), self.AllData_GetValueDictFromJSON(res[0][2])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldPrevValue(self, UID, cid, fname, fvalue, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        fvalue = storageutil.CP1250_To_UTF8(fvalue)
        ret = (-1, '', {})
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o,coalesce(v->>'v%s','') as vv,v from %s.alldata where c=%%s
            and v->>'v%s'<%%s
            order by v->>'i%s' desc,o limit 1
            ;
         ''' % (fname, aschema, fname, fname)
            cur.execute(asql, (cid, fvalue, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0], storageutil.UTF8_To_CP1250(res[0][1]), self.AllData_GetValueDictFromJSON(res[0][2])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldNextValueInt(self, UID, cid, fname, fvalue, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = (-1, '', {})
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o,coalesce((v->'v%s')::integer,-1) as vv,v from %s.alldata where c=%%s
            and (v->'v%s')::integer>%%s
            order by (v->'v%s')::integer,o limit 1
            ;
         ''' % (fname, aschema, fname, fname)
            cur.execute(asql, (cid, fvalue, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0], res[0][1], self.AllData_GetValueDictFromJSON(res[0][2])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldPrevValueInt(self, UID, cid, fname, fvalue, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = (-1, '', {})
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o,coalesce((v->'v%s')::integer,-1) as vv,v from %s.alldata where c=%%s
            and (v->'v%s')::integer<%%s
            order by (v->'v%s')::integer desc,o limit 1
            ;
         ''' % (fname, aschema, fname, fname)
            cur.execute(asql, (cid, fvalue, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0], res[0][1], self.AllData_GetValueDictFromJSON(res[0][2])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_FindValue(self, UID, cid, fname, fvalue, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        fvalue = storageutil.CP1250_To_UTF8(fvalue)
        aoid = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s and coalesce(v->>'i%s','')=lower(left(%%s,500)) order by o limit 1;
         ''' % (aschema, fname)
            cur.execute(asql, (cid, fvalue, ))
            res = cur.fetchall()
            if res:
                aoid = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return aoid

    def API_FindValueMulti(self, UID, cid, values, mode=0, aschema=None):
        if aschema is None:
            aschema = self.db.schema
        ret = []
        ls, lp = [], []
        for akey, avalue in values.items():
            avalue = storageutil.CP1250_To_UTF8(avalue)
            ls.append(" coalesce(v->>'i%s','')=lower(left(%%s,500)) " % akey)
            lp.append(avalue)
        cur = self.db.GetCursor()
        try:
            sw = ' and '.join(ls)
            asql = '''
            select o from %s.alldata where c=%%s and %s order by o;
         ''' % (aschema, sw)
            cur.execute(asql, (cid, ) + tuple(lp))
            res = cur.fetchall()
            for rec in res:
                ret.append(rec[0])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_FindValueBoolean(self, UID, cid, fname, fvalue, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        if fvalue:
            fvalue = 1
        else:
            fvalue = 0
        aoid = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s and (v->>'v%s')::boolean=%d::boolean order by o limit 1;
         ''' % (aschema, fname, fvalue)
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            if res:
                aoid = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return aoid

    def API_FindValueDateTime(self, UID, cid, fname, i1, i2, i3, i4, i5, i6, i7, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        aoid = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s and coalesce(v->>'v%s','')='%04d-%02d-%02d %02d:%02d:%02d' order by o limit 1;
         ''' % (aschema, fname, i1, i2, i3, i4, i5, i6)
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            if res:
                aoid = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return aoid

    def API_FindValueFloat(self, UID, cid, fname, fvalue, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        aoid = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s and (v->'v%s')::numeric(26,12)=%f::numeric(26,12) order by o limit 1;
         ''' % (aschema, fname, fvalue)
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            if res:
                aoid = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return aoid

    def API_FindValueInteger(self, UID, cid, fname, fvalue, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        aoid = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o from %s.alldata where c=%%s and (v->'v%s')::integer=%f order by o limit 1;
         ''' % (aschema, fname, fvalue)
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            if res:
                aoid = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return aoid

    def API_GetFieldOIDsBySearchValue(self, UID, cid, fname, value, acasesensitive=0, aregexp=0, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = set()
        cur = self.db.GetCursor()
        try:
            value = storageutil.CP1250_To_UTF8(value)
            if aregexp:
                if acasesensitive:
                    asql = '''SELECT o FROM %s.alldata where c=%d and coalesce(v->>'v%s','') ~ %%s;''' % (aschema, cid, fname)
                else:
                    asql = '''SELECT o FROM %s.alldata where c=%d and coalesce(v->>'v%s','') ~* %%s;''' % (aschema, cid, fname)
            else:
                value = value.replace('%', '%%')
                value = '%' + value + '%'
                if acasesensitive:
                    asql = '''SELECT o FROM %s.alldata where c=%d and coalesce(v->>'v%s','') like %%s;''' % (aschema, cid, fname)
                else:
                    asql = '''SELECT o FROM %s.alldata where c=%d and coalesce(v->>'v%s','') ilike %%s;''' % (aschema, cid, fname)
            try:
                cur.execute(asql, (value, ))
                res = cur.fetchall()
                for rec in res:
                    ret.add(rec[0])
            except Exception, e:
                if e.pgcode == '42P01':    #relacja "aschema.afid" nie istnieje
                    pass
                else:
                    print 'SQL ERROR: API_GetFieldOIDsBySearchValue - ', e.pgcode
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_CompareOIDs(self, UID, cid, fname, aoid1, aoid2, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            with cte_t1 as (
               select o,v->'%s' as v1 from %s.alldata where c=%%s and o=%%s
            ), cte_t2 as (
               select o,v->'%s' as v1 from %s.alldata where c=%%s and o=%%s
            )
            select
               case
                  when jsonb_typeof(cte_t1.v1)='string' then
                     case
                        when lower(cte_t1.v1::text)<lower(cte_t2.v1::text) then -1
                        when lower(cte_t1.v1::text)>lower(cte_t2.v1::text) then 1
                        else 0
                     end
                  else
                     case
                        when cte_t1.v1<cte_t2.v1 then -1
                        when cte_t1.v1>cte_t2.v1 then 1
                        else 0
                     end
               end as result
            from cte_t1,cte_t2;
         ''' % (fname, aschema, fname, aschema)
            cur.execute(asql, (cid, aoid1, cid, aoid2, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_CompareOIDValue(self, UID, cid, fname, aoid, avalue, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        cur = self.db.GetCursor()
        try:
            avalue = storageutil.CP1250_To_UTF8(avalue)
            asql = '''
            with cte_t1 as (
               select o,coalesce(v->>'v%s','') as v1,%%s::text as vc from %s.alldata where c=%%s and o=%%s
            )
            select
               case
                  when lower(cte_t1.v1::text)<lower(cte_t1.vc::text) then -1
                  when lower(cte_t1.v1::text)>lower(cte_t1.vc::text) then 1
                  else 0
               end as result
            from cte_t1;
         ''' % (fname, aschema, )
            cur.execute(asql, (avalue, cid, aoid))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetMethodsList(self, UID, cid, ainherited, aschema=None, alldata=PG_FIELDS, asset=0):
        if aschema is None:
            aschema = self.db.schema
        ret = ''
        rets = set()
        cur = self.db.GetCursor()
        try:
            asql = '''
            WITH RECURSIVE classlist AS (
               select c,o,v->>'vaClassName' as vaClassName,(v->'vaBaseCID')::integer as vaBaseCID,(v->>'vaMethods')::text as vaMethods, 0 as rlevel
                  from %s.alldata
                  where c=%%s and o=%%s
         ''' % (aschema, )
            if ainherited:
                asql += '''
               UNION ALL
               SELECT e.c, e.o, e.v->>'vaClassName' as vaClassName,(e.v->'vaBaseCID')::integer as vaBaseCID,(e.v->>'vaMethods')::text as vaMethods,mtree.rlevel+1 as rlevel 
                  FROM %s.alldata e
               INNER JOIN classlist mtree ON e.c=mtree.c and e.o=mtree.vaBaseCID
            ''' % (aschema, )
            asql += '''
            ), methods as (
               SELECT s.moid::integer, rlevel
               from
                  (SELECT * FROM classlist) t1,
                  unnest(string_to_array(t1.vaMethods,':%d:')) s(moid)
               where moid<>''
            )
            select t1.c,t1.o,t1.v->>'vaMethodName' as vaMethodName,tr.rlevel
               from %s.alldata t1
               inner join methods tr on t1.c=%d and t1.o=tr.moid
               where t1.c=%d
               order by t1.c,tr.rlevel,vaMethodName,t1.o;
         ''' % (CLASSES_System_ICORMethod, aschema, CLASSES_System_ICORMethod, CLASSES_System_ICORMethod)
            cur.execute(asql, (CLASSES_System_ICORClass, cid))
            res = cur.fetchall()
            for arec in res:
                amethod = storageutil.UTF8_To_CP1250(arec[2])
                if amethod not in rets:
                    rets.add(amethod)
                    ret += amethod + ':'
        finally:
            self.db.CloseCursor(cur)
        if asset:
            return rets
        return ret

    def API_GetMethodInfo(self, UID, cid, amethodname, aschema=None):
        if aschema is None:
            aschema = self.db.schema
        akey = (aschema, cid, amethodname)
        if self._cidmethodname2mdata.has_key(akey):
            return self._cidmethodname2mdata[akey]
        ret = -1, '', {}
        cur = self.db.GetCursor()
        try:
            asql = '''
            WITH RECURSIVE classlist AS (
               select c,o,v->>'vaClassName' as vaClassName,(v->'vaBaseCID')::integer as vaBaseCID,(v->>'vaMethods')::text as vaMethods, 0 as rlevel
                  from %s.alldata
                  where c=%%s and o=%%s
         ''' % (aschema, )
            asql += '''
            UNION ALL
            SELECT e.c, e.o, e.v->>'vaClassName' as vaClassName,(e.v->'vaBaseCID')::integer as vaBaseCID,(e.v->>'vaMethods')::text as vaMethods,mtree.rlevel+1 as rlevel 
               FROM %s.alldata e
            INNER JOIN classlist mtree ON e.c=mtree.c and e.o=mtree.vaBaseCID
         ''' % (aschema, )
            asql += '''
            ), methods as (
               SELECT s.moid::integer, rlevel
               from
                  (SELECT * FROM classlist) t1,
                  unnest(string_to_array(t1.vaMethods,':%d:')) s(moid)
               where moid<>''
            )
            select t1.c,t1.o,t1.v->>'vaMethodName' as vaMethodName,tr.rlevel, t1.v
               from %s.alldata t1
               inner join methods tr on t1.c=%d and t1.o=tr.moid
               where t1.c=%d and v->>'vaMethodName'=%%s
               order by t1.c,tr.rlevel,vaMethodName,t1.o limit 1;
         ''' % (CLASSES_System_ICORMethod, aschema, CLASSES_System_ICORMethod, CLASSES_System_ICORMethod)
            cur.execute(asql, (CLASSES_System_ICORClass, cid, amethodname))
            res = cur.fetchall()
            for arec in res:
                ret = arec[1], storageutil.UTF8_To_CP1250(arec[2]), arec[4]    # mid, mname, v
            self._cidmethodname2mdata[akey] = ret
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetClassInfo(self, UID, cid, aschema=None):
        if aschema is None:
            aschema = self.db.schema
        akey = (aschema, cid)
        if self._cid2cdata.has_key(akey):
            return self._cid2cdata[akey]
        ret = -1, '', {}
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o,v->>'vaClassName' as vaClassName,v from %s.alldata where c=%%s and o=%%s;
         ''' % (aschema, )
            cur.execute(asql, (CLASSES_System_ICORClass, cid))
            res = cur.fetchall()
            for arec in res:
                ret = arec[0], storageutil.UTF8_To_CP1250(arec[1]), arec[2]    # cid, classname, v
            self._cid2cdata[akey] = ret
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldInfo(self, UID, cid, fname, aschema=None):
        if aschema is None:
            aschema = self.db.schema
        akey = (aschema, cid, fname)
        if self._cidfieldname2fdata.has_key(akey):
            return self._cidfieldname2fdata[akey]
        ret = -1, '', {}
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o,v->>'vaFieldName' as vaFieldName,v from %s.alldata where c=%%s and v->>'vaIDClassField'=%%s;
         ''' % (aschema, )
            cur.execute(asql, (CLASSES_System_ICORField, str(cid) + '_' + fname))
            res = cur.fetchall()
            for arec in res:
                ret = arec[0], storageutil.UTF8_To_CP1250(arec[1]), arec[2]    # cid, fieldname, v
            self._cidfieldname2fdata[akey] = ret
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_IsMethodInClass(self, UID, cid, amethodname, aschema=None, alldata=PG_FIELDS):
        rets = self.API_GetMethodsList(UID, cid, 1, aschema=aschema, alldata=alldata, asset=1)
        if amethodname in rets:
            return 1
        return 0

    def API_IsMethodInThisClass(self, UID, cid, amethodname, aschema=None, alldata=PG_FIELDS):
        rets = self.API_GetMethodsList(UID, cid, 0, aschema=aschema, alldata=alldata, asset=1)
        if amethodname in rets:
            return 1
        return 0

    def API_IsFieldInClass(self, UID, cid, afieldname, aschema=None, alldata=PG_FIELDS):
        retl = self.API_GetFieldsList(UID, cid, aschema=aschema, alldata=alldata, aslist=1)
        if afieldname in retl:
            return 1
        return 0

    def API_GetFieldModification(self, UID, cid, fname, oid, aschema=None, alldata=PG_FIELDS):
        v = self.API_GetFieldValueLastModification(UID, cid, fname, oid, aschema=aschema, alldata=alldata)
        return storageutil.tdatetime2fmtstr(v)

    def API_GetObjectModification(self, UID, cid, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = '1899-12-30'
        cur = self.db.GetCursor()
        try:
            asql = '''
            select l::text from %s.alldata where c=%%s and o=%%s;
         ''' % (aschema, )
            cur.execute(asql, (cid, oid, ))
            res = cur.fetchall()
            if res:
                ret = storageutil.UTF8_To_CP1250(res[0][0])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetNextFreeObjectID(self, UID, cid, idmin, idmax, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        aoid = -1
        cur = self.db.GetCursor()
        try:
            asql = '''
            select ts.o as result from (select generate_series(%%s,%%s) as o) ts left join %s.alldata t1 on t1.c=%%s and t1.o=ts.o where t1.o is null order by ts.o limit 1;
         ''' % (aschema, )
            cur.execute(asql, (idmin, idmax, cid))
            res = cur.fetchall()
            if res:
                aoid = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return aoid

    def API_ExecuteMethod(self, UID, cid, aname, afieldname, aoid, avalue, anostringvalue, aschema=None, alldata=PG_FIELDS, acontext=None):
        ret = ''
        amid, amethodname, mdata = self.API_GetMethodInfo(UID, cid, aname, aschema=aschema)
        if amid < 0:
            return ret
            #raise icorexceptions.ICORExceptionAPI('API_ExecuteMethod - method doesnt exists: '+aname)
        acid, aclassname, cdata = self.API_GetClassInfo(UID, cid, aschema=aschema)
        if acid < 0:
            return ret
            #raise icorexceptions.ICORExceptionAPI('API_ExecuteMethod - class doesnt exists: '+str(cid))
        if (mdata.get('vaLanguage', '') in ['', 'Python']) and not mdata.get('vaIsQueued', 0) and not mdata.get('vaIsParallel', 0):
            mname = cdata.get('vaBasePath', '') + '_' + cdata.get('vaClassName', '') + '_' + aname
            mname = mname.replace('\\', '_')
            mname = mname.replace('/', '_')
            amethod = __import__(mname)
            if acontext is None:
                acontext = {}
            amethod.CONTEXT = acontext
            try:
                ret = amethod.ICORMain(cid, afieldname, aoid, avalue, UID)
            except:
                self.mlog.LogException('API_ExecuteMethod: ' + mname + ' afieldname=' + afieldname + ' aoid=' + str(aoid) + ' value=' + avalue[:100])
            return ret
        else:
            ret = self.API_ExecuteMethod(UID, CLASSES_System_ICORClass, 'OnCustomMethodExecuteEvent', str(cid) + ':' + aname + ':' + afieldname, aoid, avalue, anostringvalue, aschema=aschema, alldata=alldata, acontext=acontext)
            if ret is None:
                ret = 'None'
            #raise icorexceptions.ICORExceptionAPI('API_ExecuteMethod - execute not a simple method: '+aname)
        return ret

    def API_SetFieldValue(self, UID, cid, fname, oid, avalue, aschema=None, alldata=PG_FIELDS, amodification=None, adisablechangedevents=0):
        ret = ''
        afid, afieldname, fdata = self.API_GetFieldInfo(UID, cid, fname, aschema=aschema)
        if afid < 0:
            return ret
            #raise icorexceptions.ICORExceptionAPI('API_SetFieldValue - field doesnt exists: '+fname)
        acid, aclassname, cdata = self.API_GetClassInfo(UID, cid, aschema=aschema)
        if acid < 0:
            return ret
            #raise icorexceptions.ICORExceptionAPI('API_SetFieldValue - class doesnt exists: '+str(cid))
        if aschema is None:
            aschema = self.db.schema
        ovalue = self.API_GetFieldValue(UID, cid, fname, oid, aschema=aschema)
        ftid = fdata.get('vaFieldTypeID', -1)
        if ftid > storageutil.MAX_ICOR_SYSTEM_TYPE:
            if type(avalue) == type([]):
                if avalue:
                    if type(avalue[0]) == type(1):
                        avalue = ':'.join(map(repr, avalue) + [''])
                    else:
                        avalue = ''.join(map(lambda x: str(x[0]) + ':' + str(x[1]) + ':', avalue))
                else:
                    avalue = ''
            elif hasattr(avalue, 'AsString'):
                avalue = avalue.AsString()
            oldref = dbclasses.FieldRefIterator(ovalue)
            newref = dbclasses.FieldRefIterator(avalue)
            deletedoids = oldref.oids - newref.oids
            newoids = newref.oids - oldref.oids
            for boid in deletedoids:
                self.API_ExecuteMethod(UID, cid, 'OnObjectLinkChanged', fname, oid, '(0,' + str(boid) + ',' + str(ftid) + ')', 0, aschema=aschema, alldata=alldata)
                self.API_ExecuteMethod(UID, ftid, 'OnObjectRefChanged', fname, boid, '(0,' + str(oid) + ',' + str(cid) + ')', 0, aschema=aschema, alldata=alldata)
            for boid in newoids:
                self.API_ExecuteMethod(UID, cid, 'OnObjectLinkChanged', fname, oid, '(1,' + str(boid) + ',' + str(ftid) + ')', 0, aschema=aschema, alldata=alldata)
                self.API_ExecuteMethod(UID, ftid, 'OnObjectRefChanged', fname, boid, '(1,' + str(oid) + ',' + str(cid) + ')', 0, aschema=aschema, alldata=alldata)
            ivalue = avalue[:500]
        elif ftid in [storageutil.mt_String, storageutil.mt_Memo]:
            if not isinstance(avalue, types.StringTypes):
                avalue = str(avalue)
            avalue = storageutil.CP1250_To_UTF8(avalue)
            ivalue = avalue[:500].decode('utf-8').lower()
        elif ftid in [storageutil.mt_Integer, ]:    # storageutil.mt_SmallInt,storageutil.mt_Byte
            if isinstance(avalue, types.StringTypes):
                avalue = storageutil.getStrAsInt(avalue, 0)
            elif not avalue:
                avalue = 0
            ivalue = str(avalue)
        elif ftid in [storageutil.mt_Double, ]:    #storageutil.mt_Single,storageutil.mt_Currency,storageutil.mt_Extended
            if isinstance(avalue, types.StringTypes):
                avalue = storageutil.getStrAsFloat(avalue)
            elif not avalue:
                avalue = 0.0
            ivalue = str(avalue)
        elif ftid in [storageutil.mt_Boolean, ]:
            if storageutil.str2bool(avalue):
                avalue = True
                ivalue = 'true'
            else:
                avalue = False
                ivalue = 'false'
        elif ftid in [storageutil.mt_DateTime, ]:
            if type(avalue) in [type([]), type(())]:
                avalue = storageutil.tdatetime2fmtstr(avalue)
            elif avalue == '':
                avalue = '1899-12-30'
            else:
                avalue = avalue.replace('/', '-')
                avalue = avalue.replace('\\', '-')
            ivalue = avalue[:500].decode('utf-8').lower()
        else:
            if not isinstance(avalue, types.StringTypes):
                avalue = str(avalue)
            avalue = storageutil.CP1250_To_UTF8(avalue)
            ivalue = avalue[:500].decode('utf-8').lower()

        if avalue != ovalue:
            if not amodification:
                adt = storageutil.tdatetime()
                sdt = storageutil.tdatetime2fmtstr(adt)
            elif type(amodification) in [type([]), type(())]:
                sdt = storageutil.tdatetime2fmtstr(amodification)
            else:
                sdt = amodification.replace('/', '-')
                sdt = sdt.replace('\\', '-')
            dv={
               'v'+fname:avalue,
               'l'+fname:sdt,
               'i'+fname:ivalue,
            } # yapf: disable
            cur = self.db.GetCursor()
            try:
                asql = '''
               INSERT INTO %s.alldata as t1 (c,o,u,l,v)
               VALUES (%%s,%%s,%%s,%%s,%%s)
               ON CONFLICT (c,o) DO UPDATE SET u=EXCLUDED.u, l=greatest(t1.l,EXCLUDED.l), v=t1.v || EXCLUDED.v returning _oid;
            ''' % (aschema, )
                cur.execute(asql, (cid, oid, UID, sdt, Json(dv)))
                res = cur.fetchall()
                if res:
                    ret = storageutil.UTF8_To_CP1250(res[0][0])
            finally:
                self.db.CloseCursor(cur)
            if not adisablechangedevents:
                #LastModified[auid] := adt;
                #ClassItem.UpdateOID(aid, adt, auid);
                self.API_ExecuteMethod(UID, cid, 'OnFieldChange', fname, oid, '', 0, aschema=aschema, alldata=alldata)
        return ret

    def API_SetFieldValueDate(self, UID, cid, fname, oid, yy, mm, dd, aschema=None, alldata=PG_FIELDS, amodification=None, adisablechangedevents=0):
        ret = self.API_SetFieldValue(UID, cid, fname, oid, (yy, mm, dd), aschema=aschema, alldata=alldata, amodification=amodification, adisablechangedevents=adisablechangedevents)
        return ret

    def API_SetFieldValueDateTime(self, UID, cid, fname, oid, yy, mm, dd, ho, mi, se, ms, aschema=None, alldata=PG_FIELDS, amodification=None, adisablechangedevents=0):
        ret = self.API_SetFieldValue(UID, cid, fname, oid, (yy, mm, dd, ho, mi, se, ms), aschema=aschema, alldata=alldata, amodification=amodification, adisablechangedevents=adisablechangedevents)
        return ret

    def API_SetFieldValueTime(self, UID, cid, fname, oid, ho, mi, se, ms, aschema=None, alldata=PG_FIELDS, amodification=None, adisablechangedevents=0):
        ret = self.API_SetFieldValue(UID, cid, fname, oid, (ho, mi, se, ms), aschema=aschema, alldata=alldata, amodification=amodification, adisablechangedevents=adisablechangedevents)
        return ret

    def CheckCompareTest(self, avalue, atest):
        result = False
        if (atest & cv_eq) and (avalue == 0):
            result = True
        if (atest & cv_le) and (avalue == -1):
            result = True
        if (atest & cv_ge) and (avalue == 1):
            result = True
        if (atest & cv_not) > 0:
            result = not result
        return result

    def API_SetTestDecFieldValue(self, UID, cid, fname, oid, atest, atestvalue, aschema=None, alldata=PG_FIELDS, amodification=None, adisablechangedevents=0):
        atestvalue = int(atestvalue)
        ret = 0
        v = self.API_GetFieldValueInt(UID, cid, fname, oid, aschema=aschema, alldata=alldata)
        if v < atestvalue:
            c = -1
        elif v > atestvalue:
            c = 1
        else:
            c = 0
        t = self.CheckCompareTest(c, atest)
        if t:
            ret = 1
            self.API_SetFieldValue(UID, cid, fname, oid, v - 1, aschema=aschema, alldata=alldata, amodification=amodification, adisablechangedevents=adisablechangedevents)
        return ret

    def API_SetTestIncFieldValue(self, UID, cid, fname, oid, atest, atestvalue, aschema=None, alldata=PG_FIELDS, amodification=None, adisablechangedevents=0):
        atestvalue = int(atestvalue)
        ret = 0
        v = self.API_GetFieldValueInt(UID, cid, fname, oid, aschema=aschema, alldata=alldata)
        if v < atestvalue:
            c = -1
        elif v > atestvalue:
            c = 1
        else:
            c = 0
        t = self.CheckCompareTest(c, atest)
        if t:
            ret = 1
            self.API_SetFieldValue(UID, cid, fname, oid, v + 1, aschema=aschema, alldata=alldata, amodification=amodification, adisablechangedevents=adisablechangedevents)
        return ret

    def API_SetTestFieldValue(self, UID, cid, fname, oid, atest, atestvalue, avalue, aschema=None, alldata=PG_FIELDS, amodification=None, adisablechangedevents=0):
        atestvalue = int(atestvalue)
        ret = 0
        v = self.API_GetFieldValueInt(UID, cid, fname, oid, aschema=aschema, alldata=alldata)
        if v < atestvalue:
            c = -1
        elif v > atestvalue:
            c = 1
        else:
            c = 0
        t = self.CheckCompareTest(c, atest)
        if t:
            ret = 1
            self.API_SetFieldValue(UID, cid, fname, oid, avalue, aschema=aschema, alldata=alldata, amodification=amodification, adisablechangedevents=adisablechangedevents)
        return ret

    def API_SetClassLastModification(self, UID, cid, yy, mm, dd, ho, mi, se, ms, aschema=None, alldata=PG_FIELDS):
        ret = 0
        vn = [yy, mm, dd, ho, mi, se, ms]
        vo = self.API_GetFieldValueDateTime(UID, CLASSES_System_ICORClass, 'aLastModified', cid, aschema=aschema, alldata=alldata)
        if vn > vo:
            self.API_SetFieldValueDateTime(UID, CLASSES_System_ICORClass, 'aLastModified', cid, yy, mm, dd, ho, mi, se, ms, aschema=aschema, alldata=alldata, adisablechangedevents=1)
        return ret

    def API_SetFieldLastModification(self, UID, cid, fname, yy, mm, dd, ho, mi, se, ms, aschema=None, alldata=PG_FIELDS):
        ret = 0
        afid, afieldname, fdata = self.API_GetFieldInfo(UID, cid, fname, aschema=aschema)
        if afid < 0:
            return ret
        vn = [yy, mm, dd, ho, mi, se, ms]
        vo = self.API_GetFieldValueDateTime(UID, CLASSES_System_ICORField, 'aLastModified', afid, aschema=aschema, alldata=alldata)
        if vn > vo:
            self.API_SetFieldValueDateTime(UID, CLASSES_System_ICORField, 'aLastModified', afid, yy, mm, dd, ho, mi, se, ms, aschema=aschema, alldata=alldata, adisablechangedevents=1)
        return ret

    def API_SetMethodLastModification(self, UID, cid, mname, yy, mm, dd, ho, mi, se, ms, aschema=None, alldata=PG_FIELDS):
        ret = 0
        amid, amethodname, mdata = self.API_GetMethodInfo(UID, cid, mname, aschema=aschema)
        if amid < 0:
            return ret
        vn = [yy, mm, dd, ho, mi, se, ms]
        vo = self.API_GetFieldValueDateTime(UID, CLASSES_System_ICORMethod, 'aLastModified', amid, aschema=aschema, alldata=alldata)
        if vn > vo:
            self.API_SetFieldValueDateTime(UID, CLASSES_System_ICORMethod, 'aLastModified', amid, yy, mm, dd, ho, mi, se, ms, aschema=aschema, alldata=alldata, adisablechangedevents=1)
        return ret

    def API_SetFieldModification(self, UID, cid, fname, oid, value=None, aschema=None, alldata=PG_FIELDS):
        ret = 0
        if aschema is None:
            aschema = self.db.schema
        if type(value) in [type([]), type(())]:
            value = storageutil.tdatetime2fmtstr(value)
        elif not value:
            value = storageutil.tdatetime2fmtstr()
        else:
            value = value.replace('/', '-')
            value = value.replace('\\', '-')
        cur = self.db.GetCursor()
        try:
            asql = '''
            update %s.alldata set 
               l=greatest(l,%%s::timestamp), 
               v = v || jsonb_build_object( 'l%s',%%s)
            where c=%%s and o=%%s;
         ''' % (aschema, fname, )
            cur.execute(asql, (value, value, cid, oid))
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_SetObjectModification(self, UID, cid, oid, value, aschema=None, alldata=PG_FIELDS):
        ret = 0
        if aschema is None:
            aschema = self.db.schema
        if type(value) in [type([]), type(())]:
            value = storageutil.tdatetime2fmtstr(value)
        elif not value:
            value = storageutil.tdatetime2fmtstr()
        else:
            value = value.replace('/', '-')
            value = value.replace('\\', '-')
        cur = self.db.GetCursor()
        try:
            asql = '''
            update %s.alldata set 
               l=greatest(l,%%s::timestamp)
            where c=%%s and o=%%s;
         ''' % (aschema, )
            cur.execute(asql, (value, cid, oid))
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_SetFieldValueLastModification(self, UID, cid, fname, oid, yy, mm, dd, ho, mi, se, ms, aschema=None, alldata=PG_FIELDS):
        vn = [yy, mm, dd, ho, mi, se, ms]
        ret = self.API_SetFieldModification(UID, cid, fname, oid, vn, aschema=aschema, alldata=alldata)
        return ret

    def API_SetObjectModified(self, UID, cid, oid, aschema=None, alldata=PG_FIELDS):
        ret = self.API_SetObjectModification(UID, cid, oid, '', aschema=aschema, alldata=alldata)
        return ret

    def API_SetClassProperty(self, UID, cid, fname, value, aschema=None, alldata=PG_FIELDS):
        ret = -1
        if fname in ['ClassDescription', 'ClassFieldsHidden',    # string
                     'IsSystem', 'IsVirtual', 'IsReadOnly', 'ReportClass',    # bool
                     'ClassColIDWidth', 'ClassFormLeft', 'ClassFormTop', 'ClassFormWidth', 'ClassFormHeight',    # integer
                     ]:
            if aschema is None:
                aschema = self.db.schema
            akey = (aschema, cid)
            if self._cid2cdata.has_key(akey):
                del self._cid2cdata[akey][0]
            self.API_SetFieldValue(UID, CLASSES_System_ICORClass, 'a' + fname, cid, value, aschema=aschema, alldata=alldata, adisablechangedevents=1)
            ret = 0
        return ret

    def API_SetFieldProperty(self, UID, cid, fname, fvalue, value, aschema=None, alldata=PG_FIELDS):
        ret = -1
        if fvalue in ['FieldDefaultValueAsString', 'FieldDescription', 'FieldNameAsDisplayed', 'FieldFormat', 'Alignment', 'FieldEditor',    # string
                      'IsAliased', 'IsObligatory', 'IsInteractive', 'IsVirtual', 'IsReportProtected', 'IsReadOnly',    # bool
                      'FieldPosition', 'FieldLVColWidth', 'FieldLeft', 'FieldTop', 'FieldWidth', 'FieldHeight', 'FieldNamePosition', 'FieldDefaultDblClickAction', 'FieldSheetID', 'FieldTabIndex',    # integer
                      ]:
            afid, afieldname, fdata = self.API_GetFieldInfo(UID, cid, fname, aschema=aschema)
            if afid < 0:
                return ret
            if aschema is None:
                aschema = self.db.schema
            akey = (aschema, cid, fname)
            if self._cidfieldname2fdata.has_key(akey):
                del self._cidfieldname2fdata[akey]
            self.API_SetFieldValue(UID, CLASSES_System_ICORField, 'a' + fvalue, afid, value, aschema=aschema, alldata=alldata, adisablechangedevents=1)
            ret = 0
        return ret

    def API_SetMethodProperty(self, UID, cid, mname, fvalue, value, aschema=None, alldata=PG_FIELDS):
        ret = -1
        if fvalue in ['MethodDescription', 'WWWDescription', 'MethodAccess', 'Language', 'MethodText',    # string
                      'IsMenuHidden', 'IsParallel', 'IsQueued', 'WWWMethod', 'WWWConfirmExecute',    # bool
        # integer
                      ]:
            amid, amethodname, mdata = self.API_GetMethodInfo(UID, cid, mname, aschema=aschema)
            if amid < 0:
                return ret
            if aschema is None:
                aschema = self.db.schema
            akey = (aschema, cid, mname)
            if self._cidmethodname2mdata.has_key(akey):
                del self._cidmethodname2mdata[akey]
            self.API_SetFieldValue(UID, CLASSES_System_ICORMethod, 'a' + fvalue, amid, value, aschema=aschema, alldata=alldata, adisablechangedevents=0)
            ret = 0
        return ret

    def API_CreateObjectByID(self, UID, cid, oid, aschema=None, alldata=PG_FIELDS):
        if self.API_ObjectExists(UID, cid, oid, aschema=aschema, alldata=alldata) < 0:
            self.AllData_UpdateObject(cid, oid, UID)
            self.API_ExecuteMethod(UID, cid, 'OnObjectCreate', '', oid, '', 0, aschema=aschema, alldata=alldata)
        return oid

    def API_AddObject(self, UID, cid, aschema=None, alldata=PG_FIELDS):
        oid = 1 + self.API_GetLastObjectID(UID, cid, aschema=aschema, alldata=alldata)
        v = self.API_ExecuteMethod(UID, cid, 'OnObjectAdd', '', oid, '', 0, aschema=aschema, alldata=alldata)
        if v:
            oid = int(v)
        if oid >= 0:
            self.AllData_UpdateObject(cid, oid, UID)
            self.API_ExecuteMethod(UID, cid, 'OnObjectCreate', '', oid, '', 0, aschema=aschema, alldata=alldata)
        return oid

    def API_DeleteObject(self, UID, cid, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = -1
        res = self.API_ExecuteMethod(UID, cid, 'OnObjectDelete', '', oid, '', 0, aschema=aschema, alldata=alldata)
        if res == '0':
            return ret
        lfields = self.API_GetFieldsList(UID, cid, aschema=aschema, alldata=alldata, asfielddata=1)
        for fdata in lfields:
            fname = fdata['vaFieldName']
            ftid = fdata['vaFieldTypeID']
            if ftid > storageutil.MAX_ICOR_SYSTEM_TYPE:
                v = self.API_GetFieldValue(UID, cid, fname, oid, aschema=aschema)
                arefs = dbclasses.FieldRefIterator(v)
                for boid in arefs.oids:
                    self.API_ExecuteMethod(UID, cid, 'OnObjectLinkChanged', fname, oid, '(0,' + str(boid) + ',' + str(ftid) + ')', 0, aschema=aschema, alldata=alldata)
                    self.API_ExecuteMethod(UID, ftid, 'OnObjectRefChanged', fname, boid, '(0,' + str(oid) + ',' + str(cid) + ')', 0, aschema=aschema, alldata=alldata)
        cur = self.db.GetCursor()
        try:
            asql = '''
            delete from %s.alldata where c=%%s and o=%%s returning o;
         ''' % (aschema, )
            cur.execute(asql, (cid, oid))
            res = cur.fetchall()
            if res:
                ret = res[0][0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_ClearAllObjects(self, UID, cid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = 0
        cur = self.db.GetCursor()
        try:
            asql = '''
            delete from %s.alldata where c=%%s;
         ''' % (aschema, )
            cur.execute(asql, (cid, ))
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_ClearAllValues(self, UID, cid, fname, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = 0
        cur = self.db.GetCursor()
        try:
            asql = '''
            update %s.alldata set v = v - '{v%s,l%s,i%s}'::text[] where c=%%s;
         ''' % (aschema, fname, fname, fname)
            cur.execute(asql, (cid, ))
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetFieldVersions(self, UID, cid, fname, oid, aschema=None):
        if aschema is None:
            aschema = self.db.schema
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
            with tv as (
               select i,coalesce(v->>'l%s','') as vl,coalesce(v->>'i%s','') as iv,c,o,u,l,a,v 
               from %s.alldatav 
               where c=%%s and o=%%s and not v->'i%s' is null
               order by i desc
            ), td as (
               select distinct on (iv) i
               from tv
               order by iv,i desc
            )
            select td.i,tv.vl,tv.u,v from td
            left join tv on td.i=tv.i
            order by td.i desc
            limit 200;
         ''' % (fname, fname, aschema, fname)
            cur.execute(asql, (cid, oid))
            res = cur.fetchall()
            for arec in res:
                ret.append([arec[0], storageutil.UTF8_To_CP1250(arec[1]), arec[2], arec[3]])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetObjectValue(self, UID, cid, oid, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        ret = (-1, {})
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o,v from %s.alldata where c=%%s and o=%%s;
         ''' % (aschema, )
            cur.execute(asql, (cid, oid, ))
            res = cur.fetchall()
            if res:
                ret = res[0][0], self.AllData_GetValueDictFromJSON(res[0][1])
        finally:
            self.db.CloseCursor(cur)
        return ret

    def API_GetObjectsValue(self, UID, cid, fields=None, autfconvert=1, aslist=0, aschema=None, alldata=PG_FIELDS):
        if aschema is None:
            aschema = self.db.schema
        if aslist:
            ret = []
        else:
            ret = {}
        cur = self.db.GetCursor()
        try:
            asql = '''
            select o,v from %s.alldata where c=%%s;
         ''' % (aschema, )
            cur.execute(asql, (cid, ))
            res = cur.fetchall()
            for o, d in res:
                d2 = self.AllData_GetValueDictFromJSON(d, fields=fields, autfconvert=autfconvert)
                if aslist:
                    d2['_oid'] = o
                    ret.append(d2)
                else:
                    ret[o] = d2
        finally:
            self.db.CloseCursor(cur)
        return ret

    # DB Maintenance
    def JSONAllDataSave(self, filename, filenamev='', aschema=None):
        if aschema is None:
            aschema = self.db.schema
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
            COPY %s.alldata TO '%s' BINARY;
         ''' % (aschema, filename)
            cur.execute(asql)
            if filenamev:
                asql = '''
               COPY %s.alldatav TO '%s' BINARY;
            ''' % (aschema, filenamev)
                cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def JSONAllDataLoadSnapshot(self, akind, tablesufix, filename, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemasnapshots
        if akind == 'all':
            akind = ''
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
         COPY %s.alldata_snapshot%s_%s FROM '%s' BINARY;
         ''' % (aschema, akind, tablesufix, filename)
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def JSONAllDataSaveSnapshot(self, akind, tablesufix, filename, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemasnapshots
        if akind == 'all':
            akind = ''
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
         COPY %s.alldata_snapshot%s_%s TO '%s' BINARY;
         ''' % (aschema, akind, tablesufix, filename)
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def CreateSnapshotTable(self, akind, tablesufix, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemasnapshots
        if akind == 'all':
            akind = ''
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
         DROP TABLE IF EXISTS %s.alldata_snapshot%s_%s;
         create table %s.alldata_snapshot%s_%s as table %s.alldata with no data;
         ''' % (aschema, akind, tablesufix, aschema, akind, tablesufix, dschema)
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def MakeSnapshot(self, tablesufix, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemasnapshots
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
         DROP TABLE IF EXISTS %s.alldata_snapshot_%s;
         create table %s.alldata_snapshot_%s as table %s.alldata;
         ''' % (aschema, tablesufix, aschema, tablesufix, dschema)
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def MakeSnapshotData(self, akind, tablesufix, lwhere, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemasnapshots
        if akind == 'all':
            akind = ''
        lw = []
        for acid, loids in lwhere:
            lc = ['%s.alldata.c=%d' % (dschema, acid), ]
            for idmin, idmax in loids:
                lc.append('(%s.alldata.o<%d or %s.alldata.o>=%d)' % (dschema, idmin, dschema, idmax))
            lw.append('(' + ' AND '.join(lc) + ')')
        sw = ' OR '.join(lw)
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
         DROP TABLE IF EXISTS %s.alldata_snapshot%s_%s;
         create table %s.alldata_snapshot%s_%s as select _oid,c,o,u,l,s,v from %s.alldata where %s;
         ''' % (aschema, akind, tablesufix, aschema, akind, tablesufix, dschema, sw)
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def RestoreSnapshot(self, tablesufix, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemasnapshots
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
         truncate table %s.alldata;
         truncate table %s.alldatav;
         insert into %s.alldata select * from %s.alldata_snapshot_%s;
         ''' % (dschema, dschema, dschema, aschema, tablesufix)
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def RestoreSnapshotByWhere(self, akind, tablesufix, lwhere, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemasnapshots
        if akind == 'all':
            akind = ''
        lw = []
        for acid, loids in lwhere:
            lc = ['%s.alldata.c=%d' % (dschema, acid), ]
            for idmin, idmax in loids:
                lc.append('(%s.alldata.o<%d or %s.alldata.o>=%d)' % (dschema, idmin, dschema, idmax))
            lw.append('(' + ' AND '.join(lc) + ')')
        sw = ' OR '.join(lw)
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
         delete from %s.alldata where %s;
         insert into %s.alldata select * from %s.alldata_snapshot%s_%s;
         ''' % (dschema, sw, dschema, aschema, akind, tablesufix)
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def RemoveDataByWhere(self, lwhere, aschema=None):
        if aschema is None:
            aschema = self.db.schema
        lw = []
        for acid, loids in lwhere:
            lc = ['%s.alldata.c=%d' % (aschema, acid), ]
            for idmin, idmax in loids:
                lc.append('(%s.alldata.o<%d or %s.alldata.o>=%d)' % (aschema, idmin, aschema, idmax))
            lw.append('(' + ' AND '.join(lc) + ')')
        sw = ' OR '.join(lw)
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
         delete from %s.alldata where %s;
         ''' % (aschema, sw, )
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def RemoveSnapshot(self, akind, tablesufix, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemasnapshots
        if akind == 'all':
            akind = ''
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
         drop table %s.alldata_snapshot%s_%s;
         ''' % (aschema, akind, tablesufix)
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def RenameSnapshot(self, akind, tablesufix1, tablesufix2, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemasnapshots
        if akind == 'all':
            akind = ''
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
         ALTER TABLE %s.alldata_snapshot%s_%s RENAME TO alldata_snapshot%s_%s;
         ''' % (aschema, akind, tablesufix1, akind, tablesufix2)
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def GetTableSnapshots(self, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemasnapshots
        ret = []
        ret2 = []
        ret3 = []
        ret4 = []
        cur = self.db.GetCursor()
        try:
            asql = '''
            SELECT table_name FROM information_schema.tables WHERE table_catalog='icor' and table_schema = '%s' and table_type='BASE TABLE';
         ''' % (aschema, )
            l, ld, ls = [], [], []
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                st = storageutil.UTF8_To_CP1250(arec[0])
                ss = 'alldata_snapshot_'
                if st[:len(ss)] == ss:
                    l.append(st[len(ss):])
                ss = 'alldata_snapshotdata_'
                if st[:len(ss)] == ss:
                    ld.append(st[len(ss):])
                ss = 'alldata_snapshotsecurity_'
                if st[:len(ss)] == ss:
                    ls.append(st[len(ss):])
            for asnapshot in l:
                asql = '''
               select count(*) cnt,max(l)::text lastchange from %s.alldata_snapshot_%s;
            ''' % (aschema, asnapshot)
                cur.execute(asql)
                res = cur.fetchall()
                for arec in res:
                    ret.append([storageutil.UTF8_To_CP1250(arec[1]), asnapshot, arec[0]])
            ret.sort()
            ret.reverse()
            for asnapshot in ld:
                asql = '''
               select count(*) cnt,max(l)::text lastchange from %s.alldata_snapshotdata_%s;
            ''' % (aschema, asnapshot)
                cur.execute(asql)
                res = cur.fetchall()
                for arec in res:
                    ret3.append([storageutil.UTF8_To_CP1250(arec[1]), asnapshot, arec[0]])
            ret3.sort()
            ret3.reverse()
            for asnapshot in ls:
                asql = '''
               select count(*) cnt,max(l)::text lastchange from %s.alldata_snapshotsecurity_%s;
            ''' % (aschema, asnapshot)
                cur.execute(asql)
                res = cur.fetchall()
                for arec in res:
                    ret4.append([storageutil.UTF8_To_CP1250(arec[1]), asnapshot, arec[0]])
            ret4.sort()
            ret4.reverse()
            for atablename in ['alldata', 'alldatav']:
                asql = '''
               select count(*) cnt,max(l)::text lastchange from %s.%s;
            ''' % (dschema, atablename)
                cur.execute(asql)
                res = cur.fetchall()
                for arec in res:
                    ret2.append([atablename, arec[0], storageutil.UTF8_To_CP1250(arec[1])])
        finally:
            self.db.CloseCursor(cur)
        return ret, ret3, ret4, ret2

    def RemoveVersions(self, aschema=None):
        if aschema is None:
            aschema = self.db.schema
        ret = []
        cur = self.db.GetCursor()
        try:
            asql = '''
         truncate table %s.alldatav;
         ''' % (aschema, )
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def CreateHistoryTable(self, aname, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemahistory
        ret = []
        d = {'PGUser': self.db.GetConfigValue('PGUser'), 'PGSchema': aschema, 'Table': aname, 'TableV': aname+'_v'}
        cur = self.db.GetCursor()
        try:
            asql = '''
                CREATE TABLE IF NOT EXISTS %(PGSchema)s.%(Table)s
                (
                    _oid character(32) COLLATE pg_catalog."default" NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
                    fid integer DEFAULT 0,
                    keyid integer DEFAULT 0,
                    ownerid integer DEFAULT 0,
                    lastmodification text COLLATE pg_catalog."default" DEFAULT ''::text,
                    isdeleted integer DEFAULT 0,
                    value text COLLATE pg_catalog."default" DEFAULT ''::text,
                    vlen integer DEFAULT 0,
                    vhash text COLLATE pg_catalog."default" DEFAULT ''::text,
                    status text COLLATE pg_catalog."default" DEFAULT ''::text,
                    CONSTRAINT %(Table)s_pkey PRIMARY KEY (_oid)
                ) WITH ( OIDS = FALSE) TABLESPACE pg_default;
                ALTER TABLE %(PGSchema)s.%(Table)s OWNER to %(PGUser)s;

                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(Table)s_fid ON %(PGSchema)s.%(Table)s USING btree (fid) TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(Table)s_keyid ON %(PGSchema)s.%(Table)s USING btree (keyid) TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(Table)s_ownerid ON %(PGSchema)s.%(Table)s USING btree (ownerid) TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(Table)s_isdeleted ON %(PGSchema)s.%(Table)s USING btree (isdeleted) TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(Table)s_lastmodification ON %(PGSchema)s.%(Table)s USING btree (lastmodification COLLATE pg_catalog."default") TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(Table)s_vlen ON %(PGSchema)s.%(Table)s USING btree (vlen) TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(Table)s_vhash ON %(PGSchema)s.%(Table)s USING btree (vhash COLLATE pg_catalog."default") TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(Table)s_status ON %(PGSchema)s.%(Table)s USING btree (status COLLATE pg_catalog."default") TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(Table)s_search1 ON %(PGSchema)s.%(Table)s USING btree (fid,keyid,lastmodification,isdeleted,vhash COLLATE pg_catalog."default") TABLESPACE pg_default;

                CREATE TABLE IF NOT EXISTS %(PGSchema)s.%(TableV)s
                (
                    _oid character(32) COLLATE pg_catalog."default" NOT NULL DEFAULT lower(replace(((uuid_generate_v4())::character varying(50))::text, '-'::text, ''::text)),
                    fid integer DEFAULT 0,
                    keyid integer DEFAULT 0,
                    ownerid integer DEFAULT 0,
                    lastmodification text COLLATE pg_catalog."default" DEFAULT ''::text,
                    isdeleted integer DEFAULT 0,
                    value text COLLATE pg_catalog."default" DEFAULT ''::text,
                    vlen integer DEFAULT 0,
                    vhash text COLLATE pg_catalog."default" DEFAULT ''::text,
                    status text COLLATE pg_catalog."default" DEFAULT ''::text,
                    CONSTRAINT %(TableV)s_pkey PRIMARY KEY (_oid)
                ) WITH ( OIDS = FALSE) TABLESPACE pg_default;
                ALTER TABLE %(PGSchema)s.%(TableV)s OWNER to %(PGUser)s;

                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(TableV)s_fid ON %(PGSchema)s.%(TableV)s USING btree (fid) TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(TableV)s_keyid ON %(PGSchema)s.%(TableV)s USING btree (keyid) TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(TableV)s_ownerid ON %(PGSchema)s.%(TableV)s USING btree (ownerid) TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(TableV)s_isdeleted ON %(PGSchema)s.%(TableV)s USING btree (isdeleted) TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(TableV)s_lastmodification ON %(PGSchema)s.%(TableV)s USING btree (lastmodification COLLATE pg_catalog."default") TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(TableV)s_vlen ON %(PGSchema)s.%(TableV)s USING btree (vlen) TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(TableV)s_vhash ON %(PGSchema)s.%(TableV)s USING btree (vhash COLLATE pg_catalog."default") TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(TableV)s_status ON %(PGSchema)s.%(TableV)s USING btree (status COLLATE pg_catalog."default") TABLESPACE pg_default;
                CREATE INDEX IF NOT EXISTS i_%(PGSchema)s_%(TableV)s_search1 ON %(PGSchema)s.%(TableV)s USING btree (fid,keyid,lastmodification,isdeleted,vhash COLLATE pg_catalog."default") TABLESPACE pg_default;
            ''' % d
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def ClearHistoryTableTemp(self, aname, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemahistory
        ret = []
        d = {'PGSchema': aschema, 'Table': aname, 'TableV': aname+'_v'}
        cur = self.db.GetCursor()
        try:
            asql = '''
                TRUNCATE TABLE %(PGSchema)s.%(TableV)s;
            ''' % d
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def LoadHistoryTableTemp(self, aname, apath, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemahistory
        apath=storageutil.CleanPath(apath, aremovelast=False, aensurelast=False, anormalize=False)
        ret = []
        d = {'PGSchema': aschema, 'Table': aname, 'TableV': aname+'_v', 'Path': apath}
        cur = self.db.GetCursor()
        try:
            asql = '''
                copy %(PGSchema)s.%(TableV)s (fid,keyid,ownerid,lastmodification,isdeleted,status,value,vlen,vhash) from '%(Path)s';
            ''' % d
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret

    def StoreHistoryTableTemp(self, aname, aschema=None):
        dschema = aschema
        if dschema is None:
            dschema = self.db.schema
        aschema = self.db.schemahistory
        ret = []
        d = {'PGSchema': aschema, 'Table': aname, 'TableV': aname+'_v'}
        cur = self.db.GetCursor()
        try:
            asql = '''
                insert into %(PGSchema)s.%(Table)s (fid,keyid,ownerid,lastmodification,isdeleted,value,vlen,vhash,status)
                (
                	select tv.fid,tv.keyid,tv.ownerid,tv.lastmodification,tv.isdeleted,tv.value,tv.vlen,tv.vhash,tv.status
                	from %(PGSchema)s.%(TableV)s tv 
                	left join %(PGSchema)s.%(Table)s th on tv.fid=th.fid and tv.keyid=th.keyid and tv.lastmodification=th.lastmodification and tv.isdeleted=th.isdeleted and tv.vhash=th.vhash
                	where th._oid is null
                );
            ''' % d
            cur.execute(asql)
        finally:
            self.db.CloseCursor(cur)
        return ret
