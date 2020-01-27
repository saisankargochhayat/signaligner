import argparse, datetime, os, shutil, subprocess, sys, zipfile



def writeversions():
    anywarnings = False

    with open('version.txt', 'wt') as outfile:
        starting_folder = os.getcwd()

        for folder, name in [('.', 'signaligner'), ('../mdcas-python', 'mdcas-python')]:
            os.chdir(folder)

            try:
                gitrev = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8').strip()
                if gitrev != '':
                    modified = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no']).decode('utf-8').strip()
                    if modified != '':
                        gitrev = gitrev + '+'
            except:
                print('WARNING: could not run git, version information for %s will not be included.' % name)
                anywarnings = True
                gitrev = 'NONE'

            os.chdir(starting_folder)

            outfile.write('%s %s\n' % (name, gitrev))

    if anywarnings:
        input('press enter to continue.')



def main(tag=''):
    if sys.platform.startswith('win') or sys.platform.startswith('cygwin'):
        platform = 'windows'
        pathsep = ';'
    elif sys.platform.startswith('darwin'):
        platform = 'macos'
        pathsep = ':'
    elif sys.platform.startswith('linux'):
        platform = 'linux'
        pathsep = ':'
    else:
        raise RuntimeError('Unknown platform')

    workpath = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
    os.chdir(workpath)

    platpath = os.path.join('pyinst', platform)
    workpath = os.path.join(platpath, 'build')
    distpath = os.path.join(platpath, 'dist')
    releasename = 'signalauncher-%s-%s%s' % (platform, datetime.datetime.now().strftime('%Y%m%d'), tag)

    import dask
    daskpath=dask.__path__[0]

    shutil.rmtree(platpath, ignore_errors=True)

    writeversions()

    cmd = []
    cmd += ['pyinstaller', '../scripts/signalauncher.py']
    cmd += ['--workpath=' + workpath]
    cmd += ['--distpath=' + distpath]
    cmd += ['--paths=../scripts']
    cmd += ['--paths=../mdcas-python']
    cmd += ['--add-data=../signaligner/' + pathsep + 'signaligner/signaligner']
    cmd += ['--add-data=../static/' + pathsep + 'signaligner/static']
    cmd += ['--add-data=../common/' + pathsep + 'signaligner/common']
    cmd += ['--add-data=../mdcas-python/DW.MO.mdcas_model.pkl' + pathsep + 'signaligner/mdcas-python']
    cmd += ['--add-data=../mdcas-python/SWaN_pack/model/' + pathsep + 'signaligner/mdcas-python/SWaN_pack/model']
    cmd += ['--add-data=version.txt' + pathsep + 'signaligner']
    cmd += ['--hidden-import=dask']
    cmd += ['--add-data=' + daskpath + '/dask.yaml' + pathsep + 'dask']
    cmd += ['--hidden-import=sklearn.utils._cython_blas']
    cmd += ['--hidden-import=sklearn.calibration']

    if platform == 'macos':
        cmd += ['--add-binary=/System/Library/Frameworks/Tk.framework/Tk' + pathsep + 'tk']
        cmd += ['--add-binary=/System/Library/Frameworks/Tcl.framework/Tcl' + pathsep + 'tcl']

    subprocess.call(cmd)

    shutil.move(os.path.join(distpath, 'signalauncher.py'), os.path.join(distpath, releasename))
    shutil.make_archive(os.path.join(platpath, releasename), 'zip', distpath, releasename)
    # if platform == 'macos' or platform == 'linux':
    launcher_file = open(os.path.join(distpath, "signalauncher"), 'w')
    signalauncher_autogenerated_filepath = os.path.join(distpath, releasename, "signalauncher")
    signalauncher_command = [
        "#!/usr/bin/env python\n",
        "import subprocess, os\n",
        "dir_path = os.path.dirname(os.path.realpath(__file__))\n"
        "subprocess.call([dir_path + \"%s\"])\n" % signalauncher_autogenerated_filepath[17:]
    ]
    launcher_file.writelines(signalauncher_command)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    path = signalauncher_autogenerated_filepath[0:18] + "signalauncher"
    cmd = "chmod +x " + dir_path + "/pyinst/macos/dist/signalauncher"
    os.system(cmd)
    # elif platform == 'windows':
    #     # make executable on windows
    #     pass



if __name__ == '__main__':
    main()
