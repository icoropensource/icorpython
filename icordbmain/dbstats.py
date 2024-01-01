# -*- coding: utf-8 -*-
import appplatform.storageutil as storageutil


class ICORDBStats(object):

    def __init__(self, adb):
        self.db = adb

    ### Stats:
    def getChapterGenTimeCountByUserLast7d(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery
            as (
            	select co.username,co.chapterid,cs.title,sum(co.timeoperation) totaltime,count(co.username) gencount
            	from %s.cmschapteroperation co
            	left join %s.cmschapterstate cs on co.chapterid=cs.chapterid
            	where
            	co.created>CURRENT_DATE-7
            	and 
            	cs.created>CURRENT_DATE-7
            	group by co.username,co.chapterid,cs.title
            	order by totaltime desc
            	)
            select cast(json_agg(json_build_object('username',username, 'chapterid',chapterid, 'title',title, 'totaltime',totaltime, 'gencount',gencount)) as text) as result
            from subquery
            limit 5000;
         ''' % (self.db.schema, self.db.schema,
                )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getChapterGenTimeCountLast7d(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery
            as (
                select co.chapterid,cs.title,sum(co.timeoperation) totaltime,count(co.chapterid) gencount
                from %s.cmschapteroperation co
                left join %s.cmschapterstate cs on co.chapterid=cs.chapterid
                where
                co.created>CURRENT_DATE-7
                and 
                cs.created>CURRENT_DATE-7
                group by co.chapterid,cs.title
                order by totaltime desc
            	)
            select cast(json_agg(json_build_object('chapterid',chapterid, 'title',title, 'totaltime',totaltime, 'gencount',gencount)) as text) as result
            from subquery
            limit 5000;
         ''' % (self.db.schema, self.db.schema,
                )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getChapterGenTimeCountWithFilesLast7d(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery 
            as (
            	select q1.chapterid,cs.title,cast(cast(q1.totaltime as numeric(19,2))/100 as numeric(19,2)) as totaltime,q1.gencount,0 as filescount
            		--,(select count(*) from %s.syncfiles sf where sf.dstpath like '%%chapter_' || q1.chapterid || '%%' and sf.created>CURRENT_DATE-7) filescount
            	from (
            	    select co.chapterid,sum(cast(100*co.timeoperation as integer)) totaltime,count(co.chapterid) gencount
            	    from %s.cmschapteroperation co
            	    where
            	    co.created>CURRENT_DATE-7
            	    group by co.chapterid
            	) q1
                left join %s.cmschapterstate cs on cs.chapterid=q1.chapterid
                order by totaltime desc
            )
            select cast(json_agg(json_build_object('chapterid',chapterid, 'title',title, 'totaltime',totaltime, 'gencount',gencount, 'filescount',filescount)) as text) as result
            from subquery
            limit 5000;
         ''' % (self.db.schema, self.db.schema, self.db.schema,
                )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getChapterStates(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery
            as (
                select cs.cmsid,cs.cmsname,cs.chapterid,cs.title,cs.created,cs.priority,cs.operationoid,cs.status
                from %s.cmschapterstate cs
                order by cs.cmsname,cs.chapterid
            	)
            select cast(json_agg(json_build_object('cmsid',cmsid,'cmsname',cmsname,'chapterid',chapterid,'title',title,'created',created,'priority',priority,'operationoid',operationoid,'status',status)) as text) as result
            from subquery
            limit 10000;
         ''' % (self.db.schema, )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getCMSGenTimeCountLast7d(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery
            as (
                select 
                	cs.cmsid,cs.cmsname,
                	sum((select count(*) from %s.cmschapteroperation co2 where co2.chapterid=cs.chapterid and co2.created>CURRENT_DATE-7)) as gencount,
                	sum((select sum(co2.timeoperation) from %s.cmschapteroperation co2 where co2.chapterid=cs.chapterid and co2.created>CURRENT_DATE-7)) as totaltime
                from %s.cmschapterstate cs
                group by cs.cmsid,cs.cmsname
                order by cs.cmsname
            	)
            select cast(json_agg(json_build_object('cmsid',cmsid,'cmsname',cmsname,'gencount',gencount,'totaltime',totaltime)) as text) as result
            from subquery
            limit 10000;
         ''' % (self.db.schema, self.db.schema, self.db.schema,
                )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getFilesGenTimeCountLast7d(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery
            as (
            	select sf.created::date dzien
            		,count(*) liczbaplikow
            		,sum(sf.filesize) rozmiar
            		,sum(sf.writecnt) liczbazapisow
            		,sum(sf.timesave) czaszapisu
            	from %s.syncfiles sf
            	where
            		sf.created>CURRENT_DATE-7
            	group by 1
            	order by 1
            	)
            select cast(json_agg(json_build_object('dzien', dzien, 'liczbaplikow', liczbaplikow, 'rozmiar', rozmiar, 'liczbazapisow', liczbazapisow, 'czaszapisu',czaszapisu)) as text) as result
            from subquery;
         ''' % (self.db.schema, )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getFilesCopiedGenTimeCountLast7d(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery
            as (
            	select sf.created::date dzien
            		,count(*) liczbaplikow
            		,sum(sf.filesize) rozmiar
            		,sum(sf.writecnt) liczbazapisow
            		,sum(sf.timesave) czaszapisu
            		,sum(sf.timecopy) czaskopiowania
            	from %s.syncfiles sf
            	where
            		sf.created>CURRENT_DATE-7
            		and sf.status = 'C4'
            	group by 1
            	order by 1
            	)
            select cast(json_agg(json_build_object('dzien', dzien, 'liczbaplikow', liczbaplikow, 'rozmiar', rozmiar, 'liczbazapisow', liczbazapisow, 'czaszapisu',czaszapisu, 'czaskopiowania',czaskopiowania)) as text) as result
            from subquery;
         ''' % (self.db.schema, )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getFilesPathGenTimeCountLast7d(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery
            as (
            	select 
            		sf.dstpath
            		,count(*) gencount
            		,sum(sf.filesize) rozmiar
            		,sum(sf.writecnt) liczbazapisow
            		,sum(cast (100*sf.timesave as integer)) czaszapisu
            	from %s.syncfiles sf
            	where
            		sf.created>CURRENT_DATE-7
            	group by sf.dstpath
            	order by gencount desc,sf.dstpath
            	limit 5000
            )
            select cast(json_agg(json_build_object('dstpath', dstpath, 'gencount', gencount, 'rozmiar', rozmiar, 'liczbazapisow', liczbazapisow, 'czaszapisu',cast(cast(czaszapisu as numeric(19,2))/100 as numeric(19,2)))) as text) as result
            from subquery;
         ''' % (self.db.schema, )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getExecutorMethodsListAll(self, astatus):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            ssql = ''
            if astatus:
                ssql = " where me.status='%s' " % astatus
            asql = '''
            with subquery
            as (
            	select 
            		me.eventtime,me.meid,me.cid,me.name,me.fieldname,me.oid,me.value,me.uid,me.isparallel,me.isqueued,me.eventtime_ready,me.eventtime_deleted,me.eventtime_working,me.eventtime_done,me.status,me.priority
            	from %s.executormethods me %s
            	order by me.eventtime desc
            	limit 2000
            	)
            select cast(json_agg(json_build_object('eventtime',eventtime,'meid',meid,'cid',cid,'name',name,'fieldname',fieldname,'oid',oid,'value',value,'uid',uid,'isparallel',isparallel,'isqueued',isqueued,'eventtime_ready',eventtime_ready,'eventtime_deleted',eventtime_deleted,'eventtime_working',eventtime_working,'eventtime_done',eventtime_done,'status',status,'priority',priority)) as text) as result
            from subquery;
         ''' % (self.db.schema, ssql)
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getExecutorMethodsInfo(self, meid):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            ssql = ''
            if meid:
                ssql = " where me.meid='%s' " % meid
            asql = '''
            with subquery
            as (
            	select 
            		me.eventtime, me.meid, me.cid, me.name, me.fieldname, me.oid, me.value, me.uid, me.isparallel, me.isqueued,
                  me.eventtime_ready,me.eventtime_deleted,me.eventtime_working,me.eventtime_done, me.status, me.priority,
                  me.pid, me.result, me.output
            	from %s.executormethods me %s
            	order by me.eventtime desc
            	limit 1
            	)
            select cast(json_agg(json_build_object(
               'eventtime',eventtime,'meid',meid,'cid',cid,'name',name,'fieldname',fieldname,'oid',oid,'value',value,'uid',uid,'isparallel',isparallel,'isqueued',isqueued,
               'eventtime_ready',eventtime_ready,'eventtime_deleted',eventtime_deleted,'eventtime_working',eventtime_working,'eventtime_done',eventtime_done,'status',status,'priority',priority,
               'pid',pid,'result',result,'output',output
            )) as text) as result
            from subquery;
         ''' % (self.db.schema, ssql)
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getSessionsGenActiveLast1d(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery
            as (
            	select
            		--tt._oid as tokenid,
            		tt.created,tt.status,
            		tv1.value as uid, /*tv1.created as uid_created,tv1._datetime as uid_lastmodification,*/
            		tv2.value as username, /*tv2.created as username_created,tv2._datetime as username_lastmodification,*/
            		(select max(_datetime) from %s.sessionvalues tvx where tvx.tokenid=tt._oid) as last_access,
            		(select count(*) from %s.sessions tsx where tsx.tokenid=tt._oid) as sessions
            	from %s.sessiontokens tt
            	left join %s.sessionvalues tv1 on tv1.tokenid=tt._oid and tv1.valuename='uid'
            	left join %s.sessionvalues tv2 on tv2.tokenid=tt._oid and tv2.valuename='username'
            	where 
            	(select max(_datetime) from %s.sessionvalues tvx where tvx.tokenid=tt._oid)>CURRENT_DATE-1
            	and tv1.value<>'-1' and tv2.value<>'Administrator'
            	order by last_access desc
            	limit 1000
            	)
            select cast(json_agg(json_build_object('created',created,'status',status,'uid',uid,'username',username,'last_access',last_access,'sessions',sessions)) as text) as result
            from subquery;
         ''' % (self.db.schema, self.db.schema, self.db.schema, self.db.schema, self.db.schema, self.db.schema,
                )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getDBPGStatActivity(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery
            as (
            	select 
            	pa.datid,pa.datname,pa.pid,pa.usesysid,pa.usename,pa.application_name,pa.backend_start,pa.query_start,pa.state_change,pa.state,pa.query
            	from pg_stat_activity pa
            	order by pa.state,pa.query_start
            	limit 1000
            )
            select cast(json_agg(json_build_object(
            'datid',datid,'datname',datname,'pid',pid,'usesysid',usesysid,'usename',usename,'application_name',application_name,'backend_start',backend_start,'query_start',query_start,'state_change',state_change,'state',state,'query',query
            )) as text) as result
            from subquery;
         '''
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getDBPGDatabaseSize(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery
            as (
               SELECT pg_size_pretty( pg_database_size( current_database() ) ) As human_size, pg_database_size( current_database() ) As raw_size
            	)
            select cast(json_agg(json_build_object('human_size',human_size,'raw_size',raw_size)) as text) as result
            from subquery
            limit 10000;
         '''
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getDBPGStatIOUserTables(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery
            as (
               SELECT relid,schemaname,relname,heap_blks_read,heap_blks_hit,idx_blks_read,idx_blks_hit,toast_blks_read,toast_blks_hit,tidx_blks_read,tidx_blks_hit 
               FROM pg_statio_user_tables 
               where schemaname='%s'
            	)
            select cast(json_agg(json_build_object('relid',relid,'schemaname',schemaname,'relname',relname,'heap_blks_read',heap_blks_read,'heap_blks_hit',heap_blks_hit,'idx_blks_read',idx_blks_read,'idx_blks_hit',idx_blks_hit,'toast_blks_read',toast_blks_read,'toast_blks_hit',toast_blks_hit,'tidx_blks_read',tidx_blks_read,'tidx_blks_hit',tidx_blks_hit)) as text) as result
            from subquery
            limit 1000;
         ''' % (self.db.schema, )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getDBPGStatUserTables(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery
            as (
               SELECT relid,schemaname,relname,seq_scan,seq_tup_read,idx_scan,idx_tup_fetch,n_tup_ins,n_tup_upd,n_tup_del,n_tup_hot_upd,n_live_tup,n_dead_tup,n_mod_since_analyze,last_vacuum,last_autovacuum,last_analyze,last_autoanalyze,vacuum_count,autovacuum_count,analyze_count,autoanalyze_count 
               FROM pg_stat_user_tables 
               where schemaname='%s'
            	)
            select cast(json_agg(json_build_object('relid',relid,'schemaname',schemaname,'relname',relname,'seq_scan',seq_scan,'seq_tup_read',seq_tup_read,'idx_scan',idx_scan,'idx_tup_fetch',idx_tup_fetch,'n_tup_ins',n_tup_ins,'n_tup_upd',n_tup_upd,'n_tup_del',n_tup_del,'n_tup_hot_upd',n_tup_hot_upd,'n_live_tup',n_live_tup,'n_dead_tup',n_dead_tup,'n_mod_since_analyze',n_mod_since_analyze,'last_vacuum',last_vacuum,'last_autovacuum',last_autovacuum,'last_analyze',last_analyze,'last_autoanalyze',last_autoanalyze,'vacuum_count',vacuum_count,'autovacuum_count',autovacuum_count,'analyze_count',analyze_count,'autoanalyze_count',autoanalyze_count)) as text) as result
            from subquery
            limit 1000;
         ''' % (self.db.schema, )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getExecutorMethodsGroupByStatus(self):
        ret = '{}'
        cur = self.db.GetCursor()
        try:
            asql = '''
            with subquery
            as (
            	select 
                  me.status,
                  count(*) as total
            	from %s.executormethods  me
            	where 
            	(me.eventtime>CURRENT_DATE-7)
            	group by me.status
            	order by me.status
               limit 1000
            	)
            select 
                cast(json_build_object(
                	'widget','{
                		"type":"table",
                     "column_details":false
                	}'::json,
                    'fields','[
                       {
                          "name":"status",
                          "prettyname":"Status",
                          "type":"text"
                       },
                       {
                          "name":"total",
                          "prettyname":"Razem",
                          "type":"integer"
                       }
                    ]'::json,
            	    'items',json_agg(subquery)
                 ) as text) as result
            from subquery;
         ''' % (self.db.schema, )
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret

    def getDBPGStatActivityQuery(self):
        ret = '[]'
        cur = self.db.GetCursor()
        try:
            asql = '''
           SELECT datname,
                  a.pid as pid,
                  usename,
                  client_addr,
                  client_port,
                  round(extract(epoch from (now() - xact_start))) as age,
                  waiting,
                  string_agg(other.pid::TEXT, ',' ORDER BY other.pid) as locked_by,
                  CASE
                     WHEN state = 'idle in transaction' THEN
                         CASE WHEN xact_start != state_change THEN
                             state||' '||CAST( abs(round(extract(epoch from (now() - state_change)))) AS text )
                         ELSE
                             state
                         END
                     WHEN state = 'active' THEN query
                     ELSE state
                     END AS query
             FROM pg_stat_activity a
             LEFT JOIN pg_locks  this ON (this.pid = a.pid and this.granted = 'f')
             -- acquire the same type of lock that is granted
             LEFT JOIN pg_locks other ON ((this.locktype = other.locktype AND other.granted = 't')
                                      AND ( ( this.locktype IN ('relation', 'extend')
                                             AND this.database = other.database
                                             AND this.relation = other.relation)
                                            OR (this.locktype ='page'
                                             AND this.database = other.database
                                             AND this.relation = other.relation
                                             AND this.page = other.page)
                                            OR (this.locktype ='tuple'
                                             AND this.database = other.database
                                             AND this.relation = other.relation
                                             AND this.page = other.page
                                             AND this.tuple = other.tuple)
                                            OR (this.locktype ='transactionid'
                                             AND this.transactionid = other.transactionid)
                                            OR (this.locktype = 'virtualxid'
                                             AND this.virtualxid = other.virtualxid)
                                            OR (this.locktype IN ('object', 'userlock', 'advisory')
                                             AND this.database = other.database
                                             AND this.classid = other.classid
                                             AND this.objid = other.objid
                                             AND this.objsubid = other.objsubid))
                                          )
             WHERE a.pid != pg_backend_pid()
             GROUP BY 1,2,3,4,5,6,7,9
'''
            cur.execute(asql)
            res = cur.fetchall()
            for arec in res:
                ret = arec[0]
        finally:
            self.db.CloseCursor(cur)
        return ret
