"""
Capture package info for currently installed SSS environments.

Currently does platforms = desktop and HPC.

Uses subprocess/ssh to enquire which modules are available on platforms

For each module:
  Use "module" load and "python -c" to get the environment python path.
  Decode python path to a dated environment (tag).
  Get the relevant manifest file from the relevant tag in a git repository.
  Record in a new named file.

"""
import os
import os.path
import shutil
import subprocess
import re
import datetime

datematch_re = re.compile(r'^...._.._')

_debug = False

def grab_envs(platform, output_dirpath, git_dir, ssh_host=None):

    msg = ('\n#\n'
           '# Scanning all environments on platform "{}".\n'
           '# to : {}\n')
    print(msg.format(platform, output_dirpath))

    #shutil.rmtree(output_dirpath, ignore_errors=True)
    if not os.path.exists(output_dirpath):
        os.makedirs(output_dirpath)

    # Go to the git repo directory.
    os.chdir(git_dir)
    # Ensure it is up-to-date : refresh + get all tags.
    cmd = 'git fetch upstream --tags'
    if _debug:
        # Make verbose
        cmd += ' -v'
    text = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    if _debug:
        print('Git update output:\n{}'.format(text))

    # Use "module avail" to get a list of scitools modules on the platform.
    if ssh_host is None:
        cmd = 'module avail 2>&1'
    else:
        cmd = 'ssh {} module avail 2>&1'.format(ssh_host)

    avail_text = subprocess.check_output(
        cmd, stderr=subprocess.STDOUT, shell=True)
    module_names = []
    for line in avail_text.split('\n'):
        module_names += [part for part in line.split() if 'scitools' in part]

    # get rid of trailing "(default)" in some outputs.
    module_names = [name.split('(')[0] for name in module_names]

    for module_name in module_names:
        print('\nMODULE = {}::{}'.format(platform, module_name))

        # Chop off the "scitools/" bit.
        scitools_str, module_inner_name = module_name.split('/')
        assert scitools_str == 'scitools'

        # Execute "module" and "python" to get python install path.
        python_code_string = r'import os; print os.__file__'
        if ssh_host is None:
            cmd = 'module unload scitools; module load {modname}; python -c "{pycode}"'
            cmd = cmd.format(modname=module_name,
                             pycode=python_code_string)
        else:
            cmd = 'ssh {host} "module load {modname}; python -c \\"{pycode}\\""'
            cmd = cmd.format(host=ssh_host,
                             modname=module_name,
                             pycode=python_code_string)
        if _debug:
            print('PATH COMMAND = [{}]'.format(cmd))

        os_path = subprocess.check_output(
            cmd, stderr=subprocess.STDOUT, shell=True)
        # Apparently this can have a closing '\n' ?
        os_path = os_path.strip()

        # Split the path + look for the bit that matches a date.
        env_type_str = None
        for part in os_path.split(os.sep):
            if datematch_re.match(part):
                env_type_str, env_date_str = previous_part, part
                break
            else:
                previous_part = part

        # Skip paths that don't include a date element.
        # NOTE: can be for "old" modules like hpc::scitools/production.
        if env_type_str is None:
            msg = ('NOTE: Unexpected python path for module {} : {}\n'
                   'Skipping ...\n')
            print(msg.format(module_name, os_path))
            continue

        # Construct an output file "xxx.manifest.txt".
        env_name = "{}/{}".format(env_type_str, env_date_str)
        tag_name = "env-{}-{}".format(env_type_str, env_date_str)

        outfile_name = '{}_{}.manifest.txt'.format(platform, module_inner_name)
        outfile_path = os.path.join(output_dirpath, outfile_name)

        header_str = "MODULE {}::{}  -->  ENV-TAG:{}\n"
        header_str = header_str.format(platform, module_name, tag_name)

        print('FILE:{}  HEAD:{}'.format(outfile_name, header_str))

        with open(outfile_path, 'w') as out_file:
            # Write a file header line.
            out_file.write(header_str)

            # Checkout the tag.
            cmd = 'git checkout {}'.format(tag_name)
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)

            # Copy lines from the checked-out manifest to the output file.
            with open('env.manifest') as in_file:
                for line in in_file.readlines():
                    # Chop out the channel path: rest should be package name.
                    channel_str, package_str = line.split('\t')
                    assert channel_str.startswith('http')
                    if package_str[-1] != '\n':
                        # Ensure all have a linefeed (even the last?).
                        package_str += '\n'
                    out_file.write(package_str)

timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
main_dirname = 'manifests_{}'.format(timestamp)
main_dirpath = os.path.join(os.getcwd(), main_dirname)
main_dirpath = os.path.abspath(main_dirpath)

grab_envs(
    platform='hpc',
    output_dirpath=os.path.join(main_dirpath, 'hpc'),
    git_dir='/net/home/h05/itpp/git/sss/crayhpc-environments',
    ssh_host='xcfl00')

grab_envs(
    platform='desktop',
    output_dirpath=os.path.join(main_dirpath, 'desktop'),
    git_dir='/net/home/h05/itpp/git/sss/scidesktop-environments')

