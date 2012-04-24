AVDClone
========

Clone an Android Virtual Device for easy distribution through the Android SDK Manager.  You can create an AVD preinstalled with the apps and settings you need, and distribute it to others by having them point their Android SDK Manager to your repository.

The packaged AVD and repository are designed to be hosted on the web, but you can just as easily host them locally for development.

Requirements
------------
You will need the following python modules

* beautifulsoup4
* argparse
* zipfile

Usage
-----
1. Create an AVD you want to clone, and change any settings or install any apps you wish to persist
2. Create a config.ini basef on config.ini.template
3. Run `python AVDclone.py -c /path/to/config.ini AVD_NAME`
4. Pointing the Android SDK Manager to the newly created 'addons.xml' file will allow you to install this AVD as a package. (I like to use `python -m SimpleHTTPServer` to host a directory for local development)

Future
------
Some planned features

* Better support for custom system.img (so you can package your AVD with custom certificate chains for SSL proxy support)
* Better support for multiple AVDs in a repository
