
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




def decode_manifest_file(filepath, newstyle=True):
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

    newstyle=True simply enables stripping ".json" from end of each line.

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
    Details relating to an SSS environment manifest file.

    """


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

    legacy_filepath = os.path.abspath(os.sep.join(
        [envs_dirpath, 'legacy_reference', 'old-scitools-manifest.txt']))
    filepath = legacy_filepath
    print
    print 'LEGACY FILE: ', filepath
    for data in decode_manifest_file(filepath):
        print data
#    file_dict = {data[0]:data[1:]
#                     for data in decode_manifest_file(filepath)}
#    print '\n'.join(str(item) for item in file_dict.items())
