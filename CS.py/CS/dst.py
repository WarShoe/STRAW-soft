import os
import sys,re,optparse
try:
    from colors import *
except:
    from CS.colors import *

def get_html_page(page):
    import httplib
    
    r = re.match('http://(?P<host>[\w.]+)(?P<page>/.*)',page)
    if not r:
        raise 'bad page name:',page
    conn = httplib.HTTPConnection(r.group('host'))
    conn.request("GET", r.group('page'))
    r1 = conn.getresponse()
    #print r1.status, r1.reason
    return r1.read()

##  @brief Period properties
##
class DstPeriod:
    ##  @brief Constructor
    ##
    def __init__(self,full_name,mode,slot):

        ##  Period name
        self.full_name = full_name
        
        ##  Data taking mode: 'L' or 'T'
        self.__mode = mode

        ##  Slot number in the DST production
        self.__slot = slot

    def mode(self):
       return self.__mode

    def slot(self):
        return self.__slot

    def name(self):
        return self.full_name[2:]
        
    def year(self):
        return 2000+int(self.full_name[:2])
        
    def __str__(self):
        return '%s year=%d mode=%s slot=%d' % (self.name(),self.year(),self.mode(),self.slot())

    def pprint(self):
        print self

def add_period(period,d):
    d[period.full_name] = period

##  @brief @return regular expression for an html table cell
def htc(name):
    return '\s*\<td\>\s*(?P<%s>.*?)\s*\</td\>\s*' % name

def read_periods_from_page(page):

    periods={}

    for l in page.split('\n'):
        #r = re.match('\<tr\>\s*\<td\>\s*(?P<period>\d\d\w+)\s*\</td\>\<td\>',l)
        r = re.match('\<tr\>%s%s%s%s%s%s%s' % (htc('period'),htc('mode'),htc('start'),htc('stop'),htc('run_min'),htc('run_max'),htc('slot')),l)
        if not r: continue
        #print r.group('period'),r.group('mode'),r.group('start'),r.group('stop'),r.group('run_min'),r.group('run_max'),r.group('slot')
        
        if r.group('period')[0]!='0':
            continue
        
        rr = re.match('.*\s*(?P<mode>[LTH]).*',r.group('mode'))
        if not rr:  continue
        mode = rr.group('mode')
        
        slot = int(r.group('slot'))

        p = DstPeriod(r.group('period'),mode=mode,slot=slot)
        p.time_start = r.group('start')
        p.time_stop = r.group('stop')
        p.run_min = int(r.group('run_min'))
        p.run_max = int(r.group('run_max'))
        add_period(p,periods)
    
    return periods

def decode_mDST_name(name):
    import re
    r = re.match('mDST-(?P<run>\d+)(-(?P<cdr>\d+))?-(?P<slot>\d)-(?P<phast>\d+)\.root(\.(?P<num>\d+))?',name)
    num = r.group('num')
    if num!=None:
        num = int(num)
    return int(r.group('run')),r.group('cdr'),int(r.group('slot')),int(r.group('phast')),num

def get_period_files_cern(period,dir_name='mDST',print_files=False):
    from CS.castor import castor_files
        
    compass_data = '/castor/cern.ch/compass/data/'
    d = compass_data+str(period.year())+'/oracle_dst/'+period.name()+'/'+dir_name

    files=[]
    for f in castor_files(d):
        name = os.path.split(f)[1]
        try:
            run,cdr,slot,phast,n = decode_mDST_name(name)
        except:
            print 'Bad name:',name
            continue
        if slot!=period.slot():
            continue
        files.append(f)

        if print_files:
            print f
    
    return files

def get_period_files_gridka(period,print_files=False,verbose=False):

    period_dirs = {}
    d1 = '/grid/fzk.de/mounts/pnfs/compass/data/mDST/2004/'
    period_dirs['04W23'] = []
    period_dirs['04W23'].append(d1+'W23-1')
    period_dirs['04W23'].append(d1+'W23-2')

    period_dirs['04W32'] = []
    period_dirs['04W32'].append(d1+'W32-2')
    period_dirs['04W32'].append(d1+'W32-3')

    d2 = '/grid/fzk.de/mounts/nfs/data/compass3/data/mDST/2004/'
    period_dirs['04W22'] = []
    period_dirs['04W22'].append(d2+'W22-2')
    period_dirs['04W23'] = []
    period_dirs['04W23'].append(d2+'W23-3')
    period_dirs['04W26'] = []
    period_dirs['04W26'].append(d2+'W26-2')
    period_dirs['04W27'] = []
    period_dirs['04W27'].append(d2+'W27-2')
    period_dirs['04W28'] = []
    period_dirs['04W28'].append(d2+'W28-2')
    period_dirs['04W29'] = []
    period_dirs['04W29'].append(d2+'W29-1')
    period_dirs['04W30'] = []
    period_dirs['04W30'].append(d2+'W30-2')
    period_dirs['04W31'] = []
    period_dirs['04W31'].append(d2+'W31-2')
    period_dirs['04W33'] = []
    period_dirs['04W33'].append(d2+'W33-2')
    period_dirs['04W34'] = []
    period_dirs['04W34'].append(d2+'W34-3')
    period_dirs['04W35'] = []
    period_dirs['04W35'].append(d2+'W35-2')
    period_dirs['04W36'] = []
    period_dirs['04W36'].append(d2+'W36-2')
    period_dirs['04W37'] = []
    period_dirs['04W37'].append(d2+'W37-1')
    period_dirs['04W37'].append(d2+'W37-3')
    period_dirs['04W39'] = []
    period_dirs['04W39'].append(d2+'W39-2')
    period_dirs['04W40'] = []
    period_dirs['04W40'].append(d2+'W40-3')

    try:
        pdirs =  period_dirs[period.full_name]
    except:
        pdirs = []

    for d in gridka_get_period_dirs():
        if year(d)!=period.year():  continue
        dname = d + '/' + period.name()
        if not os.access(dname,os.F_OK):  continue
        dname2 = dname + '/mDST'
        if os.access(dname2,os.F_OK):
            dname = dname2
        pdirs.append(dname)

    if verbose:
        print 'Period %s directories:' % period.full_name,pdirs

    files = []
    for dname in pdirs:
        if verbose:
            print 'period %s dir:' % period.full_name,dname
        for f in os.listdir(dname):
            try:
                run,cdr,slot,phast,n = decode_mDST_name(f)
            except:
                print 'Bad name:',dname,f
                continue
            if slot!=period.slot():
                if verbose:
                    print 'Wrong slot for "%s"   file_slot=%d  expected_slot=%d' % (f,slot,period.slot())
                continue
            ff = dname + '/' + f
            files.append(ff)

            if print_files:
                print ff
    
    return files

def gridka_get_period_dirs():
    data_periods = []
    data_periods.append('/grid/fzk.de/mounts/pnfs/compass/data/mDST/2002')
    data_periods.append('/grid/fzk.de/mounts/pnfs/compass/data/castor_mirror/compass/data/2002/oracle_dst')
    data_periods.append('/grid/fzk.de/mounts/pnfs/compass/data/mDST/2003')
    data_periods.append('/grid/fzk.de/mounts/pnfs/compass/disk-only/data/castor_mirror/compass/data/2003/oracle_dst')
    data_periods.append('/grid/fzk.de/mounts/pnfs/compass/data/mDST/2004')
    data_periods.append('/grid/fzk.de/mounts/pnfs/compass/data/castor_mirror/compass/data/2004/oracle_dst')
    data_periods.append('/grid/fzk.de/mounts/pnfs/compass/disk-only/data/castor_mirror/compass/data/2006/oracle_dst')
    data_periods.append('/grid/fzk.de/mounts/pnfs/compass/data/castor_mirror/compass/data/2006/oracle_dst')
    return data_periods

def year(path):
    import re
    r = re.match('.*/(?P<year>\d\d\d\d)(/|$)',path)
    if not r:
        print 'Failed:', path
    return int(r.group('year'))

def main():
    parser = optparse.OptionParser(version='1.1.3')

    parser.usage = '%prog <options>\n'\
                   'Author: Zvyagin.Alexander@gmail.com'

    parser.description = 'Get DST producation information.'

    parser.add_option('', '--page',dest='page',default='http://na58dst1.home.cern.ch/na58dst1/dstprod.html',
                      help='DST producation status page (%default)', type='string')
    parser.add_option('', '--verbose',dest='verbose',default=False,action='store_true',
                      help='Be verbose')
    parser.add_option('', '--time',dest='time',default='',
                      help='Print mDST files for selected years (example: "2002,2004,03P1D")',
                      type='string')
    parser.add_option('', '--mode',dest='mode',default='LTH',
                      help='Select Longitudinal/Transversity/Hadron data, (use L,T,H,LT,etc). Default is %default.',
                      type='string')
    parser.add_option('', '--mDST-chunks',dest='mDST_chunks',default=False,action='store_true',
                      help='Print mDST files on chunks (for CERN)')
    parser.add_option('', '--mDST-merged',dest='mDST_merged',default=False,action='store_true',
                      help='Print mDST merged files (for CERN)')
    parser.add_option('', '--place',dest='place',default='cern',choices=('cern','gridka'),
                      help='Location of files (cern,gridka,..)')
    

    (options, args) = parser.parse_args()

    work = False

    years=[]
    user_periods=[]
    for y in options.time.split(','):
        if not y:
            continue
        try:
            years.append(int(y))
        except:
            user_periods.append(y)
        work = True

    if options.verbose:
        work = True
        print 'Years to scan:', years
        print 'Periods to scan:',user_periods

    if options.verbose:
        print 'Reading page: ', options.page
    page = get_html_page(options.page)

    if options.verbose:
        print 'Analysing it...'
    periods = read_periods_from_page(page)
    #if options.verbose:
    #    print CYAN,periods,RESET

    if options.verbose:
        for p in periods.values():
            p.pprint()

    if 1:
        for period in periods.values():

            if (not period.year() in years) and (not period.full_name in user_periods):
                continue

            if options.verbose:
                print 'Found user-requested period:',period


            # Check longitudinal or/and transversity data
            if not period.mode() in options.mode:
                continue

            files = []
            if options.place=='cern':
                dd = []

                if options.mDST_merged:
                    dd.append('mDST')

                if options.mDST_chunks:
                    dd.append('mDST.chunks')

                for d in dd:
                    if options.place=='cern':
                        files = get_period_files_cern(period,d,True)

            elif options.place=='gridka':
                files = get_period_files_gridka(period,True,options.verbose)
                
            if options.verbose:
                print BOLD,GREEN,'There are %d files for period %s' % (len(files),period.name()),RESET

            if 0==len(files):
                print 'No files found for year %d period %s slot %d' % (period.year(),period.name(),period.slot())

    if not work:
        parser.print_help()
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
