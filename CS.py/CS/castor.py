from __future__ import generators
import string,re,os,sys

def path_stat(path):
    stat={}
    for l in os.popen('rfstat %s 2>&1' % path).readlines():
        r = re.match('Protection\s+:\s+(?P<protection>[\w-]+)\s+.*',l)
        if r:
            return r.group('protection')[0]
    return None

def copy(src,dst,move=False):
    print 'copy: %s %s' % (src,dst)
    if path_stat(src)=='-':
        res = os.system('rfcp %s %s' % (src,dst) )
        if res==0 and move:
            os.system('rfrm %s' % src)

    elif path_stat(src)=='d':
        if path_stat(dst)=='-':
            raise "copy: I don't want to copy directory to a file %s" % dst
        elif path_stat(dst)==None:
            res = os.system('rfmkdir %s' % dst)
            if res:
                # Error!
                return res

        for f in castor_files(src):
            name = os.path.split(f)[1]
            if name in ['.','..']:
                continue
            res = copy(f,dst+'/'+name,move)
            if res:
                return res

        if move:
            os.system('rfrm -r %s' % src)

        return 0

##  Get list of files with given pattern (regular expression)
def castor_files(directory,pattern=None):
    if os.system('rfstat %s > /dev/null 2>&1' % directory):
        return
    for f in os.popen('rfdir ' + directory):
        name=f.strip().split()[-1]
        if pattern:
            r = re.match(pattern,name)
            if not r:  continue
        yield os.path.join(directory,name)

##  Dictionary with the CDR file attributes
#
def file_cdr(d,f):
    q = {}

    if d=='':
        q['name']   = f
        q['fname']  = f
    else:
        if d[-1]!='/':
            d += '/'
        q['name']  = string.strip(f.split(' ')[-1])
        q['fname']  = d+q['name']
    res = re.match(r'.*cdr(?P<cdr>\d\d)\d+-(?P<run>\d+).*',q['name'])
    q['run']    = int(res.group('run'))
    q['pccoeb'] = int(res.group('cdr'))
    q['feor']   = None!=re.match('.*00\-\d+.*',q['name'])

    # Now get the file size
    size = os.popen('rfstat %s | grep Size' % q['fname']).readlines()[0]
    size = size.split()[-1]
    try:
        q['size'] = int(size)
    except:
        q['size'] = 0
    
    return q

def rfdir_cdr_files(directory,printout=0):

    if os.system('rfstat %s > /dev/null 2>&1' % directory):
        return

    for p in os.popen('rfdir ' + directory):
        if printout>2:
            print directory,p
        try:
            yield file_cdr(directory,p)
        except KeyboardInterrupt:
            raise
        except:
            if printout>1:
                print sys.exc_value

## Generator of CDR files in 2002 castor directory
def cdr_files_2002(printout=0):
    dirs='/castor/cern.ch/compass/data/2002/raw_migration/'

    for i in range(1,4):
        for c in 'ABCDEFGHI':
            period='P%d%c' % (i,c)

            for j in range (0,9):
                d = dirs+period+('/%d0/' % j)
                #print 'The database has %d runs' % len(self.__run_db)
                if printout>0:
                    print 'Scanning directory',d
                for f in rfdir_cdr_files(d,printout):
                    f['year']=2002
                    f['period']=period
                    yield f

## Generator of CDR files in 2003 castor directory
def cdr_files_2003(printout=0):
    dirs='/castor/cern.ch/compass/data/2003/raw/'
    for i in range(1,4):
        for c in 'ABCDEFGHI':
            period='P%d%c' % (i,c)

            d = dirs+period
            if printout>0:
                print 'Scanning directory',d
            for f in rfdir_cdr_files(d,printout):
                f['year']=2003
                f['period']=period
                yield f

# Generator of CDR files in 2004 castor directory
def cdr_files_2004(printout=0):
    dirs='/castor/cern.ch/compass/data/2004/raw/'
    lst=[]
    for i in range(0,55):
        lst.append('T%2.2d'%i)
    for i in range(21,55):
        lst.append('W%2.2d'%i)

    for period in lst:
        d = dirs+period
        if printout>0:
            print 'Scanning directory',d
        for f in rfdir_cdr_files(d,printout):
            f['year']=2004
            f['period']=period
            yield f

# Generator of CDR files in 2006 castor directory
def cdr_files_2006(printout=0):
    dirs='/castor/cern.ch/compass/data/2006/raw/'
    lst=[]
    for i in range(0,55):
        lst.append('T%2.2d'%i)
        lst.append('W%2.2d'%i)
    lst.append('test')

    # This allows to add new files first.
    lst.reverse()

    for period in lst:
        d = dirs+period
        if printout>0:
            print 'Scanning directory',d
        for f in rfdir_cdr_files(d,printout):
            f['year']=2006
            f['period']=period
            yield f

# Generator of CDR files from castor
def cdr_files(years=[],printout=0):
    if not years:
        # Set default value
        years=(2002,2003,2004,2006,2007,2008,2009,2010)
    if 2002 in years:
        for f in cdr_files_2002():
            yield f
    if 2003 in years:
        for f in cdr_files_2003():
            yield f
    if 2004 in years:
        for f in cdr_files_2004():
            yield f
    if 2006 in years:
        for f in cdr_files_2006():
            yield f

########################################################################
### The self test
########################################################################

import unittest

class TestCase(unittest.TestCase):
    #def setUp(self):
        #self.top = SE(0,1)
    #    pass

    def test_rfdir(self):
        res = os.system('rfdir /castor/cern.ch/compass/data/2002 > /dev/null')
        self.failUnless(res==0, 'rfdir failed!')

def TheTestSuite():
    return unittest.makeSuite(TestCase,'test')

########################################################################
### The main program
########################################################################

def main():

    import optparse

    commands = ['ls','cp','mv']

    parser = optparse.OptionParser(version='1.1.0')
    parser.description = 'CASTOR file system utilities'
    parser.usage = 'cs %prog <command> [options]\n' \
                   '  Type "%prog <command>" for more help.\n' \
                   '  List of available commands: ' + ','.join(commands)+'\n'\
                   'Author: Alexander.Zvyagin@cern.ch'

    parser.add_option('', '--pattern',dest='pattern',default=None,
                      help='Pattern (regular expression) for files.', type='string', metavar='reg-expr')

    parser.add_option('', '--sep',dest='sep',default='EndOfLine',
                      help='Files separation symbol', type='string', metavar='symbol')

    #parser.add_option('', '--test',dest='test',default=False,action='store_true',
    #                  help='Run a test suit', type='string')
    
    (options, args) = parser.parse_args()

    #if options.test:
    #    print 'Running the test suit'
    #    return unittest.main()

    if not args:
        parser.print_help()
        return 1

    if options.sep=='EndOfLine':
        options.sep = '\n'

    if args[0]=='ls':
        del args[0]
        if len(args)==0:
            print 'Usage: castor ls [options] <dir> [<dir> ....]'
            return 1
        files=[]
        for d in args:
            for f in castor_files(d,options.pattern):
                files.append(f)
        print options.sep.join(files)
        return 0

    if args[0] in ['cp','mv']:
        move = args[0]=='mv'
        del args[0]
        if len(args)!=2:
            print 'Usage: castor cp <src> <dst>'
            print 'Usage: castor mv <src> <dst>'
            return 1
        copy(args[0],args[1],move)
        return 0

    print 'Unknwon command: %s' % args[0]
    print 'Possible commands are: %s' % ','.join(commands)
    return 1

if __name__ == '__main__':
    sys.exit(main())
