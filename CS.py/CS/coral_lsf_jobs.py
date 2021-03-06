# @brief Submit CORAL jobs to LSF

import os,sys,optparse,shutil,re
from CS.colors import *

def main():

    parser = optparse.OptionParser(version='1.0.6')

    parser.usage = '%prog <CORAL dir> <CORAL exe>  <CORAL opts> <output-dir> <run>\n'\
                   'Author: Alexander.Zvyagin@cern.ch'
    parser.description = 'Submit CORAL jobs to LSF.'
    parser.long_description = 'The output will be written to '\
                         '<output-dir-prefix>/<run>'

    parser.add_option('', '--test',dest='test',default=False,action='store_true',
                      help='Test mode (one job, 8nm queue, 10 events)')

    parser.add_option('', '--submit',dest='submit',default=False,action='store_true',
                      help='Submit jobs at the end!')

    parser.add_option('', '--njobs',dest='njobs',default=9999,
                      help='Maximum number of jobs to submit.')

    parser.add_option('', '--rm',dest='rm',default=False,action='store_true',
                      help='Remove output directory (if they exist)')

    parser.add_option('', '--noterm',dest='noterm',default=False,action='store_true',
                      help='Do not use fancy output (terminal properties).')

    parser.add_option('', '--echo',dest='echo',default=False,action='store_true',
                      help='This option is used for testing.')

    (options, args) = parser.parse_args()

    if len(args)!=5:
        parser.print_help()
        return 1

    coral_dir = os.path.abspath(args[0])
    coral_exe = os.path.abspath(args[1])
    coral_opt = os.path.abspath(args[2])
    run       = int(args[4])
    run_dir   = os.getcwd()+'/'+str(run)
    output    = os.path.abspath(args[3])

    try:
        if options.noterm:
            raise ''
        import term
        terminal = term.TerminalController()
    except:
        terminal = None
        colors_disable()


    # First we check for a 'CORAL' environment variable.
    # If it is not available, we set it and run the script again.
    if not os.environ.get('CORAL'):
        print RED+'CORAL is not initialized. I will do this now.'+RESET

        # We have to do (under bash):
        # 1) start a bash script which will:
        # 3) cd $CORAL
        # 4) . setup.sh
        # 5) Go back to the present directory
        # 6) Run the current script with the same parameters again (now with $CORAL)

        commands = []
        commands.append('cd %s' % coral_dir)
        commands.append('. setup.sh')
        commands.append('cd %s' % os.getcwd())
        
        if os.path.splitext(sys.argv[0])[1]:
            run_me = 'python'
        else:
            run_me = 'cs'
        commands.append('%s %s' % (run_me,' '.join(sys.argv)))
        commands.append('exit')
        
        bash_run = 'bash -c "%s"' % ' && '.join(commands)
        print '*** Executing the command:'
        print BOLD+BLUE+bash_run+RESET

        return os.system(bash_run)
    else:
        print BOLD,RED,YELLOWBG,'CORAL path is: ',os.environ.get('CORAL'),RESET

    if os.path.abspath(os.environ.get('CORAL'))!=os.path.abspath(coral_dir):
        print 'Your CORAL variable is not the same as in the command line!'
        print '  ENV: ',os.path.abspath(os.environ.get('CORAL'))
        print '  CMD: ',os.path.abspath(coral_dir)
        return 1

    print 'Checking the CORAL executable...'
    sys.stdout.flush()
    if os.system('%s 2>&1 | grep "usage:" > /dev/null' % coral_exe):
        print 'Problem in running the CORAL!'
        os.system(coral_exe)
        return 1

    print GREEN,'Creating output directories...',RESET

    if options.rm:
        print RED,BOLD
        os.system('rm -r %s > /dev/null 2>&1' % run_dir)
        os.system('rfrm -r %s' % output)
        print RESET

    # Create directory for temporary files
    os.mkdir(run_dir)
    os.chdir(run_dir)

    # Main output directory...
    if os.system('rfmkdir %s' % output):
        print 'Failed to create the output directory: %s' % output
        return 1
    os.system('rfcp %s %s/coral.opt' % (coral_opt,output))

    shutil.copyfile(coral_opt,'coral.opt')
    if os.system('grep \?\?\?DATA\?\?\? coral.opt > /dev/null'):
        print 'Bad options file (no data tag ???DATA??? is found).'
        return 1

    print 'Getting run data files and generating the CORAL options files...'
    sys.stdout.flush()
    if options.test:
        events = '--events=10'
    else:
        events = '' # Use default number
    if os.system('cs coral --output=%s --run=%d --opt=coral.opt %s > coral_opts.log ' % (output,run,events) ):
        return 1
    chunks = int(os.popen('wc coral_opts.log').readline().split()[0])
    print 'Run %d has %d chunk(s).' % (run,chunks)
    
    if options.test:
        queue = '8nm'
        extra = '--jobs-max=1'
    else:
        queue = '1nd'
        extra = ''
        #extra = '--jobs-max=%d' % options.njobs

    if os.system('cs lsf --queue=%s --coral-setup=%s --coral=%s --output=%s %s cdr*.opt' %  \
                    (queue,coral_dir,coral_exe,output,extra)):
        print RED,BOLD,'Failed to create the jobs list! Why?',RESET
        return 1
    
    if options.submit:
        n_jobs = 0
        if options.njobs<chunks:
            chunks=options.njobs
        if terminal:
            progress = term.ProgressBar(terminal, 'Submitting %d LSF jobs for run %d' % (chunks,run))
        for l in file('jobs.sh').readlines():
            if n_jobs>=chunks:
                break

            job = l.strip()
            r = re.match('.*cdr(?P<cdr>\d+).*',job)
            if not r:
                name = 'Unknwon'
            else:
                name = r.group('cdr')
            if terminal:
                progress.update(float(n_jobs)/chunks, 'Chunk %s' % name)
            n_jobs += 1
            if os.system('%s%s > /dev/null' % (('','echo ')[options.echo],job)):
                print RED,BOLD,'Something went wrong in the job submitting!',RESET
                break
        if terminal:
            progress.update(float(n_jobs)/chunks, 'FINISHED')
        print 'It were submitted %d job(s) out of %d chunk(s).' % (n_jobs,chunks)
    else:
        print 'File "%s" is ready for an execution.' % os.path.abspath('jobs.sh')
    
    return 0

if __name__=='__main__':
    sys.exit(main())
