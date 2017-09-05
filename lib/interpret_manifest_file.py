import re

#
# Old version "find+report", from notebook/envs_display_flex.ipynb
#
def env_version(manifest_path, key_name):
    result = 'n/a'
    with open(manifest_path) as file_in:
        for line in file_in.readlines():
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            if key_name in line.lower():
                result = line[len(key_name) + 1:]
                break
    return result.strip().split('-')[0]




def decode_manifest_file(filepath, newstyle=True, output_module_lines=None):
    """
    Interpret manifest as a sequence of (package-name, version, build-string).

    E.G. lines
        agg-regrid-0.1.0-py27_0.json
        alabaster-0.7.9-py27_0.json

    Rules used are:
        * strip first
        * package is a sequence of '[a-Z][a-Z0-9]*', with '-' separating.
        * version is "[0-9.]*".
        * build-string is whatever comes after the version
            * EXCEPT removing final ".json" (if newstyle==True)

    Args:

    * filepath (string):
        file to load from
    * newstyle (bool):
        newstyle=True simply enables stripping ".json" from end of each line.
    * module_lines (list):
        if provided, any lines beginning 'MODULE' are appended to this.
        This is a temporary hack for header-line extraction.

    """
    ignore_end_string = ".json"
    ignore_end_length = len(ignore_end_string)
    with open(filepath) as file_in:
        for line in file_in.readlines():
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            if line.startswith('MODULE'):
                # NOTE: aim to chunk this one, use '#' instead...
                if output_module_lines is not None:
                    output_module_lines.append(line)
                    continue
            if newstyle:
                if line.endswith(ignore_end_string):
                    line = line[:-ignore_end_length]
            bits = line.split('-')
            if len(bits) < 2:
                print '   ??? : ', bits
                continue
            bits = [bit for bit in bits if len(bit) > 0]
            version_start_indices = [i for i in range(len(bits))
                                     if bits[i][0].isdigit()]
            if len(version_start_indices) < 1:
                print '   ??? : ', bits
                continue
            version_start_index = version_start_indices[0]
            package_name = '-'.join(bits[:version_start_index])
            version_string = bits[version_start_index]
            build_string = '-'.join(bits[version_start_index+1:])
            yield (package_name, version_string, build_string)


class EnvManifest(object):
    """
    Environment information from a manifest file.

    Properties:

    * platform (string):
        name platform on which env exists, e.g. "hpc"
    * env_name (string):
        defining name of the env, in the form "<platform>:<env-name>"
        E.G. "desktop:default-current", or "hpc:production-os40"
    * fixed_tagname (string):
        fixed-tag pathname of the env, in the form "<category>/<env_date>"
        E.G. "default/2017_06_28"
    * packages (dict):
        packages, entries in the form "package: (version, build_string)",
        E.G. env_manifest['numpy'] --> ('1.11.1', 'py27_201')

    """
    def __init__(self, filepath, newstyle=True):
        # Filepath is of the form .../<category>/<env_date>/<manifest_name>.
        # the fixed-tag filepath
        module_lines = []
        package_results = decode_manifest_file(
            filepath, newstyle=newstyle, output_module_lines=module_lines)
        # Put package info into a dictionary.
        self.packages = {package: (version, build_string)
                         for package, version, build_string in package_results}
        # Decode the 'MODULE' line (if any) into a fixed-reference string.
        self.platform = ""
        self.module_name = ""
        self.fixed_tagname = ""
        if len(module_lines) > 0:
            module_line, = module_lines  # we only expect ONE !
            regexp = (
                r'MODULE (?P<platform>[^:]*)::scitools/(?P<modname>[^ ]*)'
                r'  -->  ENV-TAG:env-'
                r'(?P<fixcat>[^-]*)-(?P<fixdate>.*)')
            match = re.match(regexp, module_line)
            if match:
                self.platform = match.group('platform')
                self.module_name = match.group('modname')
                self.fixed_tagname = '{}/{}'.format(
                    match.group('fixcat'), match.group('fixdate'))


if __name__ == '__main__':
    import os
    import os.path

    own_dirpath = os.path.dirname(os.path.abspath(__file__))
    envs_dirpath = os.path.abspath(os.sep.join(
        [own_dirpath, '..', 'datastore', 'env_info']))
    oldstyle_filepath = os.path.abspath(os.sep.join(
        [envs_dirpath, 'samples', 'manifests_2017-08-03_16:41:15',
         'desktop', 'desktop_default-current.manifest.txt']))
    newstyle_filepath = os.path.abspath(os.sep.join(
        [envs_dirpath, 'newstyle_manifests',
        'desktop_default-current.manifest.txt']))
    legacy_filepath = os.path.abspath(os.sep.join(
        [envs_dirpath, 'legacy_reference', 'old-scitools-manifest.txt']))

    tst_em = EnvManifest(legacy_filepath)
    print 'Test: env.platform = ', tst_em.platform
    print 'Test: env.module_name = ', tst_em.module_name
    print 'Test: env.fixed_tagname = ', tst_em.fixed_tagname
    print "Test: env.packages['numpy'] = ", tst_em.packages['numpy']
    exit(0)

    files_dicts = {}
    for filepath in (oldstyle_filepath, newstyle_filepath):
        print
        print 'FILE: ', filepath
        file_dict = {data[0]:data[1:]
                     for data in decode_manifest_file(filepath)}
        files_dicts[filepath] = file_dict
        print '\n'.join(str(item) for item in file_dict.items())

    print
    print 'SAME? : ', files_dicts.values()[0] == files_dicts.values()[1]

    filepath = legacy_filepath
    print
    print 'LEGACY FILE: ', filepath
    for data in decode_manifest_file(filepath):
        print data
#    file_dict = {data[0]:data[1:]
#                     for data in decode_manifest_file(filepath)}
#    print '\n'.join(str(item) for item in file_dict.items())
