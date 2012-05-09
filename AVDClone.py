from bs4 import BeautifulSoup
from argparse import ArgumentParser
from os import path
from zipfile import ZipFile, ZIP_DEFLATED
import hashlib
import sys

TEMPLATE_FILE = path.join(path.realpath(__file__), 'templates', 'addon.xml')
AVD_PATH = path.expanduser('~/.android/avd')
if sys.platform == 'macosx':
    SDK_PATH = path.expanduser('~/android-sdk-macosx')
elif sys.platform == 'win32':
    SDK_PATH = path.abspath('C:\android-sdk-windows')
else: #we're going to assume that anything else is linux 
    SDK_PATH= path.expanduser('~/android-sdk-linux')

        
class ConfigFile(dict):
    '''
    Parses configuration files.  Initialize class with a file object
    '''
    def __init__(self, file_handle):
        for line in file_handle:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            key, value = line.split('=')
            self[key] = value
            
    def write(self, file_handle):
        '''
        write contents of ConfigFile to file_handle
        '''
        for k in self.keys():
            file_handle.write(k + '=' + self[k])

if __name__ == '__main__':
    parser = ArgumentParser(description='Create an installable AVD package from an existing AVD')
    parser.add_argument('base_avd', metavar='AVD', nargs=1, help='AVD to base package off of')
    parser.add_argument('-c', '--config', metavar='FILE', action='store', type=str, required=True, dest='config_file', help='configuration file')
    parser.add_argument('-o', '--output', metavar='PATH', action='store', type=str, dest='output_path', default='.', help="generate output in PATH (default is '.'")
    parser.add_argument('-s', '--system', metavar='PATH', action='store', type=str, dest='system', default=False, help="path to a custom system.img file")
    parser.add_argument('--avd_path',  metavar='PATH', action='store', type=str, default=AVD_PATH, dest='avd_path',
                        help="android avd path (default is '~/.android/avd')")
    parser.add_argument('--sdk_path', metavar='PATH', action='store', type=str, default=SDK_PATH, dest='sdk_path',
                        help="android sdk path (default is '~/android-sdk-linux')")

    args = parser.parse_args()
    
    base_avd = args.base_avd[0]
    avd_path = args.avd_path
    sdk_path = path.expanduser(args.sdk_path)
    
    print ' [+] Building a package from AVD: ' + base_avd  
    #load config file
    cf = ConfigFile(open(args.config_file))
    
    #create zip
    filename = path.join(args.output_path, cf['vendor'] + '_' + cf['name'] + '_' + cf['revision'] + '.zip')
    zf = ZipFile(filename, 'w', ZIP_DEFLATED)
    
    #add config file as manifest to zip
    print ' [+] Writing manifest'
    zf.write(args.config_file, path.join(filename, 'manifest.ini'))

    #load image paths
    base_avd_conf = ConfigFile(open(path.join(avd_path, base_avd + '.avd', 'config.ini')))
    user_image_path = path.join(avd_path, base_avd + '.avd')
    sdk_image_paths = [path.join(sdk_path, base_avd_conf[k]) for k in sorted(base_avd_conf.keys()) if k.startswith('image.sysdir') if path.exists(path.join(sdk_path, base_avd_conf[k]))]

    #add image files to zf
    print ' [+] Writing userdata.img'
    if path.exists(path.join(user_image_path ,'user-data_qemu.img')):
        zf.write(path.join(user_image_path, 'userdata-qemu.img'), path.join(filename, 'images/userdata.img'))
    else:
        zf.write(path.join(user_image_path, 'userdata-qemu.img'), path.join(filename, 'images/userdata-qemu.img'))
    print ' [+] Writing system.img'
    if args.system:
        zf.write(path.join(sdk_image_paths[0], 'system.img'), path.join(filename, args.system))
    else:
        zf.write(path.join(sdk_image_paths[0], 'system.img'), path.join(filename, 'images/system.img'))
    print ' [+] Writing ramdisk.img'
    zf.write(path.join(sdk_image_paths[0], 'ramdisk.img'), path.join(filename, 'images/ramdisk.img'))

    print ' [+] Deflating zip'
    zf.close()

    #compute checksum of zip file
    print ' [+] Computing checksum'
    sha1 = hashlib.sha1()
    with open(filename, 'rb') as f: 
        for chunk in iter(lambda: f.read(8192), b''): 
            sha1.update(chunk)
    
    #create addons.xml
    print ' [+] Writing repository information'
    soup = BeautifulSoup(open(TEMPLATE_FILE))
    name = soup.find('sdk:name')
    name.string = cf['name']
    level = soup.find('sdk:api-level')
    level.string = cf['api']
    vendor = soup.find('sdk:vendor')
    vendor.string = cf['vendor']
    revision = soup.find('sdk:revision')
    revision.string = cf['revision']
    desc = soup.find('sdk:description')
    desc.string = cf['description']

    size = soup.find('sdk:size')
    size.string = str(path.getsize(filename))
    checksum = soup.find('sdk:checksum')
    checksum.string = sha1.hexdigest()
    url = soup.find('sdk:url')
    url.string = filename
    
    f = open(path.join(args.output_path, 'addon.xml'),'w')
    f.write(str(soup))



